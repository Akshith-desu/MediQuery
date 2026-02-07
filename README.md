# 🏥 MediQuery - Smart Medical Consultation System

<div align="center">

![MediQuery Banner](https://img.shields.io/badge/MediQuery-Smart%20Healthcare-blue?style=for-the-badge)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0-green?style=flat-square&logo=mongodb)](https://www.mongodb.com/)

**An intelligent healthcare platform connecting patients with the right doctors through AI-powered symptom analysis and location-based search**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**MediQuery** is a comprehensive medical consultation platform that leverages natural language processing (NLP) and machine learning to help patients find the most suitable doctors based on their symptoms. The system provides:

- **Intelligent Symptom Analysis**: Advanced NLP algorithms analyze user-described symptoms and match them with potential diseases
- **Smart Doctor Recommendations**: Location-aware search finds nearby specialists with expertise in diagnosed conditions
- **Prescription Management**: OCR-powered prescription upload and digital record keeping
- **Appointment Scheduling**: Real-time slot booking with doctors
- **Medical History Timeline**: Complete patient health record visualization
- **Shareable Medical Records**: Secure, time-limited sharing of prescriptions with healthcare providers

---

## ✨ Features

### 🔍 Core Features

#### 1. **AI-Powered Symptom Analysis**

- Multi-stage NLP engine processes natural language symptom descriptions
- Confidence-based disease matching with weighted symptom correlation
- Dynamic follow-up questions for accurate diagnosis refinement
- Emergency detection for critical symptoms

#### 2. **Location-Based Doctor Search**

- Geolocation integration using Google Maps API
- Customizable search radius (5-50 km)
- Real-time distance calculation using Haversine formula
- Hospital and doctor ratings display

#### 3. **Prescription Intelligence**

- **OCR Technology**: Automatic text extraction from prescription images/PDFs
- **Multi-format Support**: Handles JPG, PNG, PDF prescription formats
- **Smart Parsing**: Extracts doctor name, hospital, medicines, dosages, and instructions
- **Medicine Search**: Find specific medications across all prescriptions
- **Shareable Links**: Generate secure, password-protected links for medical records

#### 4. **Appointment Management**

- Real-time slot availability checking
- Multi-slot booking support
- Appointment history tracking
- Cancellation functionality
- Email/SMS notifications (planned)

#### 5. **Medical Timeline**

- Unified view of prescriptions and appointments
- Chronological health record visualization
- Export capabilities for insurance claims

---

## 🛠 Tech Stack

### Backend

- **Flask** - Python web framework
- **Python 3.8+** - Core programming language
- **MySQL** - Relational database for structured medical data
- **MongoDB** - NoSQL database for user history and prescriptions
- **GridFS** - File storage for prescription documents

### Frontend

- **HTML5/CSS3** - Modern responsive UI
- **JavaScript (ES6+)** - Client-side interactivity
- **Google Maps JavaScript API** - Interactive mapping

### AI/ML & Processing

- **Tesseract OCR** - Optical character recognition for prescriptions
- **pdf2image** - PDF to image conversion
- **Pillow (PIL)** - Image processing
- **Custom NLP Engine** - Symptom-disease matching algorithm

### Additional Tools

- **Poppler** - PDF rendering utilities
- **CORS** - Cross-origin resource sharing
- **JSON** - Data interchange format

---

## 🏗 System Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │
│   (app.py)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ MySQL  │ │ MongoDB  │
│  DB    │ │   DB     │
└────────┘ └──────────┘
    │          │
    └──────┬───┘
           ▼
    ┌─────────────┐
    │  NLP Engine │
    │  OCR Engine │
    └─────────────┘
```

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **MySQL 8.0+** ([Download](https://dev.mysql.com/downloads/installer/))
- **MongoDB 5.0+** ([Download](https://www.mongodb.com/try/download/community))
- **Tesseract OCR** ([Installation Guide](#tesseract-installation))
- **Poppler** (for PDF processing - [Installation Guide](#poppler-installation))
- **Git** ([Download](https://git-scm.com/downloads))

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/mediquery.git
cd mediquery
```

---

### Step 2: Set Up Python Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required packages (included in `requirements.txt`):**

```
Flask==2.3.0
flask-cors==4.0.0
mysql-connector-python==8.0.33
pymongo==4.3.3
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==9.5.0
```

---

### Step 4: Install System Dependencies

#### Tesseract Installation

**Windows:**

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or update `ocr_processor.py` with installation path

**macOS:**

```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### Poppler Installation

**Windows:**

1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler` (or any location)
3. Update `POPPLER_PATH` in `ocr_processor.py`

**macOS:**

```bash
brew install poppler
```

**Linux:**

```bash
sudo apt-get install poppler-utils
```

---

## ⚙️ Configuration

### 1. Database Configuration

#### Update MySQL Credentials

Edit `backend/db_config.py`:

```python
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",  # Replace with your password
        database="mediquery"
    )
```

#### Update MongoDB Connection

The default MongoDB connection in `app.py` and `prescription_routes.py`:

```python
mongo_client = MongoClient("mongodb://localhost:27017/")
```

If your MongoDB uses authentication, update to:

```python
mongo_client = MongoClient("mongodb://username:password@localhost:27017/")
```

---

### 2. Google Maps API Configuration

Edit `frontend/index.html`:

```javascript
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
```

**To get an API key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Maps JavaScript API"
4. Create credentials → API Key
5. Restrict key to your domain (optional but recommended)

---

### 3. OCR Configuration

Edit `backend/ocr_processor.py`:

**Windows:**

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\path\to\poppler\Library\bin'
```

**macOS/Linux:**

```python
# Usually auto-detected, but if needed:
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
# Poppler is auto-detected on Unix systems
```

---

## 💾 Database Setup

### MySQL Database Setup

#### 1. Create Database and Tables

Open MySQL Command Line or MySQL Workbench:

```sql
CREATE DATABASE mediquery;
USE mediquery;
```

#### 2. Run Database Schema

Execute the SQL file located at `backend/sql_setup.sql`:

**Via Command Line:**

```bash
mysql -u root -p mediquery < backend/sql_setup.sql
```

**Via MySQL Workbench:**

1. Open `backend/sql_setup.sql`
2. Execute the entire script

This creates the following tables:

- `hospital` - Hospital information with geolocation
- `doctor` - Doctor profiles and specializations
- `disease` - Disease catalog
- `doctor_disease_expertise` - Doctor expertise mapping
- `consultation_fees` - Consultation pricing
- `appointment_slots` - Available time slots
- `patient` - Patient records

---

### MongoDB Setup

#### 1. Start MongoDB Service

**Windows:**

```bash
net start MongoDB
```

**macOS:**

```bash
brew services start mongodb-community
```

**Linux:**

```bash
sudo systemctl start mongod
```

#### 2. Initialize Medical Knowledge Database

Run the setup script:

```bash
cd backend
python complete_medical_knowledge_setup.py
```

This populates:

- **medical_knowledge** collection - Disease symptom mappings
- Symptom weights and severity levels
- Specialist requirements

#### 3. Initialize Follow-up Questions Database

```bash
python setup_followup_db.py
```

This creates:

- **disease_followup_questions** collection - Dynamic diagnostic questions

#### 4. Verify MongoDB Collections

```bash
mongo
> use mediquery_nlp
> show collections
```

Expected collections:

- `medical_knowledge`
- `disease_followup_questions`
- `user_search_history`
- `patient_prescriptions`
- `prescription_shares`
- `shared_records`

---

## 🎮 Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

Server will start at: `http://127.0.0.1:5000`

**Expected output:**

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Start Frontend

#### Option 1: Using Live Server (Recommended)

1. Install VS Code extension: "Live Server"
2. Right-click `frontend/index.html`
3. Select "Open with Live Server"

Frontend will open at: `http://127.0.0.1:5500` (or similar)

#### Option 2: Using Python HTTP Server

```bash
cd frontend
python -m http.server 8000
```

Open browser: `http://localhost:8000`

---

### Verify Installation

✅ **Quick Test Checklist:**

1. **Backend Health Check**
   - Visit: `http://127.0.0.1:5000/`
   - Should NOT see "404 Not Found"

2. **Frontend Loading**
   - Open: `http://localhost:5500`
   - Should see "MediQuery - Smart Medical Consultation System"

3. **Database Connections**
   - Check terminal for any MySQL/MongoDB errors
   - No errors = successful connection

4. **Feature Test**
   - Click "Use My Location" button
   - Enter symptoms: "headache nausea"
   - Click "Search Doctors"
   - Should see disease matches and doctor list

---

## 📚 API Reference

### Core Endpoints

#### 1. **Search Doctors by Symptoms**

```http
POST /search
Content-Type: application/json
```

**Request Body:**

```json
{
  "symptoms": "severe headache nausea sensitivity to light",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "max_distance_km": 20
}
```

**Response:**

```json
{
  "matches": [
    {
      "disease": "Migraine",
      "confidence": 0.85,
      "matched_symptoms": ["headache", "nausea", "sensitivity"],
      "requires_urgent_care": false,
      "follow_up_questions": [...],
      "doctors": [...]
    }
  ]
}
```

---

#### 2. **Submit Follow-up Answers**

```http
POST /submit-followup
Content-Type: application/json
```

**Request Body:**

```json
{
  "original_symptoms": "headache nausea",
  "follow_up_answers": {
    "Does light or sound make the pain worse?": "yes",
    "Is the pain on one side of your head?": "yes"
  }
}
```

---

#### 3. **Book Appointment**

```http
POST /book-appointment
Content-Type: application/json
```

**Request Body:**

```json
{
  "slot_id": 123,
  "patient_id": 1001,
  "patient_name": "John Doe"
}
```

**Response:**

```json
{
  "success": true,
  "booking_id": "507f1f77bcf86cd799439011",
  "appointment_details": {
    "doctor": "Dr. Ramesh Rao",
    "hospital": "Apollo Hospital",
    "date": "2026-01-16",
    "time": "09:00:00",
    "fee": 1000.0
  }
}
```

---

#### 4. **Upload Prescription**

```http
POST /upload-prescription
Content-Type: multipart/form-data
```

**Form Data:**

```
file: [prescription.pdf or image.jpg]
patient_id: 1001
```

**Response:**

```json
{
  "success": true,
  "prescription_id": "507f...",
  "extracted_data": {
    "doctor_name": "Dr. Smith",
    "medicines": [
      {
        "name": "Paracetamol 500mg",
        "dosage": "500mg",
        "frequency": "1-0-1",
        "duration": "5 days"
      }
    ]
  }
}
```

---

#### 5. **Get Appointment History**

```http
GET /appointment-history/{patient_id}
```

**Response:**

```json
{
  "appointments": [
    {
      "booking_id": "507f...",
      "doctor_name": "Dr. Ramesh Rao",
      "hospital_name": "Apollo Hospital",
      "appointment_date": "2026-01-16",
      "appointment_time": "09:00:00",
      "status": "confirmed"
    }
  ]
}
```

---

#### 6. **Get Medical Timeline**

```http
GET /medical-timeline/{patient_id}
```

Combines prescriptions and appointments in chronological order.

---

#### 7. **Generate Shareable Link**

```http
POST /generate-share-link/{patient_id}
Content-Type: application/json
```

**Request Body:**

```json
{
  "expiry_hours": 24,
  "password": "optional_password"
}
```

**Response:**

```json
{
  "success": true,
  "share_url": "http://localhost:5000/view-shared/abc123xyz",
  "expires_at": "2026-01-17T10:00:00",
  "requires_password": true
}
```

---

### Full API Documentation

| Endpoint                            | Method | Description                                    |
| ----------------------------------- | ------ | ---------------------------------------------- |
| `/search`                           | POST   | Search doctors by symptoms                     |
| `/submit-followup`                  | POST   | Submit follow-up answers for refined diagnosis |
| `/book-appointment`                 | POST   | Book doctor appointment                        |
| `/cancel-appointment`               | POST   | Cancel existing appointment                    |
| `/appointment-history/<patient_id>` | GET    | Get patient appointment history                |
| `/upload-prescription`              | POST   | Upload prescription with OCR                   |
| `/prescriptions/<patient_id>`       | GET    | Get all patient prescriptions                  |
| `/download-prescription/<id>`       | GET    | Download original prescription file            |
| `/medical-timeline/<patient_id>`    | GET    | Get unified medical timeline                   |
| `/search-medicine/<patient_id>`     | POST   | Search specific medicine in history            |
| `/generate-share-link/<patient_id>` | POST   | Generate shareable medical record link         |
| `/view-shared/<token>`              | POST   | View shared medical records                    |

---

## 📁 Project Structure

```
mediquery/
│
├── backend/
│   ├── app.py                              # Main Flask application
│   ├── db_config.py                        # MySQL database configuration
│   ├── nlp.py                              # NLP symptom analysis engine
│   ├── ocr_processor.py                    # OCR prescription processing
│   ├── prescription_routes.py              # Prescription management routes
│   ├── complete_medical_knowledge_setup.py # MongoDB medical data setup
│   ├── setup_followup_db.py                # Follow-up questions setup
│   ├── sql_setup.sql                       # MySQL schema and sample data
│   └── requirements.txt                    # Python dependencies
│
├── frontend/
│   ├── index.html                          # Main UI
│   ├── script.js                           # Frontend JavaScript logic
│   └── styles.css                          # Styling
│
├── .gitignore                              # Git ignore rules
└── README.md                               # This file
```

---

## 📸 Screenshots

### 1. **Symptom Search Interface**

![Search Interface](screenshots/search.png)

### 2. **Doctor Results with Map**

![Doctor Results](screenshots/results.png)

### 3. **Prescription Upload & OCR**

![Prescription OCR](screenshots/prescription.png)

### 4. **Medical Timeline**

![Timeline](screenshots/timeline.png)

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### ❌ "MySQL Connection Failed"

**Problem:** Cannot connect to MySQL database

**Solutions:**

1. Verify MySQL service is running:

   ```bash
   # Windows
   net start MySQL80

   # macOS
   brew services start mysql

   # Linux
   sudo systemctl start mysql
   ```

2. Check credentials in `db_config.py`
3. Ensure database `mediquery` exists:
   ```sql
   SHOW DATABASES;
   ```

---

#### ❌ "MongoDB Connection Refused"

**Problem:** Cannot connect to MongoDB

**Solutions:**

1. Start MongoDB service:

   ```bash
   # Windows
   net start MongoDB

   # macOS
   brew services start mongodb-community

   # Linux
   sudo systemctl start mongod
   ```

2. Verify MongoDB is listening on port 27017:
   ```bash
   mongo --eval "db.stats()"
   ```

---

#### ❌ "OCR Not Working / Tesseract Error"

**Problem:** Prescription upload fails with OCR error

**Solutions:**

1. Verify Tesseract installation:

   ```bash
   tesseract --version
   ```

2. Update Tesseract path in `ocr_processor.py`:

   ```python
   pytesseract.pytesseract.tesseract_cmd = r'YOUR_TESSERACT_PATH'
   ```

3. **Windows users**: Ensure path uses raw string (`r'...'`) with backslashes

---

#### ❌ "PDF Processing Failed"

**Problem:** Cannot process PDF prescriptions

**Solutions:**

1. Verify Poppler installation
2. Update `POPPLER_PATH` in `ocr_processor.py`:
   ```python
   POPPLER_PATH = r'C:\path\to\poppler\Library\bin'
   ```

---

#### ❌ "No Doctors Found"

**Problem:** Search returns empty results

**Solutions:**

1. Verify MySQL data populated:

   ```sql
   USE mediquery;
   SELECT COUNT(*) FROM doctor;
   SELECT COUNT(*) FROM disease;
   ```

2. Check MongoDB medical knowledge:

   ```javascript
   use mediquery_nlp
   db.medical_knowledge.count()
   ```

3. Re-run setup scripts if needed

---

#### ❌ "CORS Error in Browser"

**Problem:** Frontend cannot connect to backend

**Solutions:**

1. Verify CORS is enabled in `app.py`:

   ```python
   CORS(app, resources={r"/*": {"origins": "*"}})
   ```

2. Check backend is running on port 5000
3. Update frontend API URLs if needed

---

#### ❌ "Google Maps Not Loading"

**Problem:** Map shows blank or error

**Solutions:**

1. Verify API key in `index.html`
2. Check API key has "Maps JavaScript API" enabled
3. Check browser console for specific error messages
4. Ensure billing is enabled on Google Cloud (free tier available)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, etc.)

