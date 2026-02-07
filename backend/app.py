from flask import Flask, request, jsonify
from flask_cors import CORS
from nlp import analyze_symptoms_advanced
from db_config import get_mysql_connection
from pymongo import MongoClient
from datetime import datetime
import math
from prescription_routes import prescription_bp #OCR

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Register prescription blueprint
app.register_blueprint(prescription_bp) #OCR

# MongoDB connection for appointment history
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["mediquery_nlp"]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@app.route("/search", methods=["POST"])
def search_disease():
    data = request.get_json()
    symptoms = data.get("symptoms")
    user_lat = data.get("latitude")
    user_lng = data.get("longitude")
    max_distance = data.get("max_distance_km", 20)
    
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    
    disease_matches = analyze_symptoms_advanced(symptoms)
    
    if not disease_matches:
        return jsonify({"message": "No matching disease found"})
    
    results = []
    
    for match in disease_matches:
        disease_name = match["disease"]
        specialist_needed = match["specialist"]
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            d.doctor_id,
            d.name AS doctor_name,
            d.specialization,
            d.contact_no,
            h.name AS hospital_name,
            h.location,
            h.latitude,
            h.longitude,
            h.rating AS hospital_rating,
            COALESCE(dde.success_rate, 0) AS success_rate,
            COALESCE(dde.total_cases, 0) AS total_cases,
            cf.base_fee
        FROM doctor d
        JOIN hospital h ON d.hospital_id = h.hospital_id
        JOIN disease di ON di.name = %s
        LEFT JOIN doctor_disease_expertise dde 
            ON d.doctor_id = dde.doctor_id AND di.disease_id = dde.disease_id
        LEFT JOIN consultation_fees cf 
            ON d.doctor_id = cf.doctor_id AND cf.consultation_type = 'in-person'
        WHERE d.specialization = %s
        """
        
        cursor.execute(query, (disease_name, specialist_needed))
        doctors = cursor.fetchall()
        
        doctors_with_distance = []
        for doc in doctors:
            if user_lat and user_lng:
                distance = calculate_distance(
                    user_lat, user_lng,
                    float(doc["latitude"]), float(doc["longitude"])
                )
                
                if distance <= max_distance:
                    doc["distance_km"] = round(distance, 2)
                    doctors_with_distance.append(doc)
            else:
                doctors_with_distance.append(doc)
        
        doctors_with_distance.sort(
            key=lambda x: (x.get("distance_km", 999), -x.get("success_rate", 0))
        )
        
        for doc in doctors_with_distance:
            cursor.execute("""
                SELECT slot_id, slot_date, slot_time 
                FROM appointment_slots 
                WHERE doctor_id = %s AND is_booked = FALSE 
                AND slot_date >= CURDATE()
                ORDER BY slot_date, slot_time 
                LIMIT 5
            """, (doc["doctor_id"],))
            
            slots = cursor.fetchall()

            formatted_slots = []
            for slot in slots:
                formatted_slots.append({
                    "slot_id": slot["slot_id"],
                    "slot_date": slot["slot_date"].isoformat(),
                    "slot_time": str(slot["slot_time"])
                })

            doc["available_slots"] = formatted_slots
        
        cursor.close()
        conn.close()
        
        results.append({
            "disease": disease_name,
            "confidence": match["confidence"],
            "matched_symptoms": match["matched_symptoms"],
            "requires_urgent_care": match["requires_urgent_care"],
            "follow_up_questions": match.get("follow_up_questions", []),
            "doctors": doctors_with_distance[:10]
        })
    
    return jsonify({"matches": results})

@app.route("/submit-followup", methods=["POST"])
def submit_followup():
    """Process follow-up answers and refine diagnosis"""
    data = request.get_json()
    original_symptoms = data.get("original_symptoms")
    follow_up_answers = data.get("follow_up_answers")
    
    print(f"\n{'='*60}")
    print(f"RECEIVED FOLLOW-UP ANSWERS")
    print(f"{'='*60}")
    print(f"Original symptoms: {original_symptoms}")
    print(f"Follow-up answers: {follow_up_answers}")
    
    if not original_symptoms or not follow_up_answers:
        return jsonify({"error": "Missing symptoms or answers"}), 400
    
    # Re-analyze with follow-up data
    refined_matches = analyze_symptoms_advanced(original_symptoms, follow_up_answers)
    
    print(f"\n{'='*60}")
    print(f"✅ REFINED RESULTS: {len(refined_matches)} matches")
    print(f"{'='*60}")
    
    # Get doctors for refined matches
    results = []
    
    for match in refined_matches:
        disease_name = match["disease"]
        specialist_needed = match["specialist"]
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            d.doctor_id,
            d.name AS doctor_name,
            d.specialization,
            d.contact_no,
            h.name AS hospital_name,
            h.location,
            h.latitude,
            h.longitude,
            h.rating AS hospital_rating,
            COALESCE(dde.success_rate, 0) AS success_rate,
            COALESCE(dde.total_cases, 0) AS total_cases,
            cf.base_fee
        FROM doctor d
        JOIN hospital h ON d.hospital_id = h.hospital_id
        JOIN disease di ON di.name = %s
        LEFT JOIN doctor_disease_expertise dde 
            ON d.doctor_id = dde.doctor_id AND di.disease_id = dde.disease_id
        LEFT JOIN consultation_fees cf 
            ON d.doctor_id = cf.doctor_id AND cf.consultation_type = 'in-person'
        WHERE d.specialization = %s
        """
        
        cursor.execute(query, (disease_name, specialist_needed))
        doctors = cursor.fetchall()
        
        # Get slots for each doctor
        for doc in doctors:
            cursor.execute("""
                SELECT slot_id, slot_date, slot_time 
                FROM appointment_slots 
                WHERE doctor_id = %s AND is_booked = FALSE 
                AND slot_date >= CURDATE()
                ORDER BY slot_date, slot_time 
                LIMIT 5
            """, (doc["doctor_id"],))
            
            slots = cursor.fetchall()
            formatted_slots = []
            for slot in slots:
                formatted_slots.append({
                    "slot_id": slot["slot_id"],
                    "slot_date": slot["slot_date"].isoformat(),
                    "slot_time": str(slot["slot_time"])
                })
            doc["available_slots"] = formatted_slots
            
            #Convert Decimal to float for MongoDB
            doc["latitude"] = float(doc["latitude"])
            doc["longitude"] = float(doc["longitude"])
            doc["hospital_rating"] = float(doc["hospital_rating"])
            doc["success_rate"] = float(doc["success_rate"])
            if doc["base_fee"]:
                doc["base_fee"] = float(doc["base_fee"])
        
        cursor.close()
        conn.close()
        
        results.append({
            "disease": disease_name,
            "confidence": match["confidence"],
            "matched_symptoms": match["matched_symptoms"],
            "requires_urgent_care": match["requires_urgent_care"],
            "follow_up_questions": [],
            "doctors": doctors[:10]
        })
    
    # Store refined search in MongoDB
    mongo_db["user_search_history"].insert_one({
        "action": "refined_symptom_search",
        "timestamp": datetime.now(),
        "original_input": original_symptoms,
        "follow_up_answers": follow_up_answers,
        "refined_results": results
    })
    
    return jsonify({"refined_matches": results})

