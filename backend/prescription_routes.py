from flask import Blueprint, request, jsonify, send_file
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import gridfs
import io
import secrets
import hashlib
from ocr_processor import process_prescription_file

# Create Blueprint
prescription_bp = Blueprint('prescription', __name__)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["mediquery_nlp"]
fs = gridfs.GridFS(mongo_db)  # GridFS for file storage

# ============================================
# UPLOAD PRESCRIPTION WITH OCR
# ============================================
@prescription_bp.route("/upload-prescription", methods=["POST"])
def upload_prescription():
    """
    Upload prescription file (PDF/Image)
    Perform OCR and store structured data
    """
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    patient_id = request.form.get('patient_id')
    
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Read file bytes
        file_bytes = file.read()
        
        # Store original file in GridFS
        file_id = fs.put(
            file_bytes,
            filename=file.filename,
            content_type=file.content_type,
            upload_date=datetime.now()
        )
        
        # Perform OCR and extract data
        print(f"🔍 Processing OCR for {file.filename}...")
        parsed_data = process_prescription_file(file_bytes, file.filename)
        
        if "error" in parsed_data:
            return jsonify({"error": parsed_data["error"]}), 500
        
        # Store prescription record in MongoDB
        prescription_record = {
            "patient_id": int(patient_id),
            "file_id": str(file_id),
            "filename": file.filename,
            "upload_date": datetime.now(),
            "ocr_data": parsed_data,
            "type": "prescription"  # To distinguish from bookings
        }
        
        result = mongo_db["patient_prescriptions"].insert_one(prescription_record)
        
        return jsonify({
            "success": True,
            "message": "Prescription uploaded and processed successfully",
            "prescription_id": str(result.inserted_id),
            "extracted_data": parsed_data
        })
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================
# GET PATIENT'S PRESCRIPTIONS
# ============================================
@prescription_bp.route("/prescriptions/<int:patient_id>", methods=["GET"])
def get_prescriptions(patient_id):
    """Get all prescriptions for a patient"""
    
    prescriptions = list(mongo_db["patient_prescriptions"].find(
        {"patient_id": patient_id},
        {"_id": 1, "filename": 1, "upload_date": 1, "ocr_data": 1}
    ).sort("upload_date", -1))
    
    # Convert ObjectId to string
    for presc in prescriptions:
        presc["prescription_id"] = str(presc.pop("_id"))
    
    return jsonify({"prescriptions": prescriptions})

# ============================================
# GET MEDICAL HISTORY TIMELINE
# ============================================
@prescription_bp.route("/medical-timeline/<int:patient_id>", methods=["GET"])
def get_medical_timeline(patient_id):
    """
    Combine prescriptions + appointments into chronological timeline
    """
    
    # Get prescriptions
    prescriptions = list(mongo_db["patient_prescriptions"].find(
        {"patient_id": patient_id},
        {"_id": 1, "filename": 1, "upload_date": 1, "ocr_data": 1}
    ))
    
    # Get appointments (bookings)
    appointments = list(mongo_db["user_search_history"].find(
        {"patient_id": patient_id, "type": "booking"},
        {"_id": 1, "doctor_name": 1, "hospital_name": 1, 
         "appointment_date": 1, "appointment_time": 1, 
         "specialization": 1, "booking_timestamp": 1, "status": 1}
    ))
    
    # Create unified timeline
    timeline = []
    
    # Add prescriptions
    for presc in prescriptions:
        timeline.append({
            "type": "prescription",
            "id": str(presc["_id"]),
            "date": presc["upload_date"],
            "title": f"Prescription uploaded: {presc['filename']}",
            "doctor": presc["ocr_data"].get("doctor_name", "Unknown"),
            "hospital": presc["ocr_data"].get("hospital", "N/A"),
            "medicines_count": len(presc["ocr_data"].get("medicines", []))
        })
    
    # Add appointments
    for apt in appointments:
        timeline.append({
            "type": "appointment",
            "id": str(apt["_id"]),
            "date": apt["booking_timestamp"],
            "title": f"Appointment with Dr. {apt['doctor_name']}",
            "doctor": apt["doctor_name"],
            "hospital": apt["hospital_name"],
            "specialization": apt["specialization"],
            "status": apt.get("status", "confirmed")
        })
    
    # Sort by date (most recent first)
    timeline.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify({"timeline": timeline})