### Suggesting Features

1. Open an issue with `[FEATURE REQUEST]` prefix
2. Describe the feature and its benefits
3. Provide examples or mockups if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update documentation for new features

---

## 📊 Database Schema

### MySQL Tables

#### **hospital**

```sql
hospital_id, name, location, latitude, longitude,
contact_no, rating, total_reviews, facilities
```

#### **doctor**

```sql
doctor_id, name, specialization, hospital_id, contact_no
```

#### **disease**

```sql
disease_id, name, description
```

#### **doctor_disease_expertise**

```sql
expertise_id, doctor_id, disease_id, experience_years,
success_rate, total_cases
```

#### **appointment_slots**

```sql
slot_id, doctor_id, slot_date, slot_time,
duration_minutes, is_booked, patient_id
```

---

### MongoDB Collections

#### **medical_knowledge**

```javascript
{
  disease: "Migraine",
  symptoms: [
    {name: "headache", weight: 1.0, severity: "high"},
    {name: "nausea", weight: 0.7, severity: "medium"}
  ],
  specialist_requirements: {
    primary: "Neurologist",
    urgent_care_eligible: false
  }
}
```

#### **disease_followup_questions**

```javascript
{
  disease: "Migraine",
  follow_up_questions: [
    {
      question: "Does light or sound make the pain worse?",
      symptom_mapped: "photophobia",
      weight: 0.3,
      type: "yes_no"
    }
  ]
}
```

