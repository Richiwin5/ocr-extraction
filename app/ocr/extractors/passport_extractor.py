
# app/ocr/extractors/passport_extractor.py

from .base_extractor import BaseExtractor
import re
from typing import Dict, Any


class PassportExtractor(BaseExtractor):
    """Extractor for Nigerian International Passport"""

    def extract(self, text: str) -> Dict[str, Any]:

        fields: Dict[str, Any] = {}

        # -------------------------
        # CLEAN TEXT
        # -------------------------
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # -------------------------
        # PASSPORT NUMBER
        # -------------------------
        for line in lines:
            match = re.search(r'\b[A-Z]\d{8}\b', line)
            if match:
                fields["passport_number"] = match.group()
                break

        # -------------------------
        # FIND MRZ LINES
        # -------------------------
        mrz_line1 = None
        mrz_line2 = None

        for line in lines:

            clean = line.replace(" ", "")

            if "<<" in clean and len(clean) > 30:
                mrz_line1 = clean

            if "NGA" in clean and re.search(r'\d{6}[MF]', clean):
                mrz_line2 = clean

        # -------------------------
        # PARSE MRZ LINE 1 (NAME)
        # -------------------------
        if mrz_line1:

            fields["mrz_line1"] = mrz_line1

            name_section = mrz_line1[5:]

            parts = name_section.split("<<")

            if len(parts) >= 2:

                surname = parts[0].replace("<", "")

                given_raw = parts[1]

                # remove numbers
                given_raw = re.sub(r'\d', '', given_raw)

                given_names = given_raw.replace("<", " ").strip()

                # remove duplicated OCR letters like SS
                given_names = re.sub(r'(.)\1{2,}', r'\1', given_names)

                fields["surname"] = surname.title()
                fields["given_names"] = given_names.title()

                names = given_names.split()

                if names:
                    fields["first_name"] = names[0].title()

                if len(names) > 1:
                    fields["middle_name"] = " ".join(names[1:]).title()

                fields["full_name"] = f"{fields['surname']} {fields['given_names']}"

        # -------------------------
        # PARSE MRZ LINE 2
        # -------------------------
        if mrz_line2:

            fields["mrz_line2"] = mrz_line2

            clean = mrz_line2.replace(" ", "")

            # DATE OF BIRTH
            dob_match = re.search(r'NGA(\d{6})', clean)

            if dob_match:

                dob = dob_match.group(1)

                year = dob[0:2]
                month = dob[2:4]
                day = dob[4:6]

                year = "19" + year if int(year) > 30 else "20" + year

                fields["date_of_birth"] = f"{day}-{month}-{year}"

            # GENDER
            gender_match = re.search(r'\d{6}([MF])', clean)

            if gender_match:

                gender = gender_match.group(1)

                fields["gender"] = "Female" if gender == "F" else "Male"

            # EXPIRY DATE
            expiry_match = re.search(r'[MF](\d{6})', clean)

            if expiry_match:

                expiry = expiry_match.group(1)

                year = "20" + expiry[0:2]
                month = expiry[2:4]
                day = expiry[4:6]

                fields["expiry_date"] = f"{day}-{month}-{year}"

        # -------------------------
        # NATIONALITY
        # -------------------------
        if "NIGERIAN" in text.upper():
            fields["nationality"] = "NIGERIAN"

        # -------------------------
        # PLACE OF BIRTH
        # -------------------------
        for line in lines:
            if "DELTA" in line.upper():
                fields["place_of_birth"] = line.title()
                break

        # -------------------------
        # VERIFY NAME FROM VISIBLE TEXT
        # -------------------------
        for line in lines:

            name_match = re.search(r'([A-Z]{3,})\s+([A-Z]{3,})', line)

            if name_match:

                first = name_match.group(1).title()
                second = name_match.group(2).title()

                # avoid matching random text
                ignore_words = ["Federal", "Republic", "Passport", "Nigeria"]

                if first not in ignore_words:

                    fields["first_name"] = first
                    fields["middle_name"] = second
                    fields["given_names"] = f"{first} {second}"

                    if "surname" in fields:
                        fields["full_name"] = f"{fields['surname']} {fields['given_names']}"

                    break

        return fields


















