# import pytesseract
# from PIL import Image
# import pdf2image
# import re
# from datetime import datetime
# import io

# # Configure Tesseract for Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Poppler path for Windows
# POPPLER_PATH = r'C:\Users\akshi\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin'

# def extract_text_from_image(image_bytes):
#     """Extract text from image using Tesseract OCR"""
#     try:
#         image = Image.open(image_bytes)
#         text = pytesseract.image_to_string(image)
#         return text
#     except Exception as e:
#         print(f"❌ OCR Error: {str(e)}")
#         return None

# def extract_text_from_pdf(pdf_bytes):
#     """Convert PDF to images and extract text"""
#     try:
#         images = pdf2image.convert_from_bytes(
#             pdf_bytes,
#             poppler_path=POPPLER_PATH
#         )
#         full_text = ""
#         for img in images:
#             text = pytesseract.image_to_string(img)
#             full_text += text + "\n"
#         return full_text
#     except Exception as e:
#         print(f"❌ PDF OCR Error: {str(e)}")
#         return None

# def parse_prescription_data(ocr_text):
#     """
#     Parse OCR text to extract structured prescription data
#     Uses regex patterns to identify medicine names, dosages, etc.
#     """
    
#     if not ocr_text:
#         return None
    
#     prescription_data = {
#         "doctor_name": None,
#         "hospital": None,
#         "patient_name": None,
#         "date": None,
#         "medicines": [],
#         "follow_up_date": None,
#         "raw_text": ocr_text
#     }
    
#     # Extract Doctor Name (patterns: Dr., Dr, Doctor)
#     doctor_match = re.search(r'(?:Dr\.?|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', ocr_text, re.IGNORECASE)
#     if doctor_match:
#         prescription_data["doctor_name"] = doctor_match.group(1).strip()
    
#     # Extract Hospital/Clinic name (look for common keywords)
#     hospital_keywords = r'(Hospital|Clinic|Medical Center|Healthcare|Nursing Home)'
#     hospital_match = re.search(r'([A-Z][a-zA-Z\s]+)(?:\s+' + hospital_keywords + ')', ocr_text)
#     if hospital_match:
#         prescription_data["hospital"] = hospital_match.group(0).strip()
    
#     # Extract Patient Name (patterns: Patient:, Name:, Mr., Mrs.)
#     patient_match = re.search(r'(?:Patient|Name|Mr\.|Mrs\.|Ms\.)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', ocr_text, re.IGNORECASE)
#     if patient_match:
#         prescription_data["patient_name"] = patient_match.group(1).strip()
    
#     # Extract Date (multiple formats)
#     date_patterns = [
#         r'(\d{2}[-/]\d{2}[-/]\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
#         r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD
#         r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})'  # 14 Jan 2026
#     ]
#     for pattern in date_patterns:
#         date_match = re.search(pattern, ocr_text, re.IGNORECASE)
#         if date_match:
#             prescription_data["date"] = date_match.group(1).strip()
#             break
    
#     # ============================================
#     # IMPROVED MEDICINE EXTRACTION
#     # ============================================
    
#     # Split text into lines for better parsing
#     lines = ocr_text.split('\n')
    
#     current_medicine = None
#     medicine_index = 0
    
#     for i, line in enumerate(lines):
#         line = line.strip()
        
#         # Pattern 1: Numbered medicine name (e.g., "1. Augmentin 625 Duo Tablet")
#         medicine_header = re.match(r'(\d+)\.\s+(.+?)\s+(Tablet|Capsule|Syrup|Injection|Suspension|Cream|Ointment)', line, re.IGNORECASE)
        
#         if medicine_header:
#             # Save previous medicine if exists
#             if current_medicine and current_medicine.get("name"):
#                 prescription_data["medicines"].append(current_medicine)
            
#             # Start new medicine
#             medicine_index = int(medicine_header.group(1))
#             medicine_name = medicine_header.group(2) + " " + medicine_header.group(3)
            
#             current_medicine = {
#                 "name": medicine_name.strip(),
#                 "dosage": "",
#                 "instructions": "",
#                 "frequency": "",
#                 "duration": ""
#             }
#             continue
        