# ============================================
# DOWNLOAD PRESCRIPTION FILE
# ============================================
@prescription_bp.route("/download-prescription/<prescription_id>", methods=["GET"])
def download_prescription(prescription_id):
    """Download original prescription file"""
    
    try:
        # Get prescription record
        presc = mongo_db["patient_prescriptions"].find_one({"_id": ObjectId(prescription_id)})
        
        if not presc:
            return jsonify({"error": "Prescription not found"}), 404
        
        # Get file from GridFS
        file_data = fs.get(ObjectId(presc["file_id"]))
        
        return send_file(
            io.BytesIO(file_data.read()),
            mimetype=file_data.content_type,
            as_attachment=True,
            download_name=presc["filename"]
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# SEARCH MEDICINES IN PRESCRIPTIONS
# ============================================
@prescription_bp.route("/search-medicine/<int:patient_id>", methods=["POST"])
def search_medicine(patient_id):
    """Search for specific medicine in patient's prescription history"""
    
    data = request.get_json()
    medicine_name = data.get("medicine_name", "").lower()
    
    if not medicine_name:
        return jsonify({"error": "Medicine name required"}), 400
    
    # Search in prescriptions
    prescriptions = list(mongo_db["patient_prescriptions"].find(
        {"patient_id": patient_id}
    ))
    
    results = []
    
    for presc in prescriptions:
        medicines = presc["ocr_data"].get("medicines", [])
        
        for med in medicines:
            if medicine_name in med.get("name", "").lower():
                results.append({
                    "prescription_id": str(presc["_id"]),
                    "date": presc["upload_date"].strftime("%Y-%m-%d"),
                    "doctor": presc["ocr_data"].get("doctor_name", "Unknown"),
                    "medicine": med
                })
    
    return jsonify({"results": results, "count": len(results)})

# ============================================
# GENERATE SHAREABLE LINK
# ============================================
@prescription_bp.route("/generate-share-link/<int:patient_id>", methods=["POST"])
def generate_share_link(patient_id):
    """
    Generate secure, time-limited link to share medical records
    """
    
    data = request.get_json()
    expiry_hours = data.get("expiry_hours", 24)  # Default 24 hours
    password = data.get("password", None)
    
    # Generate unique token
    token = secrets.token_urlsafe(32)
    
    # Hash password if provided
    password_hash = None
    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Store share record
    share_record = {
        "patient_id": patient_id,
        "token": token,
        "password_hash": password_hash,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=expiry_hours),
        "access_count": 0,
        "is_active": True
    }
    
    mongo_db["shared_records"].insert_one(share_record)
    
    # Generate shareable URL
    share_url = f"http://localhost:5000/view-shared/{token}"
    
    return jsonify({
        "success": True,
        "share_url": share_url,
        "expires_at": share_record["expires_at"].isoformat(),
        "requires_password": password is not None
    })