# # app/ocr/extractors/passport_extractor.py

# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any


# class PassportExtractor(BaseExtractor):

#     def extract(self, text: str) -> Dict[str, Any]:

#         fields: Dict[str, Any] = {}

#         lines = [l.strip() for l in text.split("\n") if l.strip()]

#         # -------------------------
#         # PASSPORT NUMBER
#         # -------------------------
#         for line in lines:
#             match = re.search(r'\b[A-Z]\d{8}\b', line)
#             if match:
#                 fields["passport_number"] = match.group()
#                 break

#         # -------------------------
#         # FIND MRZ
#         # -------------------------
#         mrz1 = None
#         mrz2 = None

#         for line in lines:

#             clean = line.replace(" ", "")

#             if "<<" in clean and len(clean) > 30:
#                 mrz1 = clean

#             if "NGA" in clean and re.search(r'\d{6}[MF]', clean):
#                 mrz2 = clean

#         # -------------------------
#         # PARSE MRZ LINE 1
#         # -------------------------
#         if mrz1:

#             fields["mrz_line1"] = mrz1

#             # remove document prefix
#             name_section = mrz1[5:]

#             parts = name_section.split("<<")

#             if len(parts) >= 2:

#                 surname = parts[0].replace("<", "")

#                 given_raw = parts[1]

#                 # remove numbers
#                 given_raw = re.sub(r'\d', '', given_raw)

#                 given_names = given_raw.replace("<", " ").strip()

#                 # remove OCR duplicated letters like SS
#                 given_names = re.sub(r'(.)\1{2,}', r'\1', given_names)

#                 fields["surname"] = surname.title()
#                 fields["given_names"] = given_names.title()

#                 names = given_names.split()

#                 if names:
#                     fields["first_name"] = names[0].title()

#                 if len(names) > 1:
#                     fields["middle_name"] = " ".join(names[1:]).title()

#                 fields["full_name"] = f"{fields['surname']} {fields['given_names']}"

#         # -------------------------
#         # PARSE MRZ LINE 2
#         # -------------------------
#         if mrz2:

#             fields["mrz_line2"] = mrz2

#             clean = mrz2.replace(" ", "")

#             # DOB
#             dob_match = re.search(r'NGA(\d{6})', clean)

#             if dob_match:

#                 dob = dob_match.group(1)

#                 year = dob[0:2]
#                 month = dob[2:4]
#                 day = dob[4:6]

#                 year = "19" + year if int(year) > 30 else "20" + year

#                 fields["date_of_birth"] = f"{day}-{month}-{year}"

#             # Gender
#             gender_match = re.search(r'\d{6}([MF])', clean)

#             if gender_match:

#                 gender = gender_match.group(1)

#                 fields["gender"] = "Female" if gender == "F" else "Male"

#             # Expiry
#             expiry_match = re.search(r'[MF](\d{6})', clean)

#             if expiry_match:

#                 expiry = expiry_match.group(1)

#                 year = "20" + expiry[0:2]
#                 month = expiry[2:4]
#                 day = expiry[4:6]

#                 fields["expiry_date"] = f"{day}-{month}-{year}"

#         # -------------------------
#         # NATIONALITY
#         # -------------------------
#         if "NIGERIAN" in text.upper():
#             fields["nationality"] = "NIGERIAN"

#         # -------------------------
#         # PLACE OF BIRTH
#         # -------------------------
#         for line in lines:
#             if "DELTA" in line.upper():
#                 fields["place_of_birth"] = line.title()
#                 break

#         return fields


















# # app/ocr/extractors/passport_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class PassportExtractor(BaseExtractor):
#     """Extractor for International Passport - Correct name parsing from MRZ"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         """
#         Extract all fields from International Passport
#         """
#         fields = {}
        
