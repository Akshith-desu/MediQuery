from flask import Flask, request, jsonify
from flask_cors import CORS
from nlp import find_disease
from db_config import get_mysql_connection

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/search", methods=["POST"])
def search_disease():
    data = request.get_json()
    symptoms = data.get("symptoms")

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    # Step 1: NLP → disease
    disease = find_disease(symptoms)

    if not disease:
        return jsonify({"message": "No matching disease found"})

    # Step 2: MySQL → doctors
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT d.name AS doctor_name, d.specialization, h.name AS hospital_name
    FROM doctor d
    JOIN hospital h ON d.hospital_id = h.hospital_id
    JOIN disease di ON d.specialization = di.department
    WHERE di.name = %s
    """

    cursor.execute(query, (disease,))
    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "disease": disease,
        "doctors": doctors
    })

if __name__ == "__main__":
    app.run(debug=True)
