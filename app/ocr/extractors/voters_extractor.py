# app/ocr/extractors/voters_extractor.py
from .base_extractor import BaseExtractor
import re
from typing import Dict, Any

class VotersCardExtractor(BaseExtractor):
    """Extractor for Nigerian Voter's Card with corrected DOB handling"""

    def extract(self, text: str) -> Dict[str, Any]:
        fields = {}

        # --- Clean text lines ---
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        full_text = ' '.join(lines)

        # --- Name extraction ---
        name_line = None
        for line in lines:
            if ',' in line and re.search(r'[A-Z]{3,}', line):
                name_line = line
                break

        if name_line:
            name_line = re.sub(r'^[^A-Z]+', '', name_line)  # remove leading garbage
            match = re.search(r'([A-Z]+),\s*([A-Z\s]+)', name_line)
            if match:
                surname = re.sub(r'[^A-Z]', '', match.group(1))
                given_names = re.sub(r'[^A-Z\s]', '', match.group(2))
                fields["surname"] = surname.title()
                fields["given_names"] = given_names.title()
                name_parts = given_names.split()
                fields["first_name"] = name_parts[0].title() if name_parts else ""
                fields["middle_name"] = " ".join(name_parts[1:]).title() if len(name_parts) > 1 else ""
                fields["full_name"] = f"{fields['surname']} {fields['given_names']}"

        # --- DOB extraction ---
        dob = None
        for i, line in enumerate(lines):
            if 'BIRTH' in line.upper():
                # check next 2 lines for date
                for j in range(1, 3):
                    if i + j < len(lines):
                        candidate = lines[i + j].strip()
                        candidate_clean = re.sub(r'[^0-9\-\/]', '', candidate)
                        dob_match = re.search(r'(\d{1,3})[^\d]?(\d{1,2})[^\d]?(\d{4})', candidate_clean)
                        if dob_match:
                            day_raw, month, year = dob_match.groups()
                            # Take last 2 digits if OCR added extra digits (e.g., 145 -> 15)
                            day_digits = ''.join(filter(str.isdigit, day_raw))
                            day = day_digits[-2:] if len(day_digits) > 2 else day_digits
                            day = str(int(day)).zfill(2)
                            month = str(int(month)).zfill(2)
                            dob = f"{day}-{month}-{year}"
                            break
                if dob:
                    break

        # fallback: search full text if no context
        if not dob:
            candidate_clean = re.sub(r'[^0-9\-\/]', '', full_text)
            dob_match = re.search(r'(\d{1,3})[^\d]?(\d{1,2})[^\d]?(\d{4})', candidate_clean)
            if dob_match:
                day_raw, month, year = dob_match.groups()
                day_digits = ''.join(filter(str.isdigit, day_raw))
                day = day_digits[-2:] if len(day_digits) > 2 else day_digits
                day = str(int(day)).zfill(2)
                month = str(int(month)).zfill(2)
                dob = f"{day}-{month}-{year}"

        if dob:
            fields["date_of_birth"] = dob

        # --- Gender extraction ---
        if 'FEMALE' in full_text.upper():
            fields["gender"] = "Female"
        elif 'MALE' in full_text.upper():
            fields["gender"] = "Male"

        # --- Occupation extraction ---
        occ_match = re.search(r'OCCUPATION[:\s]*([A-Z]+)', full_text, re.I)
        if occ_match:
            fields["occupation"] = occ_match.group(1).title()

        # --- Address ---
        addr_match = re.search(r'([A-Z]+!?\s+ROAD\s+[A-Z]+\s+[A-Z]+)', full_text, re.I)
        if addr_match:
            address = addr_match.group(1).replace('!', '').strip()
            fields["address"] = address.title()

        # --- State ---
        if 'DELTA' in full_text.upper():
            fields["state"] = "Delta"

        # --- Code ---
        code_match = re.search(r'CODE[:\s]*["]?([0-9.\-]+)', full_text, re.I)
        if code_match:
            fields["code"] = code_match.group(1).strip()

        return fields






















# # app/ocr/extractors/voters_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class VotersCardExtractor(BaseExtractor):
#     """Extractor for Nigerian Voter's Card - Robust pattern matching"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         """
#         Extract all fields from Nigerian Voter's Card
#         Designed to handle poor OCR quality
#         """
#         fields = {}
        
#         # Split into lines
#         lines = text.split('\n')
#         clean_lines = []
        
#         # Keep lines that might contain useful information
#         for line in lines:
#             line = line.strip()
#             if line and len(line) > 2:
#                 # Remove lines that are just symbols
#                 if re.search(r'[A-Z0-9]', line):
#                     clean_lines.append(line)
        
#         full_text = ' '.join(clean_lines)
        
#         print("=" * 50)
#         print("VOTER'S CARD EXTRACTION")
#         print("=" * 50)
#         for line in clean_lines:
#             print(line)
#         print("=" * 50)
        
