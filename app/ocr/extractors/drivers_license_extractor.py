# app/ocr/extractors/drivers_license_extractor.py
from .base_extractor import BaseExtractor
import re
from typing import Dict, Any

class DriversLicenseExtractor(BaseExtractor):
    """Extractor for Driver's License"""
    
    def extract(self, text: str) -> Dict[str, Any]:
        text = self.clean_text(text)
        fields = {}
        
        # License Number
        license_patterns = [
            r'DL[_\s]*No[:\s]*([A-Z0-9]{12,16})',
            r'License[_\s]*Number[:\s]*([A-Z0-9]{12,16})',
            r'([A-Z]{2}\d{10}[A-Z0-9]?)',
        ]
        
        for pattern in license_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                fields["license_number"] = match.group(1).upper()
                break
        
        # Full Name
        name_match = re.search(r'Name[:\s]*([A-Z\s,]+)', text, re.I)
        if name_match:
            full_name = name_match.group(1).strip().title()
            fields["full_name"] = full_name
            
            # Try to split name
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                fields["surname"] = name_parts[0]
                fields["first_name"] = name_parts[1]
                fields["middle_name"] = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
        
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
        
        # Issue Date
        issue_match = re.search(r'Issue[_\s]*Date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
        if issue_match:
            fields["issue_date"] = issue_match.group(1)
        
        # Expiry Date
        expiry_match = re.search(r'Expiry[_\s]*Date[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text, re.I)
        if expiry_match:
            fields["expiry_date"] = expiry_match.group(1)
        
        # Vehicle Categories
        cat_match = re.search(r'Categories?[:\s]*([A-Z,\s]+)', text, re.I)
        if cat_match:
            categories = cat_match.group(1).strip()
            fields["vehicle_categories"] = [cat.strip() for cat in categories.split(',')]
        
        # Blood Group
        blood_match = re.search(r'Blood[_\s]*Group[:\s]*([A-Z0-9+-]+)', text, re.I)
        if blood_match:
            fields["blood_group"] = blood_match.group(1).upper()
        
        # Address
        addr_match = re.search(r'Address[:\s]*([^0-9]+(?:[0-9]+[^0-9]+)*)', text, re.I)
        if addr_match:
            fields["address"] = addr_match.group(1).strip().title()
        
        # Height
        height_match = re.search(r'Height[:\s]*([0-9.]+)', text, re.I)
        if height_match:
            fields["height"] = height_match.group(1)
        
        return fields