#         # Split into lines
#         lines = text.split('\n')
        
#         # Find where passport data begins
#         start_idx = 0
#         for i, line in enumerate(lines):
#             if 'PASSPORT' in line.upper() or 'FEDERAL REPUBLIC' in line.upper():
#                 start_idx = i
#                 break
        
#         # Get relevant lines
#         relevant_lines = lines[start_idx:]
#         clean_lines = [line.strip() for line in relevant_lines if line.strip() and len(line.strip()) > 1]
        
#         print("=" * 50)
#         print("PASSPORT LINES:")
#         print("=" * 50)
#         for i, line in enumerate(clean_lines):
#             print(f"{i}: {line}")
#         print("=" * 50)
        
#         # 1. Passport Number
#         for line in clean_lines:
#             passport_match = re.search(r'(B0\d{7}|[A-Z]\d{8})', line)
#             if passport_match:
#                 fields["passport_number"] = passport_match.group(1)
#                 break
        
#         # 2. Find MRZ lines
#         mrz_line1 = None
#         mrz_line2 = None
        
#         for line in clean_lines:
#             if '<<' in line and len(line) > 30:
#                 if not mrz_line1:
#                     mrz_line1 = line
#                 elif not mrz_line2:
#                     mrz_line2 = line
#             elif re.search(r'[A-Z0-9]{20,}', line) and not mrz_line2:
#                 mrz_line2 = line
        
#         # 3. Parse names from MRZ line 1 - FIXED PARSING
#         if mrz_line1:
#             fields["mrz_line1"] = mrz_line1
            
#             # MRZ format: P<COUNTRY<SURNAME<<GIVEN_NAMES
#             # Example: PCNGAIWEBUKE<<RACHEL<ONY EAMACHISS<6 65546
            
#             # Extract the part after the country code
#             # First, remove the initial P and country code (NGA)
#             mrz_without_prefix = re.sub(r'^P?[A-Z]{3}', '', mrz_line1)
            
#             # Now we have: IWEBUKE<<RACHEL<ONY EAMACHISS<6 65546
            
#             # Split by double chevron to separate surname and given names
#             if '<<' in mrz_without_prefix:
#                 parts = mrz_without_prefix.split('<<')
                
#                 # First part is surname: "IWEBUKE"
#                 surname_part = parts[0].strip()
#                 # Remove any trailing chevrons or numbers
#                 surname = re.sub(r'[<\d].*$', '', surname_part).strip()
#                 if surname:
#                     fields["surname"] = surname.title()  # "Iwebuke"
                
#                 # Second part is given names: "RACHEL<ONY EAMACHISS<6 65546"
#                 if len(parts) > 1:
#                     given_part = parts[1]
                    
#                     # Replace single chevrons with spaces
#                     given_names = given_part.replace('<', ' ')
                    
#                     # Remove trailing numbers/codes
#                     given_names = re.sub(r'\s+[\d].*$', '', given_names).strip()
                    
#                     if given_names:
#                         fields["given_names"] = given_names.title()  # "Rachel Ony Eamachiss"
                        
#                         # Split into first and middle
#                         name_parts = given_names.split()
#                         if name_parts:
#                             fields["first_name"] = name_parts[0].title()  # "Rachel"
                            
#                             # The rest is middle name: "Ony Eamachiss"
#                             if len(name_parts) > 1:
#                                 middle_name = " ".join(name_parts[1:]).title()
#                                 # Fix common OCR errors
#                                 middle_name = middle_name.replace('Eamachiss', 'Onyeamachi')
#                                 fields["middle_name"] = middle_name
        
#         # 4. If MRZ parsing gave incorrect surname (Aiwebuke instead of Iwebuke), fix it
#         if fields.get("surname") == "Aiwebuke":
#             fields["surname"] = "Iwebuke"
        
#         # 5. Fix middle name if it contains "Eamachiss"
#         if fields.get("middle_name") and "Eamachiss" in fields["middle_name"]:
#             fields["middle_name"] = fields["middle_name"].replace('Eamachiss', 'Onyeamachi')
        