#### **patient_prescriptions** (GridFS)

```javascript
{
  patient_id: 1001,
  file_id: "gridfs_file_id",
  filename: "prescription.pdf",
  upload_date: ISODate(),
  ocr_data: {
    doctor_name: "Dr. Smith",
    medicines: [...]
  }
}
```

---

## 🔒 Security Considerations

### Implemented Security Features

1. **Password-Protected Sharing**: Optional password protection for shared medical records
2. **Time-Limited Links**: Shareable links automatically expire
3. **GridFS Storage**: Secure file storage for prescriptions
4. **Input Sanitization**: SQL injection prevention via parameterized queries

### Recommendations for Production

1. **Add Authentication**: Implement JWT or OAuth2 for user sessions
2. **HTTPS Only**: Use SSL/TLS certificates
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Enhanced server-side validation
5. **Encryption**: Encrypt sensitive patient data at rest
6. **Audit Logs**: Track all data access and modifications
7. **HIPAA Compliance**: Implement full healthcare data compliance measures

---

## 🚀 Future Enhancements

- [ ] Real-time chat with doctors
- [ ] Video consultation integration
- [ ] Mobile app (React Native)
- [ ] AI-powered health risk prediction
- [ ] Integration with wearable devices
- [ ] Multi-language support
- [ ] Insurance claim automation
- [ ] Pharmacy integration for medicine delivery
- [ ] AI chatbot for preliminary diagnosis
- [ ] Telemedicine features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - _Initial work_ - [GitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Tesseract OCR by Google
- Flask framework by Pallets
- MongoDB for flexible data storage
- Google Maps Platform
- All contributors and testers

---

## 📞 Support

For support, email: support@mediquery.com (update with your email)

Or open an issue on [GitHub Issues](https://github.com/yourusername/mediquery/issues)

---

<div align="center">

**Made with ❤️ for better healthcare accessibility**

[⬆ Back to Top](#-mediquery---smart-medical-consultation-system)

</div>
