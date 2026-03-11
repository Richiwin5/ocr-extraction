# app/ocr/extractors/base_extractor.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import re

class BaseExtractor(ABC):
    """Base class for all document extractors"""
    
    @abstractmethod
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract fields from text"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_by_patterns(self, text: str, patterns: Dict[str, list]) -> Dict[str, Any]:
        """Extract fields using multiple patterns"""
        results = {}
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.I)
                if match:
                    if match.groups():
                        results[field] = match.group(1).strip()
                    else:
                        results[field] = match.group(0).strip()
                    break
        
        return results
















# # app/ocr/extractors/base_extractor.py
# from abc import ABC, abstractmethod
# from typing import Dict, Any
# import re

# class BaseExtractor(ABC):
#     """Base class for all document extractors"""
    
#     @abstractmethod
#     def extract(self, text: str) -> Dict[str, Any]:
#         """Extract fields from text"""
#         pass
    
#     def clean_text(self, text: str) -> str:
#         """Clean and normalize text"""
#         # Remove extra whitespace
#         text = ' '.join(text.split())
#         return text
    
#     def extract_by_patterns(self, text: str, patterns: Dict[str, list]) -> Dict[str, Any]:
#         """Extract fields using multiple patterns"""
#         results = {}
        
#         for field, pattern_list in patterns.items():
#             for pattern in pattern_list:
#                 match = re.search(pattern, text, re.I)
#                 if match:
#                     if match.groups():
#                         results[field] = match.group(1).strip()
#                     else:
#                         results[field] = match.group(0).strip()
#                     break
        
#         return results

# # app/ocr/extractors/voters_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class VotersCardExtractor(BaseExtractor):
#     """Extractor for Nigerian Voter's Card"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         text = self.clean_text(text)
#         fields = {}
        
#         # VIN (Voter Identification Number)
#         vin_patterns = [
#             r'VIN[:\s]*([A-Z0-9]{19})',
#             r'Voter[_\s]*ID[:\s]*([A-Z0-9]{19})',
#             r'([A-Z0-9]{2}[\s-]?[A-Z0-9]{4}[\s-]?[A-Z0-9]{4}[\s-]?[A-Z0-9]{4}[\s-]?[A-Z0-9]{4})',
#         ]
        
#         for pattern in vin_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 vin = match.group(1)
#                 vin = re.sub(r'[\s-]', '', vin)
#                 fields["vin"] = vin
#                 break
        
#         # Full Name
#         name_match = re.search(r'IWEBUKE[,\s]+([^0-9]+)', text, re.I)
#         if name_match:
#             name = name_match.group(1).strip()
#             fields["full_name"] = f"IWEBUKE {name}".title()
#         else:
#             name_match = re.search(r'NAME[:\s]*([A-Z\s,]+)', text, re.I)
#             if name_match:
#                 fields["full_name"] = name_match.group(1).strip().title()
        
#         # Split name into components
#         if "full_name" in fields:
#             name_parts = fields["full_name"].split()
#             if len(name_parts) >= 2:
#                 fields["surname"] = name_parts[0]
#                 fields["first_name"] = name_parts[1]
#                 fields["middle_name"] = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
        
#         # Date of Birth
#         dob_patterns = [
#             r'DATE[_\s]*OF[_\s]*BIRTH[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'(\d{2}[-/]\d{2}[-/]\d{4})',
#         ]
        
#         for pattern in dob_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 dob = match.group(1)
#                 dob = re.sub(r'[/]', '-', dob)
#                 fields["date_of_birth"] = dob
#                 break
        
#         # Occupation
#         occ_match = re.search(r'OCCUPATION[:\s]*([A-Z\s]+)', text, re.I)
#         if occ_match:
#             fields["occupation"] = occ_match.group(1).strip().title()
        
#         # Address
#         addr_match = re.search(r'ADDRESS[:\s]*([^0-9]+(?:[0-9]+[^0-9]+)*)', text, re.I)
#         if addr_match:
#             fields["address"] = addr_match.group(1).strip().title()
        
#         # State/LGA
#         if 'DELTA' in text.upper():
#             fields["state"] = "Delta"
        
#         lga_match = re.search(r'DELIM[:\s]*([A-Z\s]+)', text, re.I)
#         if lga_match:
#             fields["lga"] = lga_match.group(1).strip().title()
        
#         # Ward and Polling Unit
#         ward_match = re.search(r'CODE[:\s]*([0-9]{2}-[0-9]{2}-[0-9]{2,3})', text, re.I)
#         if ward_match:
#             fields["ward"] = ward_match.group(1)
        