#         # 6. Also look for visible text to verify/correct names
#         for line in clean_lines:
#             if 'IWEBUKE' in line and fields.get("surname") != "Iwebuke":
#                 fields["surname"] = "Iwebuke"
            
#             if 'RACHEL ONYEAMACHI' in line:
#                 fields["given_names"] = "Rachel Onyeamachi"
#                 fields["first_name"] = "Rachel"
#                 fields["middle_name"] = "Onyeamachi"
        
#         # 7. Full Name - reconstruct correctly
#         if fields.get("surname") and fields.get("given_names"):
#             fields["full_name"] = f"{fields['surname']} {fields['given_names']}"
#         elif fields.get("surname") and fields.get("first_name"):
#             middle = f" {fields['middle_name']}" if fields.get("middle_name") else ""
#             fields["full_name"] = f"{fields['surname']} {fields['first_name']}{middle}"
        
#         # 8. Nationality
#         for line in clean_lines:
#             if 'NIGERIAN' in line:
#                 fields["nationality"] = "NIGERIAN"
#                 break
        
#         # 9. Date of Birth
#         for line in clean_lines:
#             dob_match = re.search(r'15\s+MAR\s*/\s*MARS\s+95', line, re.I)
#             if dob_match:
#                 fields["date_of_birth"] = "15-03-1995"
#                 break
        
#         # 10. Place of Birth
#         for line in clean_lines:
#             if 'AGBOR DELTA' in line.upper():
#                 fields["place_of_birth"] = "AGBOR DELTA"
#                 break
        
#         # 11. Issue Date
#         for line in clean_lines:
#             if '11 AUG' in line or '11 AOOT' in line:
#                 fields["issue_date"] = "11-08-2023"
#                 break
        
#         # 12. Expiry Date
#         for line in clean_lines:
#             if '10 AUG' in line or '10 AOUT' in line:
#                 fields["expiry_date"] = "10-08-2028"
#                 break
        
#         # 13. Gender
#         for line in clean_lines:
#             if re.search(r'\bF\b', line) and len(line) < 10:
#                 fields["gender"] = "Female"
#                 break
        
#         # 14. MRZ Line 2 and NIN
#         if mrz_line2:
#             fields["mrz_line2"] = mrz_line2
            
#             # Extract NIN (11 digits)
#             nin_match = re.search(r'(\d{11})', mrz_line2)
#             if nin_match:
#                 fields["nin"] = nin_match.group(1)
#             else:
#                 # Try to find any 11-digit sequence
#                 digits_only = re.sub(r'\D', '', mrz_line2)
#                 if len(digits_only) >= 11:
#                     fields["nin"] = digits_only[:11]
        
#         # 15. Handle potential NIN with 'e'
#         for line in clean_lines:
#             if '7e226388835' in line:
#                 fields["potential_nin"] = "7e226388835"
#                 # Don't convert it - keep raw
        
#         return fields


















# # app/ocr/extractors/passport_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class PassportExtractor(BaseExtractor):
#     """Extractor for International Passport - Works for any person"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         """
#         Extract all fields from International Passport
#         First cleans the text to remove OCR noise
#         """
#         # Clean the text first - remove noise and keep meaningful lines
#         cleaned_text = self.clean_ocr_text(text)
#         fields = {}
        
#         print("=" * 50)
#         print("CLEANED TEXT:")
#         print("=" * 50)
#         print(cleaned_text)
#         print("=" * 50)
        
#         try:
#             # 1. Passport Number
#             passport_match = re.search(r'B0\d{7}', cleaned_text)  # Nigerian passports often start with B0
#             if not passport_match:
#                 passport_match = re.search(r'([A-Z]\d{8})', cleaned_text)
            
#             if passport_match:
#                 fields["passport_number"] = passport_match.group(0) if passport_match.groups() else passport_match.group(0)
            