@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    slot_id = data.get("slot_id")
    patient_id = data.get("patient_id")
    patient_name = data.get("patient_name", "Guest Patient")
    
    if not slot_id or not patient_id:
        return jsonify({"error": "Missing slot_id or patient_id"}), 400
    
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check/create patient
        cursor.execute("SELECT patient_id FROM patient WHERE patient_id = %s", (patient_id,))
        patient_exists = cursor.fetchone()
        
        if not patient_exists:
            cursor.execute("INSERT INTO patient (patient_id, name) VALUES (%s, %s)", (patient_id, patient_name))
            conn.commit()
        
        # Get slot details (NO is_booked check - multiple bookings allowed)
        cursor.execute("""
            SELECT 
                s.slot_id, s.slot_date, s.slot_time, s.doctor_id,
                d.name AS doctor_name, d.specialization,
                h.name AS hospital_name, h.location,
                cf.base_fee
            FROM appointment_slots s
            JOIN doctor d ON s.doctor_id = d.doctor_id
            JOIN hospital h ON d.hospital_id = h.hospital_id
            LEFT JOIN consultation_fees cf 
                ON d.doctor_id = cf.doctor_id AND cf.consultation_type = 'in-person'
            WHERE s.slot_id = %s
        """, (slot_id,))
        
        slot_details = cursor.fetchone()
        
        if not slot_details:
            return jsonify({"error": "Slot not found"}), 400
        
        # Store booking in user_search_history with type="booking"
        booking_record = {
            "type": "booking", 
            "action": "appointment_booking",
            "patient_id": int(patient_id),
            "patient_name": patient_name,
            "slot_id": slot_id,
            "doctor_id": slot_details["doctor_id"],
            "doctor_name": slot_details["doctor_name"],
            "specialization": slot_details["specialization"],
            "hospital_name": slot_details["hospital_name"],
            "location": slot_details["location"],
            "appointment_date": slot_details["slot_date"].isoformat(),
            "appointment_time": str(slot_details["slot_time"]),
            "consultation_fee": float(slot_details["base_fee"]) if slot_details["base_fee"] else None,
            "booking_timestamp": datetime.now(),
            "status": "confirmed"
        }
        
        result = mongo_db["user_search_history"].insert_one(booking_record)
        booking_id = str(result.inserted_id)
        print(f"✅ Booking saved to MongoDB patient_bookings collection")
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Appointment booked successfully!",
            "booking_id": booking_id,
            "appointment_details": {
                "booking_id": booking_id,
                "patient_id": patient_id,
                "doctor": slot_details["doctor_name"],
                "hospital": slot_details["hospital_name"],
                "date": slot_details["slot_date"].isoformat(),
                "time": str(slot_details["slot_time"]),
                "fee": slot_details["base_fee"]
            }
        })
        
    except Exception as e:
        print(f"❌ Booking error: {str(e)}")
        return jsonify({"error": f"Booking failed: {str(e)}"}), 500
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/cancel-appointment", methods=["POST"])
def cancel_appointment():
    data = request.get_json()
    booking_id = data.get("booking_id")  # MongoDB _id
    patient_id = data.get("patient_id")
    
    if not booking_id or not patient_id:
        return jsonify({"error": "Missing booking_id or patient_id"}), 400
    
    try:
        from bson.objectid import ObjectId
        
        # Update status in user_search_history
        result = mongo_db["user_search_history"].update_one(
            {
                "_id": ObjectId(booking_id),
                "patient_id": int(patient_id),
                "type": "booking",
                "status": "confirmed"
            },
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Appointment not found or already cancelled"}), 404
        
        return jsonify({
            "success": True,
            "message": "Appointment cancelled successfully"
        })
        
    except Exception as e:
        print(f"❌ Cancellation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get patient appointment history
@app.route("/appointment-history/<int:patient_id>", methods=["GET"])
def get_appointment_history(patient_id):
    # Get only booking records for this patient
    appointments = list(mongo_db["user_search_history"].find(
    {
        "patient_id": patient_id,
        "type": "booking"
    },
    {"_id": 1, "booking_timestamp": 1, "doctor_name": 1, "hospital_name": 1, 
     "location": 1, "appointment_date": 1, "appointment_time": 1, 
     "consultation_fee": 1, "specialization": 1, "status": 1, "cancelled_at": 1}
).sort("booking_timestamp", -1))  # ✅ Change from "timestamp" to "booking_timestamp"
    
    # Convert ObjectId to string for JSON
    for apt in appointments:
        apt["booking_id"] = str(apt.pop("_id"))
    
    return jsonify({"appointments": appointments})

if __name__ == "__main__":
    app.run(debug=True)