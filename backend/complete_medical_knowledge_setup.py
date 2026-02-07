from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mediquery_nlp"]

# ============================================
# COMPLETE MEDICAL KNOWLEDGE DATA
# ============================================

medical_knowledge_data = [
    {
        "_id": "migraine_001",
        "disease": "Migraine",
        "severity_levels": ["mild", "moderate", "severe"],
        "symptoms": [
            {"name": "headache", "weight": 1.0, "severity": "high"},
            {"name": "nausea", "weight": 0.7, "severity": "medium"},
            {"name": "sensitivity", "weight": 0.6, "severity": "medium"},
            {"name": "light", "weight": 0.6, "severity": "medium"},
            {"name": "sound", "weight": 0.5, "severity": "medium"},
            {"name": "vomiting", "weight": 0.5, "severity": "medium"},
            {"name": "throbbing", "weight": 0.8, "severity": "high"},
            {"name": "pulsating", "weight": 0.7, "severity": "high"},
            {"name": "aura", "weight": 0.8, "severity": "high"},
            {"name": "visual", "weight": 0.6, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Neurologist",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Pain management", "Preventive medication", "Lifestyle modifications"],
        "patient_reviews": []
    },
    {
        "_id": "dengue_001",
        "disease": "Dengue",
        "severity_levels": ["mild", "moderate", "severe", "critical"],
        "symptoms": [
            {"name": "fever", "weight": 1.0, "severity": "high"},
            {"name": "body", "weight": 0.8, "severity": "high"},
            {"name": "pain", "weight": 0.8, "severity": "high"},
            {"name": "rash", "weight": 0.7, "severity": "medium"},
            {"name": "joint", "weight": 0.7, "severity": "high"},
            {"name": "muscle", "weight": 0.7, "severity": "high"},
            {"name": "headache", "weight": 0.6, "severity": "medium"},
            {"name": "fatigue", "weight": 0.6, "severity": "medium"},
            {"name": "bleeding", "weight": 0.9, "severity": "critical"},
            {"name": "vomiting", "weight": 0.6, "severity": "medium"},
            {"name": "spots", "weight": 0.8, "severity": "high"},
            {"name": "petechiae", "weight": 0.8, "severity": "high"}
        ],
        "specialist_requirements": {
            "primary": "Infectious Disease Specialist",
            "urgent_care_eligible": True
        },
        "treatment_protocols": ["Hydration therapy", "Platelet monitoring", "Symptomatic treatment"],
        "patient_reviews": []
    },
    {
        "_id": "diabetes_001",
        "disease": "Diabetes Type 2",
        "severity_levels": ["pre-diabetes", "controlled", "uncontrolled", "complicated"],
        "symptoms": [
            {"name": "thirst", "weight": 0.9, "severity": "high"},
            {"name": "urination", "weight": 0.9, "severity": "high"},
            {"name": "frequent", "weight": 0.8, "severity": "high"},
            {"name": "hunger", "weight": 0.7, "severity": "medium"},
            {"name": "fatigue", "weight": 0.7, "severity": "medium"},
            {"name": "weight", "weight": 0.8, "severity": "high"},
            {"name": "loss", "weight": 0.7, "severity": "high"},
            {"name": "blurred", "weight": 0.8, "severity": "high"},
            {"name": "vision", "weight": 0.8, "severity": "high"},
            {"name": "wounds", "weight": 0.7, "severity": "medium"},
            {"name": "healing", "weight": 0.6, "severity": "medium"},
            {"name": "numbness", "weight": 0.7, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Endocrinologist",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Blood sugar monitoring", "Insulin therapy", "Dietary management"],
        "patient_reviews": []
    },
    {
        "_id": "hypertension_001",
        "disease": "Hypertension",
        "severity_levels": ["stage1", "stage2", "hypertensive_crisis"],
        "symptoms": [
            {"name": "headache", "weight": 0.7, "severity": "medium"},
            {"name": "dizziness", "weight": 0.7, "severity": "medium"},
            {"name": "chest", "weight": 0.9, "severity": "critical"},
            {"name": "pain", "weight": 0.8, "severity": "high"},
            {"name": "shortness", "weight": 0.8, "severity": "high"},
            {"name": "breath", "weight": 0.8, "severity": "high"},
            {"name": "fatigue", "weight": 0.6, "severity": "medium"},
            {"name": "nosebleed", "weight": 0.6, "severity": "medium"},
            {"name": "irregular", "weight": 0.7, "severity": "high"},
            {"name": "heartbeat", "weight": 0.7, "severity": "high"},
            {"name": "vision", "weight": 0.6, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Cardiologist",
            "urgent_care_eligible": True
        },
        "treatment_protocols": ["Blood pressure monitoring", "Antihypertensive medication", "Lifestyle changes"],
        "patient_reviews": []
    },
    {
        "_id": "cold_001",
        "disease": "Common Cold",
        "severity_levels": ["mild", "moderate"],
        "symptoms": [
            {"name": "runny", "weight": 0.9, "severity": "low"},
            {"name": "nose", "weight": 0.9, "severity": "low"},
            {"name": "sneezing", "weight": 0.8, "severity": "low"},
            {"name": "cough", "weight": 0.7, "severity": "low"},
            {"name": "sore", "weight": 0.7, "severity": "low"},
            {"name": "throat", "weight": 0.7, "severity": "low"},
            {"name": "congestion", "weight": 0.8, "severity": "low"},
            {"name": "mild", "weight": 0.5, "severity": "low"},
            {"name": "fever", "weight": 0.5, "severity": "low"},
            {"name": "fatigue", "weight": 0.5, "severity": "low"}
        ],
        "specialist_requirements": {
            "primary": "General Physician",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Rest", "Hydration", "Over-the-counter medication"],
        "patient_reviews": []
    },
    {
        "_id": "pneumonia_001",
        "disease": "Pneumonia",
        "severity_levels": ["mild", "moderate", "severe"],
        "symptoms": [
            {"name": "cough", "weight": 1.0, "severity": "high"},
            {"name": "fever", "weight": 0.9, "severity": "high"},
            {"name": "chest", "weight": 0.9, "severity": "high"},
            {"name": "pain", "weight": 0.8, "severity": "high"},
            {"name": "shortness", "weight": 0.9, "severity": "critical"},
            {"name": "breath", "weight": 0.9, "severity": "critical"},
            {"name": "breathing", "weight": 0.9, "severity": "critical"},
            {"name": "difficulty", "weight": 0.8, "severity": "high"},
            {"name": "phlegm", "weight": 0.8, "severity": "high"},
            {"name": "chills", "weight": 0.7, "severity": "medium"},
            {"name": "sweating", "weight": 0.6, "severity": "medium"},
            {"name": "fatigue", "weight": 0.7, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Pulmonologist",
            "urgent_care_eligible": True
        },
        "treatment_protocols": ["Antibiotics", "Oxygen therapy", "Rest and hydration"],
        "patient_reviews": []
    },
    {
        "_id": "arthritis_001",
        "disease": "Arthritis",
        "severity_levels": ["mild", "moderate", "severe"],
        "symptoms": [
            {"name": "joint", "weight": 1.0, "severity": "high"},
            {"name": "pain", "weight": 0.9, "severity": "high"},
            {"name": "stiffness", "weight": 0.9, "severity": "high"},
            {"name": "swelling", "weight": 0.8, "severity": "medium"},
            {"name": "inflammation", "weight": 0.8, "severity": "medium"},
            {"name": "reduced", "weight": 0.7, "severity": "medium"},
            {"name": "mobility", "weight": 0.7, "severity": "medium"},
            {"name": "redness", "weight": 0.6, "severity": "medium"},
            {"name": "warmth", "weight": 0.6, "severity": "medium"},
            {"name": "morning", "weight": 0.7, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Orthopedic Surgeon",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Pain management", "Physical therapy", "Anti-inflammatory medication"],
        "patient_reviews": []
    },
    {
        "_id": "asthma_001",
        "disease": "Asthma",
        "severity_levels": ["mild_intermittent", "mild_persistent", "moderate", "severe"],
        "symptoms": [
            {"name": "wheezing", "weight": 1.0, "severity": "high"},
            {"name": "shortness", "weight": 0.9, "severity": "high"},
            {"name": "breath", "weight": 0.9, "severity": "high"},
            {"name": "breathing", "weight": 0.9, "severity": "high"},
            {"name": "difficulty", "weight": 0.8, "severity": "high"},
            {"name": "chest", "weight": 0.8, "severity": "medium"},
            {"name": "tightness", "weight": 0.8, "severity": "medium"},
            {"name": "cough", "weight": 0.7, "severity": "medium"},
            {"name": "night", "weight": 0.7, "severity": "medium"},
            {"name": "exercise", "weight": 0.6, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Pulmonologist",
            "urgent_care_eligible": True
        },
        "treatment_protocols": ["Inhaler therapy", "Bronchodilators", "Avoid triggers"],
        "patient_reviews": []
    },
    {
        "_id": "gastritis_001",
        "disease": "Gastritis",
        "severity_levels": ["acute", "chronic"],
        "symptoms": [
            {"name": "stomach", "weight": 1.0, "severity": "high"},
            {"name": "pain", "weight": 0.9, "severity": "high"},
            {"name": "burning", "weight": 0.9, "severity": "high"},
            {"name": "nausea", "weight": 0.8, "severity": "medium"},
            {"name": "vomiting", "weight": 0.7, "severity": "medium"},
            {"name": "bloating", "weight": 0.7, "severity": "medium"},
            {"name": "indigestion", "weight": 0.8, "severity": "medium"},
            {"name": "loss", "weight": 0.6, "severity": "medium"},
            {"name": "appetite", "weight": 0.6, "severity": "medium"},
            {"name": "acid", "weight": 0.7, "severity": "medium"}
        ],
        "specialist_requirements": {
            "primary": "Gastroenterologist",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Antacids", "Dietary changes", "Stress management"],
        "patient_reviews": []
    },
    {
        "_id": "skin_allergy_001",
        "disease": "Skin Allergy",
        "severity_levels": ["mild", "moderate", "severe"],
        "symptoms": [
            {"name": "itching", "weight": 1.0, "severity": "medium"},
            {"name": "rash", "weight": 0.9, "severity": "medium"},
            {"name": "redness", "weight": 0.8, "severity": "medium"},
            {"name": "swelling", "weight": 0.8, "severity": "high"},
            {"name": "hives", "weight": 0.9, "severity": "high"},
            {"name": "burning", "weight": 0.7, "severity": "medium"},
            {"name": "dry", "weight": 0.6, "severity": "low"},
            {"name": "skin", "weight": 0.7, "severity": "medium"},
            {"name": "bumps", "weight": 0.7, "severity": "medium"},
            {"name": "blisters", "weight": 0.8, "severity": "high"}
        ],
        "specialist_requirements": {
            "primary": "Dermatologist",
            "urgent_care_eligible": False
        },
        "treatment_protocols": ["Antihistamines", "Topical creams", "Avoid allergens"],
        "patient_reviews": []
    }
]

# ============================================
# SETUP FUNCTION
# ============================================

def setup_complete_medical_knowledge():
    """
    Populate MongoDB with complete medical knowledge for all diseases
    """
    print(f"\n{'='*60}")
    print(f"🏥 SETTING UP COMPLETE MEDICAL KNOWLEDGE DATABASE")
    print(f"{'='*60}\n")
    
    # Clear existing data
    result = db["medical_knowledge"].delete_many({})
    print(f"🗑️  Cleared {result.deleted_count} existing records")
    
    # Insert new data
    result = db["medical_knowledge"].insert_many(medical_knowledge_data)
    print(f"✅ Inserted {len(result.inserted_ids)} disease records")
    
    # Create indexes for faster queries
    db["medical_knowledge"].create_index("disease")
    db["medical_knowledge"].create_index([("symptoms.name", 1)])
    print(f"📊 Created indexes on 'disease' and 'symptoms.name'")
    
    # Verify data
    print(f"\n{'='*60}")
    print(f"📋 VERIFICATION")
    print(f"{'='*60}")
    
    for disease in medical_knowledge_data:
        doc = db["medical_knowledge"].find_one({"disease": disease["disease"]})
        if doc:
            print(f"✅ {disease['disease']}: {len(doc['symptoms'])} symptoms, Specialist: {doc['specialist_requirements']['primary']}")
        else:
            print(f"❌ {disease['disease']}: NOT FOUND")
    
    print(f"\n{'='*60}")
    print(f"✅ DATABASE SETUP COMPLETE!")
    print(f"{'='*60}\n")
    
    return True

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    try:
        setup_complete_medical_knowledge()
        
        # Additional verification
        total_diseases = db["medical_knowledge"].count_documents({})
        print(f"📊 Total diseases in database: {total_diseases}")
        
        # Show all disease names
        print(f"\n📋 Available Diseases:")
        for doc in db["medical_knowledge"].find({}, {"disease": 1, "_id": 0}):
            print(f"   • {doc['disease']}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    finally:
        client.close()
        print(f"\n🔌 MongoDB connection closed")