#         # 1. VIN (Voter Identification Number)
#         # Look for patterns like "Nica? 2000: 0" -> should be INC/INEC number
#         vin_candidates = re.findall(r'([A-Z]{2,3}[^\w]*\d{4}[^\w]*\d{4}[^\w]*\d{4}[^\w]*\d{3,4})', full_text, re.I)
#         if vin_candidates:
#             vin = vin_candidates[0]
#             # Clean it up
#             vin = re.sub(r'[^\w]', '', vin)
#             fields["vin"] = vin.upper()
#         else:
#             # Try alternative pattern
#             vin_match = re.search(r'([A-Z]{2,4}[\s-]*\d{4}[\s-]*\d{4}[\s-]*\d{4}[\s-]*\d{3,4})', full_text, re.I)
#             if vin_match:
#                 vin = vin_match.group(1)
#                 vin = re.sub(r'[\s-]', '', vin)
#                 fields["vin"] = vin.upper()
        
#         # 2. Extract Name - Look for "SURNAME, FIRSTNAME MIDDLENAME"
#         # From your text: "INEBUKE, RACHEL ONYEAMACHI"
#         name_match = re.search(r'([A-Z]+),\s*([A-Z]+\s+[A-Z]+(?:\s+[A-Z]+)?)', full_text, re.I)
#         if name_match:
#             surname = name_match.group(1).strip()
#             given_names = name_match.group(2).strip()
            
#             # Clean up common OCR errors
#             surname = re.sub(r'[^A-Z]', '', surname)
#             given_names = re.sub(r'[^A-Z\s]', '', given_names)
            
#             fields["surname"] = surname.title()
#             fields["given_names"] = given_names.title()
            
#             # Split given names
#             name_parts = given_names.split()
#             if name_parts:
#                 fields["first_name"] = name_parts[0].title()
#                 if len(name_parts) > 1:
#                     fields["middle_name"] = " ".join(name_parts[1:]).title()
            
#             fields["full_name"] = f"{fields['surname']} {fields['given_names']}"
        
#         # 3. Date of Birth
#         # Look for pattern like "145-03-1995" -> should be "15-03-1995"
#         dob_match = re.search(r'(\d{1,3})[^\d]*(\d{1,2})[^\d]*(\d{4})', full_text)
#         if dob_match:
#             day, month, year = dob_match.groups()
            
#             # Fix common OCR error: "145" -> "15"
#             if len(day) > 2:
#                 day = day[-2:]  # Take last 2 digits
            
#             # Ensure proper formatting
#             day = day.zfill(2)
#             month = month.zfill(2)
            
#             # Validate
#             if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
#                 fields["date_of_birth"] = f"{day}-{month}-{year}"
        
#         # 4. Gender
#         if 'FEMALE' in full_text.upper() or ' F ' in full_text:
#             fields["gender"] = "Female"
#         elif 'MALE' in full_text.upper() or ' M ' in full_text:
#             fields["gender"] = "Male"
        
#         # 5. Occupation
#         occ_match = re.search(r'OCCUPATION[:\s]*([A-Z]+)', full_text, re.I)
#         if occ_match:
#             fields["occupation"] = occ_match.group(1).title()
#         elif 'HER' in full_text.upper():
#             fields["occupation"] = "Her"  # From your text
        
#         # 6. Address
#         # Look for "NNEBIS! ROAD ASABE DELTA"
#         addr_match = re.search(r'([A-Z]+[!]?\s+ROAD\s+[A-Z]+\s+[A-Z]+)', full_text, re.I)
#         if addr_match:
#             address = addr_match.group(1)
#             # Clean up
#             address = address.replace('!', '').strip()
#             fields["address"] = address.title()
        
#         # 7. State
#         if 'DELTA' in full_text.upper():
#             fields["state"] = "Delta"
        
#         # 8. LGA (Local Government Area)
#         # Look for "DELIM: DELTA IKA SOUTH"
#         lga_match = re.search(r'DELIM[:\s]*[A-Z]+\s+([A-Z]+\s+[A-Z]+)', full_text, re.I)
#         if lga_match:
#             lga = lga_match.group(1).strip()
#             fields["lga"] = lga.title()
        
#         # 9. Code/Ward
#         code_match = re.search(r'CODE[:\s]*["]?([0-9.\-]+)', full_text, re.I)
#         if code_match:
#             fields["code"] = code_match.group(1)
        
#         # 10. NIN
#         nin_match = re.search(r'NIN[:\s]*(\d{3,})', full_text, re.I)
#         if nin_match:
#             nin = nin_match.group(1)
#             fields["nin"] = nin
        
#         # 11. Polling Unit
#         pu_match = re.search(r'PU[:\s]*([A-Z0-9\s]+)', full_text, re.I)
#         if pu_match:
#             fields["polling_unit"] = pu_match.group(1).strip()
        
#         return fields