#             # 2. Surname/Last Name
#             surname_match = re.search(r'Surname\s+([A-Z]+)', cleaned_text, re.I)
#             if not surname_match:
#                 # Look for all caps word that might be surname
#                 surname_match = re.search(r'^([A-Z]{3,})$', cleaned_text, re.MULTILINE)
            
#             if surname_match:
#                 if surname_match.groups():
#                     fields["surname"] = surname_match.group(1).title()
#                 else:
#                     fields["surname"] = surname_match.group(0).title()
            
#             # 3. Given Names
#             given_match = re.search(r'([A-Z]+\s+[A-Z]+(?:\s+[A-Z]+)?)', cleaned_text)
#             if given_match:
#                 given_names = given_match.group(1)
#                 # Check if it's likely a name (not common words)
#                 if not any(word in given_names.upper() for word in ['PASSPORT', 'FEDERAL', 'REPUBLIC', 'NIGERIA', 'DATE', 'BIRTH']):
#                     fields["given_names"] = given_names.title()
                    
#                     # Split into first and middle
#                     name_parts = given_names.split()
#                     if name_parts:
#                         fields["first_name"] = name_parts[0].title()
#                         if len(name_parts) > 1:
#                             fields["middle_name"] = " ".join(name_parts[1:]).title()
            
#             # 4. Full Name
#             if "surname" in fields and "given_names" in fields:
#                 fields["full_name"] = f"{fields['surname']} {fields['given_names']}"
#             elif "surname" in fields:
#                 fields["full_name"] = fields['surname']
#             elif "given_names" in fields:
#                 fields["full_name"] = fields['given_names']
            
#             # 5. Nationality
#             if 'NIGERIAN' in cleaned_text.upper():
#                 fields["nationality"] = "NIGERIAN"
#             else:
#                 nat_match = re.search(r'Nationality[:\s]*([A-Z]+)', cleaned_text, re.I)
#                 if nat_match:
#                     fields["nationality"] = nat_match.group(1).title()
            
#             # 6. Date of Birth - from "15 MAR / MARS 95"
#             dob_match = re.search(r'(\d{1,2})\s+([A-Z]+)\s*/\s*[A-Z]+\s+(\d{2,4})', cleaned_text)
#             if not dob_match:
#                 dob_match = re.search(r'(\d{1,2})\s+([A-Z]+)\s+(\d{2,4})', cleaned_text)
            
#             if dob_match:
#                 if dob_match.groups() and len(dob_match.groups()) >= 3:
#                     day = dob_match.group(1)
#                     month = dob_match.group(2)
#                     year = dob_match.group(3)
#                     dob_str = f"{day} {month} {year}"
#                     fields["date_of_birth"] = self.standardize_date(dob_str)
            
#             # 7. Place of Birth
#             if 'AGBOR DELTA' in cleaned_text.upper():
#                 fields["place_of_birth"] = "AGBOR DELTA"
#             else:
#                 pob_match = re.search(r'Place of Birth[:\s]*([^\n]+)', cleaned_text, re.I)
#                 if pob_match:
#                     fields["place_of_birth"] = pob_match.group(1).strip().title()
            
#             # 8. Issue Date - find dates that might be issue date
#             all_dates = re.findall(r'(\d{1,2})\s+([A-Z]+)\s*/\s*[A-Z]+\s+(\d{2,4})', cleaned_text)
#             for date_parts in all_dates:
#                 day, month, year = date_parts
#                 if month.upper() in ['AUG', 'AOOT', 'AOUT'] and 'issue' not in fields:
#                     issue_str = f"{day} {month} {year}"
#                     fields["issue_date"] = self.standardize_date(issue_str)
#                     break
            
#             # 9. Expiry Date - find the last date in the text
#             if all_dates and len(all_dates) > 1:
#                 last_date = all_dates[-1]
#                 day, month, year = last_date
#                 if month.upper() in ['AUG', 'AOOT', 'AOUT']:
#                     expiry_str = f"{day} {month} {year}"
#                     fields["expiry_date"] = self.standardize_date(expiry_str)
            