# ============================================
# VIEW SHARED RECORDS (PUBLIC ACCESS)
# ============================================
@prescription_bp.route("/view-shared/<token>", methods=["POST"])
def view_shared_records(token):
    """View shared medical records with token"""
    
    data = request.get_json()
    password = data.get("password", None)
    
    # Find share record
    share = mongo_db["shared_records"].find_one({
        "token": token,
        "is_active": True
    })
    
    if not share:
        return jsonify({"error": "Invalid or expired link"}), 404
    
    # Check expiry
    if datetime.now() > share["expires_at"]:
        return jsonify({"error": "Link has expired"}), 403
    
    # Check password if required
    if share["password_hash"]:
        if not password:
            return jsonify({"error": "Password required"}), 401
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != share["password_hash"]:
            return jsonify({"error": "Incorrect password"}), 401
    
    # Increment access count
    mongo_db["shared_records"].update_one(
        {"_id": share["_id"]},
        {"$inc": {"access_count": 1}}
    )
    
    # Get patient's medical records
    patient_id = share["patient_id"]
    
    prescriptions = list(mongo_db["patient_prescriptions"].find(
        {"patient_id": patient_id}
    ).sort("upload_date", -1))
    
    for presc in prescriptions:
        presc["_id"] = str(presc["_id"])
        presc["file_id"] = str(presc["file_id"])
    
    return jsonify({
        "success": True,
        "patient_id": patient_id,
        "prescriptions": prescriptions,
        "access_expires_at": share["expires_at"].isoformat()
    })


# modification : 
# ============================================
# SHARE PRESCRIPTION WITH DOCTOR (INTERNAL)
# ============================================
@prescription_bp.route("/share-with-doctor", methods=["POST"])
def share_with_doctor():
    """
    Share prescription directly with a doctor through the platform
    """
    data = request.get_json()
    patient_id = data.get("patient_id")
    prescription_id = data.get("prescription_id")
    doctor_id = data.get("doctor_id")
    message = data.get("message", "")
    
    if not all([patient_id, prescription_id, doctor_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Verify prescription exists and belongs to patient
        prescription = mongo_db["patient_prescriptions"].find_one({
            "_id": ObjectId(prescription_id),
            "patient_id": patient_id
        })
        
        if not prescription:
            return jsonify({"error": "Prescription not found"}), 404
        
        # Check if already shared with this doctor
        existing_share = mongo_db["prescription_shares"].find_one({
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "prescription_id": prescription_id
        })
        
        if existing_share:
            return jsonify({"error": "Already shared with this doctor"}), 400
        
        # Create share record
        share_record = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "prescription_id": prescription_id,
            "status": "pending",
            "shared_at": datetime.now(),
            "message": message,
            "viewed_at": None
        }
        
        result = mongo_db["prescription_shares"].insert_one(share_record)
        
        return jsonify({
            "success": True,
            "message": "Prescription shared with doctor successfully",
            "share_id": str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"❌ Share error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================
# GET DOCTOR'S SHARED PRESCRIPTIONS
# ============================================
@prescription_bp.route("/doctor/shared-prescriptions/<int:doctor_id>", methods=["GET"])
def get_doctor_shared_prescriptions(doctor_id):
    """
    Get all prescriptions shared with a specific doctor
    """
    try:
        # Get all shares for this doctor
        shares = list(mongo_db["prescription_shares"].find(
            {"doctor_id": doctor_id}
        ).sort("shared_at", -1))
        
        result = []
        
        for share in shares:
            # Get prescription details
            prescription = mongo_db["patient_prescriptions"].find_one({
                "_id": ObjectId(share["prescription_id"])
            })
            
            if prescription:
                result.append({
                    "share_id": str(share["_id"]),
                    "patient_id": share["patient_id"],
                    "prescription_id": str(prescription["_id"]),
                    "filename": prescription["filename"],
                    "upload_date": prescription["upload_date"],
                    "ocr_data": prescription["ocr_data"],
                    "shared_at": share["shared_at"],
                    "status": share["status"],
                    "message": share.get("message", ""),
                    "viewed_at": share.get("viewed_at")
                })
        
        return jsonify({"shared_prescriptions": result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# MARK PRESCRIPTION AS VIEWED BY DOCTOR
# ============================================
@prescription_bp.route("/doctor/mark-viewed/<share_id>", methods=["POST"])
def mark_prescription_viewed(share_id):
    """
    Doctor marks prescription as viewed
    """
    try:
        result = mongo_db["prescription_shares"].update_one(
            {"_id": ObjectId(share_id)},
            {
                "$set": {
                    "status": "viewed",
                    "viewed_at": datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({"success": True, "message": "Marked as viewed"})
        else:
            return jsonify({"error": "Share not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500