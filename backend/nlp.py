from pymongo import MongoClient
import re
client = MongoClient("mongodb://localhost:27017/") # change to your url
db = client["mediquery_nlp"] # change to your client
collection = db["diseases_symptoms"] # change to your collection

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    return words

def find_disease(user_input):
    user_words = clean_text(user_input)
    diseases = collection.find()

    best_match = None
    max_matches = 0

    for disease in diseases:
        symptoms = disease.get("symptoms", [])
        keywords = disease.get("keywords", [])

        match_count = 0

        for word in user_words:
            if word in symptoms or word in keywords:
                match_count += 1

        if match_count > max_matches:
            max_matches = match_count
            best_match = disease["disease"]

    return best_match

if __name__ == "__main__":
    sentence = input("Enter your symptoms: ")
    result = find_disease(sentence)
    print("Possible Disease:", result)
