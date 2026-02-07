# Create a new file: setup_followup_db.py
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["mediquery_nlp"]

# Comprehensive follow-up questions for common diseases
followup_questions_data = [
    {
        "disease": "Migraine",
        "follow_up_questions": [
            {
                "question": "Does light or sound make the pain worse?",
                "symptom_mapped": "photophobia",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Is the pain on one side of your head?",
                "symptom_mapped": "unilateral_pain",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Do you experience nausea or vomiting?",
                "symptom_mapped": "nausea",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Do you see visual disturbances (aura) before headache?",
                "symptom_mapped": "aura",
                "weight": 0.5,
                "type": "yes_no"
            },
            {
                "question": "How long does the headache typically last?",
                "symptom_mapped": "duration",
                "weight": 0.2,
                "options": ["Less than 4 hours", "4-72 hours", "More than 72 hours"],
                "type": "multiple_choice"
            }
        ],
        "specialist": "Neurologist",
        "severity_threshold": 0.7
    },
    {
        "disease": "Dengue",
        "follow_up_questions": [
            {
                "question": "Have you had a high fever for more than 3 days?",
                "symptom_mapped": "prolonged_fever",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Do you see small red or purple spots on your skin?",
                "symptom_mapped": "petechiae",
                "weight": 0.5,
                "type": "yes_no"
            },
            {
                "question": "Have you traveled to tropical areas recently?",
                "symptom_mapped": "tropical_exposure",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Are you experiencing severe joint or muscle pain?",
                "symptom_mapped": "severe_myalgia",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Do you have bleeding from nose or gums?",
                "symptom_mapped": "bleeding",
                "weight": 0.6,
                "type": "yes_no"
            }
        ],
        "specialist": "Infectious Disease Specialist",
        "severity_threshold": 0.8
    },
    {
        "disease": "Diabetes Type 2",
        "follow_up_questions": [
            {
                "question": "Are you experiencing increased thirst?",
                "symptom_mapped": "polydipsia",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Are you urinating more frequently than usual?",
                "symptom_mapped": "polyuria",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Have you noticed unexplained weight loss?",
                "symptom_mapped": "weight_loss",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Do you have a family history of diabetes?",
                "symptom_mapped": "family_history",
                "weight": 0.2,
                "type": "yes_no"
            },
            {
                "question": "Are you experiencing blurred vision?",
                "symptom_mapped": "blurred_vision",
                "weight": 0.3,
                "type": "yes_no"
            }
        ],
        "specialist": "Endocrinologist",
        "severity_threshold": 0.6
    },
    {
        "disease": "Hypertension",
        "follow_up_questions": [
            {
                "question": "Do you experience frequent headaches, especially in the morning?",
                "symptom_mapped": "morning_headaches",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Have you noticed any chest pain or discomfort?",
                "symptom_mapped": "chest_pain",
                "weight": 0.5,
                "type": "yes_no"
            },
            {
                "question": "Do you experience shortness of breath during normal activities?",
                "symptom_mapped": "dyspnea",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Do you have a family history of heart disease?",
                "symptom_mapped": "cardiac_family_history",
                "weight": 0.2,
                "type": "yes_no"
            },
            {
                "question": "Are you currently stressed or anxious?",
                "symptom_mapped": "stress",
                "weight": 0.2,
                "type": "yes_no"
            }
        ],
        "specialist": "Cardiologist",
        "severity_threshold": 0.7
    },
    {
        "disease": "Common Cold",
        "follow_up_questions": [
            {
                "question": "Do you have a runny or stuffy nose?",
                "symptom_mapped": "rhinorrhea",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Are you experiencing sneezing?",
                "symptom_mapped": "sneezing",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Do you have a sore throat?",
                "symptom_mapped": "sore_throat",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "How long have you had these symptoms?",
                "symptom_mapped": "duration",
                "weight": 0.2,
                "options": ["Less than 3 days", "3-7 days", "More than 7 days"],
                "type": "multiple_choice"
            }
        ],
        "specialist": "General Physician",
        "severity_threshold": 0.4
    },
    {
        "disease": "Pneumonia",
        "follow_up_questions": [
            {
                "question": "Do you have a persistent cough with phlegm?",
                "symptom_mapped": "productive_cough",
                "weight": 0.5,
                "type": "yes_no"
            },
            {
                "question": "Are you experiencing chest pain when breathing or coughing?",
                "symptom_mapped": "pleuritic_pain",
                "weight": 0.4,
                "type": "yes_no"
            },
            {
                "question": "Do you have difficulty breathing or shortness of breath?",
                "symptom_mapped": "dyspnea",
                "weight": 0.5,
                "type": "yes_no"
            },
            {
                "question": "Are you experiencing chills and sweating?",
                "symptom_mapped": "chills",
                "weight": 0.3,
                "type": "yes_no"
            },
            {
                "question": "Is your fever higher than 100.4°F (38°C)?",
                "symptom_mapped": "high_fever",
                "weight": 0.4,
                "type": "yes_no"
            }
        ],
        "specialist": "Pulmonologist",
        "severity_threshold": 0.8
    }
]

# Insert into MongoDB
def setup_followup_database():
    # Clear existing data
    db["disease_followup_questions"].delete_many({})
    
    # Insert new data
    db["disease_followup_questions"].insert_many(followup_questions_data)
    
    print(f"✅ Inserted {len(followup_questions_data)} disease follow-up templates")
    
    # Create index for faster queries
    db["disease_followup_questions"].create_index("disease")
    
    print("✅ Database setup complete!")

if __name__ == "__main__":
    setup_followup_database()


