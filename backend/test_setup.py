import pytesseract
import pdf2image
from PIL import Image
import io

print("=" * 50)
print("Testing OCR Setup")
print("=" * 50)

# Test 1: Tesseract
print("\n1. Testing Tesseract OCR...")
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Create simple test image
    img = Image.new('RGB', (300, 100), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), "Test Prescription", fill='black')
    
    text = pytesseract.image_to_string(img)
    print(f"✅ Tesseract working! Extracted: '{text.strip()}'")
except Exception as e:
    print(f"❌ Tesseract error: {e}")

# Test 2: Poppler
print("\n2. Testing Poppler...")
try:
    poppler_path = r'C:\Users\akshi\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin'
    print(f"✅ Poppler path configured: {poppler_path}")
except Exception as e:
    print(f"❌ Poppler error: {e}")

# Test 3: MongoDB
print("\n3. Testing MongoDB connection...")
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mediquery_nlp"]
    print(f"✅ MongoDB connected! Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"❌ MongoDB error: {e}")

print("\n" + "=" * 50)
print("Setup test complete!")
print("=" * 50)