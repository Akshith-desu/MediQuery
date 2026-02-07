from pymongo import MongoClient
from datetime import datetime
import re

client = MongoClient("mongodb://localhost:27017/")
db = client["mediquery_nlp"]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text.split()

def get_followup_questions(disease_name):
    """Fetch follow-up questions for a disease"""
    print(f"🔍 Searching follow-up questions for: '{disease_name}'")
    disease_data = db["disease_followup_questions"].find_one({"disease": disease_name})
    
    if disease_data:
        questions = disease_data.get("follow_up_questions", [])
        print(f"✅ Found {len(questions)} questions for {disease_name}")
        return questions
    else:
        print(f"❌ No follow-up data found for: '{disease_name}'")
        return []

def analyze_symptoms_advanced(user_input, follow_up_answers=None):
    """
    Multi-stage symptom analysis with proper follow-up integration
    """
    
    print(f"\n{'='*60}")
    print(f"🔍 ANALYZING SYMPTOMS: '{user_input}'")
    if follow_up_answers:
        print(f"📋 Follow-up answers provided: {follow_up_answers}")
    print(f"{'='*60}")
    
    # Clean and tokenize
    user_words = clean_text(user_input)
    print(f"📝 Tokenized words: {user_words}")
    
    # Check for emergency keywords
    emergency_keywords = ["severe", "acute", "unbearable", "emergency", "urgent", "bleeding", "unconscious"]
    is_emergency = any(keyword in user_input.lower() for keyword in emergency_keywords)
    
    # Get all disease documents
    diseases = list(db["medical_knowledge"].find())
    print(f"📚 Total diseases in database: {len(diseases)}")
    
    # Calculate matching scores
    disease_scores = []
    
    for disease in diseases:
        initial_score = 0
        matched_symptoms = []
        total_possible_weight = 0
        
        # STEP 1: Match original symptoms from user input
        for symptom in disease.get("symptoms", []):
            symptom_name = symptom["name"]
            weight = symptom.get("weight", 0.5)
            total_possible_weight += weight
            
            if symptom_name in user_words:
                initial_score += weight
                matched_symptoms.append(symptom_name)
        
        # STEP 2: Add follow-up answer scores (THIS WAS MISSING!)
        followup_score = 0
        followup_matched = []
        
        if follow_up_answers:
            followup_questions = get_followup_questions(disease["disease"])
            
            for fq in followup_questions:
                question_text = fq["question"]
                answer = follow_up_answers.get(question_text)
                
                # Check if answer is "yes" or matches an option
                if answer:
                    if fq["type"] == "yes_no" and answer.lower() == "yes":
                        followup_score += fq["weight"]
                        followup_matched.append(fq["symptom_mapped"])
                        total_possible_weight += fq["weight"]
                    elif fq["type"] == "multiple_choice":
                        # For multiple choice, any non-empty answer adds weight
                        followup_score += fq["weight"]
                        followup_matched.append(f"{fq['symptom_mapped']}:{answer}")
                        total_possible_weight += fq["weight"]
        
        # STEP 3: Calculate final score
        total_score = initial_score + followup_score
        
        # STEP 4: Calculate confidence (normalize by total possible weight)
        if total_possible_weight > 0:
            confidence = min(total_score / total_possible_weight, 1.0)
        else:
            confidence = 0.0
        
        # Only include diseases with some match
        if total_score > 0:
            # Get follow-up questions ONLY if no follow-up answers were provided yet
            followup_qs = [] if follow_up_answers else get_followup_questions(disease["disease"])
            
            print(f"\n✨ MATCH FOUND: {disease['disease']}")
            print(f"   Initial score: {initial_score:.2f}")
            print(f"   Follow-up score: {followup_score:.2f}")
            print(f"   Total score: {total_score:.2f}/{total_possible_weight:.2f}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Initial symptoms: {matched_symptoms}")
            if followup_matched:
                print(f"   ✅ Follow-up confirmations: {followup_matched}")
            
            all_matched = matched_symptoms + followup_matched
            
            disease_scores.append({
                "disease": disease["disease"],
                "confidence": confidence,
                "matched_symptoms": all_matched,
                "specialist": disease["specialist_requirements"]["primary"],
                "requires_urgent_care": is_emergency or disease["specialist_requirements"].get("urgent_care_eligible", False),
                "follow_up_questions": followup_qs,
                "score_breakdown": {
                    "initial_score": initial_score,
                    "followup_score": followup_score,
                    "total_score": total_score,
                    "max_possible": total_possible_weight
                }
            })
    
    # Sort by confidence
    disease_scores.sort(key=lambda x: x["confidence"], reverse=True)
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS: {len(disease_scores)} matches")
    if disease_scores:
        print(f"Top match: {disease_scores[0]['disease']} ({disease_scores[0]['confidence']:.1%})")
    print(f"{'='*60}")
    
    # Store to user_search_history
    action_type = "refined_symptom_search" if follow_up_answers else "symptom_search"
    
    db["user_search_history"].insert_one({
        "action": action_type,
        "timestamp": datetime.now(),
        "input": user_input,
        "follow_up_answers": follow_up_answers,
        "results": disease_scores[:3],
        "emergency_detected": is_emergency
    })
    
    return disease_scores[:3]