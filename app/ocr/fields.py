# app/ocr/fields.py
import re

def normalize_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_fields(text):
    text = normalize_text(text)
    data = {}

    # Name
    name_match = re.search(r'([A-Z]{2,}, [A-Z ]{2,})', text)
    if name_match:
        data['full_name'] = name_match.group(1)

    # DOB
    dob_match = re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
    if dob_match:
        data['date_of_birth'] = dob_match.group(0)

    # NIN
    nin_match = re.search(r'\d{11,}', text)
    if nin_match:
        data['nin'] = nin_match.group(0)

    # Passport
    passport_match = re.search(r'\b[A-Z]{1}\d{7}\b', text)
    if passport_match:
        data['passport_number'] = passport_match.group(0)

    # Voter VIN
    vin_match = re.search(r'VIN[: ]+([A-Z0-9\s]+)', text, re.I)
    if vin_match:
        data['voter_id'] = vin_match.group(1).replace(" ", "")

    return data