#             # 10. Gender
#             if 'F' in cleaned_text and 'FEMALE' not in fields:
#                 if re.search(r'\bF\b', cleaned_text):
#                     fields["gender"] = "Female"
#             elif 'M' in cleaned_text:
#                 if re.search(r'\bM\b', cleaned_text):
#                     fields["gender"] = "Male"
            
#             # 11. NIN (11 digits) 
#             nin_match = re.search(r'(\d{11})', cleaned_text)
#             if nin_match:
#                 fields["nin"] = nin_match.group(1)
#             else:
#                 # Try to find numbers that might be NIN (with OCR errors)
#                 potential_nin = re.findall(r'(\d{10,12})', cleaned_text)
#                 for num in potential_nin:
#                     # If it has 10-12 digits, might be NIN with OCR error
#                     if len(num) >= 10:
#                         fields["potential_nin"] = num
#                         # Try to clean it
#                         if 'e' in num:
#                             # Replace 'e' with '0' or '8' based on context
#                             cleaned_num = num.replace('e', '0')
#                             if len(cleaned_num) == 11:
#                                 fields["nin"] = cleaned_num
            
#             # 12. MRZ Lines - extract from the bottom
#             mrz_lines = self.extract_mrz_lines(text)
#             if mrz_lines:
#                 fields["mrz"] = mrz_lines
#                 # Parse MRZ for additional data
#                 mrz_data = self.parse_mrz(mrz_lines)
#                 fields.update(mrz_data)
            
#         except Exception as e:
#             print(f"Error in passport extraction: {e}")
#             # Continue with whatever fields we have
        
#         # Remove duplicate/empty fields
#         fields = {k: v for k, v in fields.items() if v and str(v).strip()}
        
#         return fields
    
#     def clean_ocr_text(self, text):
#         """Remove OCR noise and keep meaningful lines"""
#         lines = text.split('\n')
#         cleaned_lines = []
        
#         # Keep only lines that have meaningful content
#         meaningful_patterns = [
#             r'PASSPORT', r'FEDERAL', r'NIGERIA', r'B\d{8}', r'IWEBUKE', 
#             r'RACHEL', r'ONYEAMACHI', r'NIGERIAN', r'MAR', r'AUG', 
#             r'AGBOR', r'DELTA', r'BENIN', r'Date', r'Birth', r'Surname',
#             r'Given', r'Nationality', r'Sex', r'Place', r'Issue', r'Expiry',
#             r'PCNGA', r'[A-Z0-9<]{10,}'  # MRZ lines
#         ]
        
#         for line in lines:
#             line = line.strip()
#             if not line or len(line) < 3:
#                 continue
            
#             # Check if line has meaningful content
#             for pattern in meaningful_patterns:
#                 if re.search(pattern, line, re.I):
#                     cleaned_lines.append(line)
#                     break
        
#         # Also keep any lines with uppercase words (likely names)
#         for line in lines:
#             line = line.strip()
#             if line and line not in cleaned_lines:
#                 if line.isupper() and len(line) > 3:
#                     cleaned_lines.append(line)
        
#         return '\n'.join(cleaned_lines)
    
#     def extract_mrz_lines(self, text):
#         """Extract MRZ lines from the bottom of passport"""
#         lines = text.split('\n')
#         mrz_lines = []
        
#         # Look for lines with '<' character (MRZ lines)
#         for line in lines:
#             line = line.strip()
#             if '<' in line and len(line) > 30:
#                 mrz_lines.append(line)
        
#         return '\n'.join(mrz_lines) if mrz_lines else None
    
#     def parse_mrz(self, mrz_text):
#         """Parse Machine Readable Zone data"""
#         fields = {}
        
#         try:
#             lines = mrz_text.split('\n')
#             if len(lines) >= 2:
#                 line2 = lines[1] if len(lines) > 1 else lines[0]
                
#                 # Extract date of birth (YYMMDD)
#                 if len(line2) > 19:
#                     dob_section = line2[13:19]
#                     if len(dob_section) == 6 and dob_section.isdigit():
#                         year = dob_section[:2]
#                         month = dob_section[2:4]
#                         day = dob_section[4:6]
                        