#         # Pattern 2: Extract dosage from composition line (e.g., "Amoxycillin (500mg) + Clavulanic Acid (125mg)")
#         if current_medicine and not current_medicine.get("dosage"):
#             dosage_match = re.search(r'\((\d+\s*(?:mg|ml|g))\)', line, re.IGNORECASE)
#             if dosage_match:
#                 current_medicine["dosage"] = dosage_match.group(1).strip()
#                 continue
        
#         # Pattern 3: Extract frequency and duration (e.g., "1 tablet - 0 - 1 tablet for 5 Days")
#         if current_medicine:
#             # Duration pattern
#             duration_match = re.search(r'for\s+(\d+\s+(?:day|days|week|weeks|month|months))', line, re.IGNORECASE)
#             if duration_match and not current_medicine.get("duration"):
#                 current_medicine["duration"] = duration_match.group(1).strip()
            
#             # Frequency pattern (e.g., "1 - 0 - 1" or "twice daily")
#             freq_pattern1 = re.search(r'(\d+\s*[-–]\s*\d+\s*[-–]\s*\d+)', line)
#             freq_pattern2 = re.search(r'(once|twice|thrice|\d+\s+times?)\s+(daily|per day|a day)', line, re.IGNORECASE)
            
#             if freq_pattern1 and not current_medicine.get("frequency"):
#                 current_medicine["frequency"] = freq_pattern1.group(1).strip() + " daily"
#             elif freq_pattern2 and not current_medicine.get("frequency"):
#                 current_medicine["frequency"] = freq_pattern2.group(0).strip()
            
#             # Instructions pattern (e.g., "Instructions: Take on empty stomach")
#             inst_match = re.search(r'Instructions:\s*(.+)', line, re.IGNORECASE)
#             if inst_match:
#                 current_medicine["instructions"] = inst_match.group(1).strip()
#                 continue
            
#             # If line has "tablet when required" or "after food"
#             if re.search(r'(when required|after food|before food|empty stomach|with food)', line, re.IGNORECASE):
#                 if current_medicine["instructions"]:
#                     current_medicine["instructions"] += " " + line
#                 else:
#                     current_medicine["instructions"] = line
    
#     # Add the last medicine
#     if current_medicine and current_medicine.get("name"):
#         prescription_data["medicines"].append(current_medicine)
    
#     # ============================================
#     # FALLBACK: If no medicines found with above method, try simpler pattern
#     # ============================================
#     if not prescription_data["medicines"]:
#         print("⚠️ Primary extraction failed, trying fallback pattern...")
        
#         # Simpler pattern for medicine name + any dosage info
#         simple_pattern = r'(\d+)\.\s+([A-Z][a-zA-Z\s]+(?:Tablet|Capsule|Syrup))'
#         matches = re.finditer(simple_pattern, ocr_text, re.IGNORECASE)
        
#         for match in matches:
#             med_name = match.group(2).strip()
            
#             # Try to find dosage near this medicine
#             start_pos = match.end()
#             next_section = ocr_text[start_pos:start_pos+200]  # Look ahead 200 chars
            
#             dosage_match = re.search(r'(\d+\s*(?:mg|ml|g))', next_section)
            
#             prescription_data["medicines"].append({
#                 "name": med_name,
#                 "dosage": dosage_match.group(1) if dosage_match else "Not specified",
#                 "instructions": "See prescription",
#                 "frequency": "",
#                 "duration": ""
#             })
    
#     # Extract Follow-up date
#     followup_match = re.search(r'(?:Follow[-\s]?up|Next Visit|Review)\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})', ocr_text, re.IGNORECASE)
#     if followup_match:
#         prescription_data["follow_up_date"] = followup_match.group(1).strip()
    
#     print(f"\n✅ Extracted {len(prescription_data['medicines'])} medicines")
#     for med in prescription_data['medicines']:
#         print(f"   - {med['name']} ({med['dosage']})")
    
#     return prescription_data

# def process_prescription_file(file_bytes, filename):
#     """
#     Main function to process uploaded prescription
#     Returns structured data
#     """
    
