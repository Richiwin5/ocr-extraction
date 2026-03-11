# app/ocr/extractors/nin_extractor.py
from .base_extractor import BaseExtractor
import re
from typing import Dict, Any

class NINExtractor(BaseExtractor):
    """Extractor for Nigerian NIN (National Identification Number)"""
    
    def extract(self, text: str) -> Dict[str, Any]:
        text = self.clean_text(text)
        fields = {}
        
        # NIN Number (11 digits)
        nin_patterns = [
            r'NIN[:\s]*(\d{11})',
            r'National Identification Number[:\s]*(\d{11})',
            r'ID[:\s]*(\d{11})',
            r'(\d{11})',
        ]
        
        for pattern in nin_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                potential_nin = match.group(1)
                if len(potential_nin) == 11 and potential_nin.isdigit():
                    fields["nin"] = potential_nin
                    break
        
        # Full Name
        name_patterns = [
            r'Surname[:\s]*([A-Z\s]+)',
            r'First[_\s]*Name[:\s]*([A-Z\s]+)',
            r'Middle[_\s]*Name[:\s]*([A-Z\s]+)',
        ]
        
        for pattern in name_patterns:
            if 'surname' not in fields and 'Surname' in pattern:
                match = re.search(pattern, text, re.I)
                if match:
                    fields["surname"] = match.group(1).strip().title()
            elif 'first' in pattern.lower() and 'first_name' not in fields:
                match = re.search(pattern, text, re.I)
                if match:
                    fields["first_name"] = match.group(1).strip().title()
            elif 'middle' in pattern.lower():
                match = re.search(pattern, text, re.I)
                if match:
                    fields["middle_name"] = match.group(1).strip().title()
        
        # Date of Birth
        dob_patterns = [
            r'Date[_\s]*of[_\s]*Birth[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(\d{2}[-/]\d{2}[-/]\d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                dob = match.group(1)
                dob = re.sub(r'[/]', '-', dob)
                fields["date_of_birth"] = dob
                break
        
        # Gender
        gender_match = re.search(r'Gender[:\s]*(MALE|FEMALE|M|F)', text, re.I)
        if gender_match:
            fields["gender"] = gender_match.group(1).upper()
        
        # Address
        addr_match = re.search(r'Address[:\s]*([^0-9]+(?:[0-9]+[^0-9]+)*)', text, re.I)
        if addr_match:
            fields["address"] = addr_match.group(1).strip().title()
        
        # Phone Number
        phone_match = re.search(r'Phone[:\s]*(\+?\d{11,14})', text, re.I)
        if phone_match:
            fields["phone_number"] = phone_match.group(1)
        
        # Build full name from components
        if "surname" in fields and "first_name" in fields:
            middle = f" {fields['middle_name']}" if "middle_name" in fields else ""
            fields["full_name"] = f"{fields['surname']} {fields['first_name']}{middle}"
        
        return fields