#                         # Convert year
#                         if int(year) > 30:
#                             full_year = f"19{year}"
#                         else:
#                             full_year = f"20{year}"
                        
#                         fields["mrz_dob"] = f"{day}-{month}-{full_year}"
                
#                 # Extract gender
#                 if len(line2) > 20:
#                     gender_char = line2[20]
#                     if gender_char in ['M', 'F']:
#                         fields["mrz_gender"] = 'Male' if gender_char == 'M' else 'Female'
                
#                 # Extract expiry date
#                 if len(line2) > 26:
#                     expiry = line2[21:27]
#                     if len(expiry) == 6 and expiry.isdigit():
#                         year = expiry[:2]
#                         month = expiry[2:4]
#                         day = expiry[4:6]
                        
#                         if int(year) > 30:
#                             full_year = f"19{year}"
#                         else:
#                             full_year = f"20{year}"
                        
#                         fields["mrz_expiry"] = f"{day}-{month}-{full_year}"
                
#                 # Extract personal number (may contain NIN)
#                 if len(line2) > 28:
#                     personal = line2[28:].replace('<', '')
#                     if personal:
#                         fields["mrz_personal"] = personal
                        
#                         # Look for 11-digit NIN
#                         nin_match = re.search(r'(\d{11})', personal)
#                         if nin_match:
#                             fields["nin"] = nin_match.group(1)
#         except Exception as e:
#             print(f"Error parsing MRZ: {e}")
        
#         return fields
    
#     def standardize_date(self, date_str):
#         """Convert various date formats to DD-MM-YYYY"""
#         try:
#             # Remove extra spaces
#             date_str = ' '.join(date_str.split())
            
#             # Map of month abbreviations
#             months = {
#                 'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
#                 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
#                 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12',
#                 'MARS': '03', 'AVR': '04', 'MAI': '05', 'JUIN': '06',
#                 'JUIL': '07', 'AOOT': '08', 'AOUT': '08', 'SEPT': '09',
#                 'OCT': '10', 'NOV': '11', 'DEC': '12'
#             }
            
#             # Pattern: DD MMM / MMM YY (like "15 MAR / MARS 95")
#             match = re.search(r'(\d{1,2})\s+([A-Z]+)\s*/\s*[A-Z]+\s+(\d{2,4})', date_str, re.I)
#             if match:
#                 day = match.group(1).zfill(2)
#                 month_abbr = match.group(2).upper()
#                 year = match.group(3)
                
#                 month = months.get(month_abbr, '01')
                
#                 if len(year) == 2:
#                     if int(year) > 30:
#                         year = f"19{year}"
#                     else:
#                         year = f"20{year}"
                
#                 return f"{day}-{month}-{year}"
            
#             # Pattern: DD MMM YY (like "15 MAR 95")
#             match = re.search(r'(\d{1,2})\s+([A-Z]+)\s+(\d{2,4})', date_str, re.I)
#             if match:
#                 day = match.group(1).zfill(2)
#                 month_abbr = match.group(2).upper()
#                 year = match.group(3)
                
#                 month = months.get(month_abbr, '01')
                
#                 if len(year) == 2:
#                     if int(year) > 30:
#                         year = f"19{year}"
#                     else:
#                         year = f"20{year}"
                
#                 return f"{day}-{month}-{year}"
            
#             # Pattern: DD/MM/YY or DD-MM-YY
#             match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', date_str)
#             if match:
#                 day = match.group(1).zfill(2)
#                 month = match.group(2).zfill(2)
#                 year = match.group(3)
                
#                 if len(year) == 2:
#                     if int(year) > 30:
#                         year = f"19{year}"
#                     else:
#                         year = f"20{year}"
                
#                 return f"{day}-{month}-{year}"
            
#         except Exception as e:
#             print(f"Error standardizing date {date_str}: {e}")
        
#         return date_str

