#         pu_match = re.search(r'CODE[:\s]*([0-9]{2}-[0-9]{2}-[0-9]{2,3}\.[0-9]{3})', text, re.I)
#         if pu_match:
#             fields["polling_unit"] = pu_match.group(1)
        
#         return fields

# # app/ocr/extractors/nin_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class NINExtractor(BaseExtractor):
#     """Extractor for Nigerian NIN (National Identification Number)"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         text = self.clean_text(text)
#         fields = {}
        
#         # NIN Number (11 digits)
#         nin_patterns = [
#             r'NIN[:\s]*(\d{11})',
#             r'National Identification Number[:\s]*(\d{11})',
#             r'ID[:\s]*(\d{11})',
#             r'(\d{11})',
#         ]
        
#         for pattern in nin_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 potential_nin = match.group(1)
#                 if len(potential_nin) == 11 and potential_nin.isdigit():
#                     fields["nin"] = potential_nin
#                     break
        
#         # Full Name
#         name_patterns = [
#             r'Surname[:\s]*([A-Z\s]+)',
#             r'First[_\s]*Name[:\s]*([A-Z\s]+)',
#             r'Middle[_\s]*Name[:\s]*([A-Z\s]+)',
#         ]
        
#         for pattern in name_patterns:
#             if 'surname' not in fields and 'Surname' in pattern:
#                 match = re.search(pattern, text, re.I)
#                 if match:
#                     fields["surname"] = match.group(1).strip().title()
#             elif 'first' in pattern.lower() and 'first_name' not in fields:
#                 match = re.search(pattern, text, re.I)
#                 if match:
#                     fields["first_name"] = match.group(1).strip().title()
#             elif 'middle' in pattern.lower():
#                 match = re.search(pattern, text, re.I)
#                 if match:
#                     fields["middle_name"] = match.group(1).strip().title()
        
#         # Date of Birth
#         dob_patterns = [
#             r'Date[_\s]*of[_\s]*Birth[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'(\d{2}[-/]\d{2}[-/]\d{4})',
#         ]
        
#         for pattern in dob_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 dob = match.group(1)
#                 dob = re.sub(r'[/]', '-', dob)
#                 fields["date_of_birth"] = dob
#                 break
        
#         # Gender
#         gender_match = re.search(r'Gender[:\s]*(MALE|FEMALE|M|F)', text, re.I)
#         if gender_match:
#             fields["gender"] = gender_match.group(1).upper()
        
#         # Address
#         addr_match = re.search(r'Address[:\s]*([^0-9]+(?:[0-9]+[^0-9]+)*)', text, re.I)
#         if addr_match:
#             fields["address"] = addr_match.group(1).strip().title()
        
#         # Phone Number
#         phone_match = re.search(r'Phone[:\s]*(\+?\d{11,14})', text, re.I)
#         if phone_match:
#             fields["phone_number"] = phone_match.group(1)
        
#         # Build full name from components
#         if "surname" in fields and "first_name" in fields:
#             middle = f" {fields['middle_name']}" if "middle_name" in fields else ""
#             fields["full_name"] = f"{fields['surname']} {fields['first_name']}{middle}"
        
#         return fields

# # app/ocr/extractors/passport_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class PassportExtractor(BaseExtractor):
#     """Extractor for International Passport"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         text = self.clean_text(text)
#         fields = {}
        
#         # Passport Number
#         passport_patterns = [
#             r'Passport[_\s]*No[:\s]*([A-Z]\d{8})',
#             r'Passport[_\s]*Number[:\s]*([A-Z]\d{8})',
#             r'([A-Z]\d{8})',
#         ]
        
#         for pattern in passport_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 fields["passport_number"] = match.group(1).upper()
#                 break
        
#         # Surname
#         surname_match = re.search(r'Surname[:\s]*([A-Z\s]+)', text, re.I)
#         if surname_match:
#             fields["surname"] = surname_match.group(1).strip().title()
        
#         # Given Names
#         given_match = re.search(r'Given[_\s]*Names?[:\s]*([A-Z\s]+)', text, re.I)
#         if given_match:
#             given_names = given_match.group(1).strip().title()
#             name_parts = given_names.split()
#             if name_parts:
#                 fields["first_name"] = name_parts[0]
#                 if len(name_parts) > 1:
#                     fields["middle_name"] = " ".join(name_parts[1:])
        
#         # Nationality
#         nat_match = re.search(r'Nationality[:\s]*([A-Z\s]+)', text, re.I)
#         if nat_match:
#             fields["nationality"] = nat_match.group(1).strip().title()
        