#     file_extension = filename.lower().split('.')[-1]
    
#     # Extract text based on file type
#     if file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
#         ocr_text = extract_text_from_image(io.BytesIO(file_bytes))
#     elif file_extension == 'pdf':
#         ocr_text = extract_text_from_pdf(file_bytes)
#     else:
#         return {"error": "Unsupported file format"}
    
#     if not ocr_text:
#         return {"error": "Could not extract text from file"}
    
#     # Parse the extracted text
#     parsed_data = parse_prescription_data(ocr_text)
    
#     return parsed_data

import pytesseract
from PIL import Image
import pdf2image
import re
from datetime import datetime
import io

# Configure Tesseract for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Poppler path for Windows
POPPLER_PATH = r'C:\Users\akshi\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin'

def extract_text_from_image(image_bytes):
    """Extract text from image using Tesseract OCR"""
    try:
        image = Image.open(image_bytes)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        return None

def extract_text_from_pdf(pdf_bytes):
    """Convert PDF to images and extract text"""
    try:
        images = pdf2image.convert_from_bytes(
            pdf_bytes,
            poppler_path=POPPLER_PATH
        )
        full_text = ""
        for img in images:
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"❌ PDF OCR Error: {str(e)}")
        return None

def clean_text(text):
    """Clean OCR artifacts and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might confuse parsing
    text = re.sub(r'[^\w\s\.\-\+\(\)\/\:,\n]', '', text)
    return text.strip()

def parse_prescription_data(ocr_text):
    """
    Parse OCR text to extract structured prescription data
    Uses multiple strategies to handle different prescription formats
    """
    
    if not ocr_text:
        return None
    
    prescription_data = {
        "doctor_name": None,
        "hospital": None,
        "patient_name": None,
        "date": None,
        "medicines": [],
        "follow_up_date": None,
        "advice": None,
        "raw_text": ocr_text
    }
    
    # ============================================
    # EXTRACT HEADER INFORMATION
    # ============================================
    
    # Extract Doctor Name (multiple patterns)
    doctor_patterns = [
        r'(?:Dr\.?|Doctor)\s+([A-Z][a-zA-Z\s\.]+?)(?=\n|MBBS|M\.D|M\.S|MD|MS|Consultant)',
        r'(?:Dr\.?|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]
    for pattern in doctor_patterns:
        doctor_match = re.search(pattern, ocr_text, re.IGNORECASE)
        if doctor_match:
            prescription_data["doctor_name"] = doctor_match.group(1).strip()
            break
    
    # Extract Hospital/Clinic name
    hospital_patterns = [
        r'([A-Z][a-zA-Z\s]+(?:Hospital|Clinic|Medical Center|Healthcare|Care Clinic|Nursing Home))',
        r'Hospital:\s*(.+?)(?=\n)',
    ]
    for pattern in hospital_patterns:
        hospital_match = re.search(pattern, ocr_text, re.IGNORECASE)
        if hospital_match:
            prescription_data["hospital"] = hospital_match.group(1).strip()
            break
    
    # Extract Patient Name
    patient_patterns = [
        r'(?:Patient|Name|Mr\.|Mrs\.|Ms\.)\s*:?\s*([A-Z][a-zA-Z\s]+?)(?=\n|\d+\s*Years)',
        r'ID:\s*\d+\s*-\s*([A-Z\s]+)\s*\([MF]\)',
    ]
    for pattern in patient_patterns:
        patient_match = re.search(pattern, ocr_text, re.IGNORECASE)
        if patient_match:
            prescription_data["patient_name"] = patient_match.group(1).strip()
            break
    
    # Extract Date (multiple formats)
    date_patterns = [
        r'Date:\s*(\d{2}-\w{3}-\d{4})',  # 27-Apr-2020
        r'Date:\s*(\d{2}/\d{2}/\d{4})',  # 27/04/2020
        r'(\d{2}[-/]\d{2}[-/]\d{4})',    # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{4}[-/]\d{2}[-/]\d{2})',    # YYYY-MM-DD
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, ocr_text, re.IGNORECASE)
        if date_match:
            prescription_data["date"] = date_match.group(1).strip()
            break
    
    # Extract Follow-up date
    followup_patterns = [
        r'Follow\s*Up:\s*(\d{2}-\d{2}-\d{4})',
        r'(?:Next Visit|Review)\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})',
    ]
    for pattern in followup_patterns:
        followup_match = re.search(pattern, ocr_text, re.IGNORECASE)
        if followup_match:
            prescription_data["follow_up_date"] = followup_match.group(1).strip()
            break
    
    # Extract Advice
    advice_match = re.search(r'Advice\s*Given:\s*(.+?)(?=\n\n|Follow Up|Charts|$)', ocr_text, re.IGNORECASE | re.DOTALL)
    if advice_match:
        prescription_data["advice"] = advice_match.group(1).strip()
    
    # ============================================
    # MEDICINE EXTRACTION - MULTI-STRATEGY APPROACH
    # ============================================
    
    medicines = []
    
    # STRATEGY 1: Table format detection (like Image 2)
    # Pattern: Medicine Name | Dosage | Duration in columns
    table_section = re.search(r'Medicine Name\s+Dosage\s+Duration(.+?)(?=Advice|Follow|Charts|$)', 
                              ocr_text, re.IGNORECASE | re.DOTALL)
    
    if table_section:
        print("📊 Detected table format prescription")
        table_content = table_section.group(1)
        lines = [line.strip() for line in table_content.split('\n') if line.strip()]
        
        for line in lines:
            # Pattern: "1) TAB. DEMO MEDICINE 1    1 Morning, 1 Night    10 Days"
            # or: "TAB. MEDICINE NAME    dosage info    duration"
            parts = re.split(r'\s{2,}', line)  # Split by 2+ spaces (column separator)
            
            if len(parts) >= 2:
                # Extract medicine number and name
                med_match = re.match(r'(\d+\)?)?\s*(TAB\.|CAP\.|SYR\.|INJ\.)?\s*(.+)', parts[0], re.IGNORECASE)
                if med_match:
                    med_name = med_match.group(3).strip()
                    
                    # Extract dosage from second column
                    dosage = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Extract duration from third column
                    duration = parts[2].strip() if len(parts) > 2 else ""
                    
                    # Parse instructions from dosage
                    instructions = ""
                    if 'Before Food' in dosage:
                        instructions = "Take before food"
                    elif 'After Food' in dosage:
                        instructions = "Take after food"
                    
                    medicines.append({
                        "name": med_name,
                        "dosage": "",  # Not specified in simple format
                        "frequency": dosage.replace('(Before Food)', '').replace('(After Food)', '').strip(),
                        "duration": duration,
                        "instructions": instructions
                    })
    
    # STRATEGY 2: Numbered list format (like Image 1)
    # Pattern: "1. Augmentin 625 Duo Tablet"
    if not medicines:
        print("📝 Detected numbered list format prescription")
        
        # Find the Rx section
        rx_section = re.search(r'Rx\s*\n(.+?)(?=Investigations|Advice|Follow|$)', 
                              ocr_text, re.IGNORECASE | re.DOTALL)
        
        if rx_section:
            rx_content = rx_section.group(1)
        else:
            # Try to find medicines section by looking for numbered items with medicine keywords
            rx_content = ocr_text
        
        lines = rx_content.split('\n')
        current_medicine = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Pattern: "1. Medicine Name Tablet/Capsule/Syrup"
            medicine_header = re.match(
                r'(\d+)\.\s+(.+?)\s+(Tablet|Capsule|Syrup|Injection|Suspension|Cream|Ointment|Chewable)',
                line, re.IGNORECASE
            )
            
            if medicine_header:
                # Save previous medicine
                if current_medicine and current_medicine.get("name"):
                    medicines.append(current_medicine)
                
                # Start new medicine
                med_num = medicine_header.group(1)
                med_name = medicine_header.group(2).strip() + " " + medicine_header.group(3)
                
                current_medicine = {
                    "name": med_name,
                    "dosage": "",
                    "frequency": "",
                    "duration": "",
                    "instructions": ""
                }
                continue
            
            # Extract composition/dosage (e.g., "Amoxycillin (500mg) + Clavulanic Acid (125mg)")
            if current_medicine and not current_medicine.get("dosage"):
                dosage_match = re.search(r'\((\d+\s*(?:mg|ml|g|mcg))\)', line, re.IGNORECASE)
                if dosage_match:
                    # Get full composition
                    current_medicine["dosage"] = line.strip()
                    continue
            
            # Extract frequency and duration (e.g., "1 tablet - 0 - 1 tablet for 5 Days")
            if current_medicine:
                # Duration
                duration_match = re.search(r'for\s+(\d+\s+(?:Day|Days|Week|Weeks|Month|Months))', 
                                          line, re.IGNORECASE)
                if duration_match:
                    current_medicine["duration"] = duration_match.group(1).strip()
                
                # Frequency patterns
                freq_patterns = [
                    r'(\d+\s+tablet\s*-\s*\d+\s*-\s*\d+\s+tablet)',  # "1 tablet - 0 - 1 tablet"
                    r'(\d+\s*-\s*\d+\s*-\s*\d+)',  # "1 - 0 - 1"
                    r'(once|twice|thrice|\d+\s+times?)\s+(daily|per day|a day)',
                ]
                for pattern in freq_patterns:
                    freq_match = re.search(pattern, line, re.IGNORECASE)
                    if freq_match:
                        current_medicine["frequency"] = freq_match.group(0).strip()
                        break
                
                # Instructions
                inst_match = re.search(r'Instructions?:\s*(.+)', line, re.IGNORECASE)
                if inst_match:
                    current_medicine["instructions"] = inst_match.group(1).strip()
                elif re.search(r'(when required|after food|before food|empty stomach|with food)', 
                             line, re.IGNORECASE):
                    if current_medicine["instructions"]:
                        current_medicine["instructions"] += " " + line
                    else:
                        current_medicine["instructions"] = line
        
        # Add last medicine
        if current_medicine and current_medicine.get("name"):
            medicines.append(current_medicine)
    
    # STRATEGY 3: Simple pattern matching (fallback)
    if not medicines:
        print("🔍 Using fallback pattern matching")
        
        # Look for any medicine-like patterns
        medicine_patterns = [
            r'(\d+)\.\s+([A-Z][a-zA-Z\s\-\+\(\)]+?(?:Tablet|Capsule|Syrup|mg|ml))',
            r'(TAB\.|CAP\.|SYR\.)\s+([A-Z][a-zA-Z\s\-]+)',
        ]
        
        for pattern in medicine_patterns:
            matches = re.finditer(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                med_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                medicines.append({
                    "name": med_name.strip(),
                    "dosage": "Not specified",
                    "frequency": "As directed",
                    "duration": "As prescribed",
                    "instructions": "Follow doctor's advice"
                })
    
    prescription_data["medicines"] = medicines
    
    # ============================================
    # LOGGING
    # ============================================
    print(f"\n✅ Extraction Summary:")
    print(f"   Doctor: {prescription_data['doctor_name']}")
    print(f"   Hospital: {prescription_data['hospital']}")
    print(f"   Patient: {prescription_data['patient_name']}")
    print(f"   Date: {prescription_data['date']}")
    print(f"   Medicines: {len(medicines)}")
    for med in medicines:
        print(f"      - {med['name']}")
        if med.get('frequency'):
            print(f"        Frequency: {med['frequency']}")
        if med.get('duration'):
            print(f"        Duration: {med['duration']}")
    
    return prescription_data

def process_prescription_file(file_bytes, filename):
    """
    Main function to process uploaded prescription
    Returns structured data
    """
    
    file_extension = filename.lower().split('.')[-1]
    
    # Extract text based on file type
    if file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
        ocr_text = extract_text_from_image(io.BytesIO(file_bytes))
    elif file_extension == 'pdf':
        ocr_text = extract_text_from_pdf(file_bytes)
    else:
        return {"error": "Unsupported file format"}
    
    if not ocr_text:
        return {"error": "Could not extract text from file"}
    
    # Parse the extracted text
    parsed_data = parse_prescription_data(ocr_text)
    
    return parsed_data