#         # Date of Birth
#         dob_patterns = [
#             r'Date[_\s]*of[_\s]*Birth[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'(\d{2}[-/]\d{2}[-/]\d{4})',
#         ]
        
#         for pattern in dob_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 dob = match.group(1)
#                 dob = re.sub(r'[/]', '-', dob)
#                 fields["date_of_birth"] = dob
#                 break
        
#         # Place of Birth
#         pob_match = re.search(r'Place[_\s]*of[_\s]*Birth[:\s]*([A-Z\s,]+)', text, re.I)
#         if pob_match:
#             fields["place_of_birth"] = pob_match.group(1).strip().title()
        
#         # Issue Date
#         issue_match = re.search(r'Date[_\s]*of[_\s]*Issue[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
#         if issue_match:
#             fields["issue_date"] = issue_match.group(1)
        
#         # Expiry Date
#         expiry_match = re.search(r'Date[_\s]*of[_\s]*Expiry[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
#         if expiry_match:
#             fields["expiry_date"] = expiry_match.group(1)
        
#         # Gender
#         gender_match = re.search(r'Sex[:\s]*(M|F|MALE|FEMALE)', text, re.I)
#         if gender_match:
#             fields["gender"] = gender_match.group(1).upper()
        
#         # Build full name
#         if "surname" in fields and "first_name" in fields:
#             middle = f" {fields['middle_name']}" if "middle_name" in fields else ""
#             fields["full_name"] = f"{fields['surname']} {fields['first_name']}{middle}"
        
#         return fields

# # app/ocr/extractors/drivers_license_extractor.py
# from .base_extractor import BaseExtractor
# import re
# from typing import Dict, Any

# class DriversLicenseExtractor(BaseExtractor):
#     """Extractor for Driver's License"""
    
#     def extract(self, text: str) -> Dict[str, Any]:
#         text = self.clean_text(text)
#         fields = {}
        
#         # License Number
#         license_patterns = [
#             r'DL[_\s]*No[:\s]*([A-Z0-9]{12,16})',
#             r'License[_\s]*Number[:\s]*([A-Z0-9]{12,16})',
#             r'([A-Z]{2}\d{10}[A-Z0-9]?)',
#         ]
        
#         for pattern in license_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 fields["license_number"] = match.group(1).upper()
#                 break
        
#         # Full Name
#         name_match = re.search(r'Name[:\s]*([A-Z\s,]+)', text, re.I)
#         if name_match:
#             full_name = name_match.group(1).strip().title()
#             fields["full_name"] = full_name
            
#             # Try to split name
#             name_parts = full_name.split()
#             if len(name_parts) >= 2:
#                 fields["surname"] = name_parts[0]
#                 fields["first_name"] = name_parts[1]
#                 fields["middle_name"] = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
        
#         # Date of Birth
#         dob_patterns = [
#             r'Date[_\s]*of[_\s]*Birth[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
#             r'(\d{2}[-/]\d{2}[-/]\d{4})',
#         ]
        
#         for pattern in dob_patterns:
#             match = re.search(pattern, text, re.I)
#             if match:
#                 dob = match.group(1)
#                 dob = re.sub(r'[/]', '-', dob)
#                 fields["date_of_birth"] = dob
#                 break
        
#         # Issue Date
#         issue_match = re.search(r'Issue[_\s]*Date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
#         if issue_match:
#             fields["issue_date"] = issue_match.group(1)
        
#         # Expiry Date
#         expiry_match = re.search(r'Expiry[_\s]*Date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
#         if expiry_match:
#             fields["expiry_date"] = expiry_match.group(1)
        
#         # Vehicle Categories
#         cat_match = re.search(r'Categories?[:\s]*([A-Z,\s]+)', text, re.I)
#         if cat_match:
#             categories = cat_match.group(1).strip()
#             fields["vehicle_categories"] = [cat.strip() for cat in categories.split(',')]
        
#         # Blood Group
#         blood_match = re.search(r'Blood[_\s]*Group[:\s]*([A-Z0-9+-]+)', text, re.I)
#         if blood_match:
#             fields["blood_group"] = blood_match.group(1).upper()
        
#         # Address
#         addr_match = re.search(r'Address[:\s]*([^0-9]+(?:[0-9]+[^0-9]+)*)', text, re.I)
#         if addr_match:
#             fields["address"] = addr_match.group(1).strip().title()
        
#         # Height
#         height_match = re.search(r'Height[:\s]*([0-9.]+)', text, re.I)
#         if height_match:
#             fields["height"] = height_match.group(1)
        
#         return fields