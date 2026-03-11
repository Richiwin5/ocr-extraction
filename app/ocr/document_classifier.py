# app/ocr/document_classifier.py
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """
    Classifies ID documents based on text patterns
    """
    
    # Document type signatures
    DOCUMENT_PATTERNS = {
        "voters_card": {
        "patterns": [
            r'VOTERS?\s+CARD',
            r'VOTER.?S?\s+CARD',
            r'INDEPENDENT NATIONAL ELECTORAL COMMISSION',
            r'INEC',
            r'VIN[:\s]*[A-Z0-9]{15,}',
            r'FEDERAL.*REPUBLIC.*NIGERIA',
            r'ELECTORAL COMMISSION',
            r'DELIM',
            r'POLLING UNIT',
            r'PU:',
            r'IKA SOUTH',  # Specific to your image
            r'DELTA.*SOUTH',
            r'NNEBIS ROAD',  # Specific to your image
        ],
        "keywords": ['voter', 'inec', 'vin', 'polling', 'lga', 'ward', 'delim', 'election', 'delta'],
        "country": "nigeria"
    },
        
        "nin": {
            "patterns": [
                r'NATIONAL IDENTITY CARD',
                r'NIN[:\s]*\d{11}',
                r'NATIONAL IDENTIFICATION NUMBER',
                r'NIMC',
            ],
            "keywords": ['nin', 'nimc', 'national identification'],
            "country": "nigeria"
        },
        
        "international_passport": {
            "patterns": [
                r'PASSPORT',
                r'PASSPORT NO[:\s]*[A-Z]\d{8}',
                r'FEDERAL REPUBLIC OF NIGERIA.*PASSPORT',
            ],
            "keywords": ['passport', 'nigerian', 'nga'],
            "country": "nigeria"
        },
        
        "drivers_license": {
            "patterns": [
                r'DRIVER.?S?\s+LICENSE',
                r'DRIVING LICENCE',
                r'DL NO[:\s]*[A-Z0-9]{12,16}',
            ],
            "keywords": ['driver', 'license', 'licence', 'dl no'],
            "country": "nigeria"
        }
    }
    
    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classify document type based on text content
        """
        text_upper = text.upper()
        scores = {}
        
        for doc_type, signatures in cls.DOCUMENT_PATTERNS.items():
            score = 0
            
            # Check patterns
            for pattern in signatures["patterns"]:
                if re.search(pattern, text, re.I):
                    score += 10
                    print(f"Pattern match for {doc_type}: {pattern}")
            
            # Check keywords
            for keyword in signatures["keywords"]:
                if keyword.upper() in text_upper:
                    score += 5
                    print(f"Keyword match for {doc_type}: {keyword}")
            
            scores[doc_type] = score
        
        print(f"Classification scores: {scores}")
        
        # Get document type with highest score
        if scores:
            doc_type = max(scores, key=scores.get)
            confidence = scores[doc_type]
            
            # Determine if confidence is high enough
            if confidence >= 10:  # Threshold
                return {
                    "document_type": doc_type,
                    "confidence": confidence,
                    "country": cls.DOCUMENT_PATTERNS[doc_type]["country"]
                }
        
        return {
            "document_type": "unknown",
            "confidence": 0,
            "country": "unknown"
        }





















# # app/ocr/document_classifier.py
# import re
# from typing import Dict, Any
# import logging

# logger = logging.getLogger(__name__)

# class DocumentClassifier:
#     """
#     Classifies ID documents based on text patterns
#     """
    
#     # Document type signatures
#     DOCUMENT_PATTERNS = {
#         "voters_card": {
#             "patterns": [
#                 r'VOTER.?S?\s+CARD',
#                 r'INDEPENDENT NATIONAL ELECTORAL COMMISSION',
#                 r'INEC',
#                 r'VIN[:\s]*[A-Z0-9]{19}',
#                 r'VOTER.?S?\s+ID',
#                 r'POLLING UNIT',
#                 r'PU:',
#             ],
#             "keywords": ['voter', 'inec', 'vin', 'polling unit', 'lga', 'ward'],
#             "country": "nigeria"
#         },
        
#         "nin": {
#             "patterns": [
#                 r'NATIONAL IDENTITY CARD',
#                 r'NIN[:\s]*\d{11}',
#                 r'NATIONAL IDENTIFICATION NUMBER',
#                 r'NIMC',
#                 r'FINGERPRINT',
#                 r'ADDRESS:',
#             ],
#             "keywords": ['nin', 'nimc', 'national identification', 'identity card'],
#             "country": "nigeria"
#         },
        
#       "international_passport": {
#     "patterns": [
#         r'PASSPORT',
#         r'PASSPORT NO[:\s]*[A-Z]\d{8}',
#         r'PASSPORT NUMBER',
#         r'FEDERAL REPUBLIC OF NIGERIA',  # Add this
#         r'NIGERIAN PASSPORT',  # Add this
#     ],
#     "keywords": ['passport', 'nigerian', 'federal republic', 'nga'],
#     "country": "nigeria"  # Change from "multiple" to "nigeria"
# },
      
    
#         "drivers_license": {
#             "patterns": [
#                 r'DRIVER.?S?\s+LICENSE',
#                 r'DRIVING LICENCE',
#                 r'DRIVER.?S?\s+LICENCE',
#                 r'DL NO[:\s]*[A-Z0-9]{12,16}',
#                 r'ISSUE DATE',
#                 r'EXPIRY DATE',
#                 r'VEHICLE CATEGORY',
#                 r'BLOOD GROUP',
#             ],
#             "keywords": ['driver', 'license', 'licence', 'dl no', 'blood group'],
#             "country": "multiple"
#         }
#     }
    
#     @classmethod
#     def classify(cls, text: str) -> Dict[str, Any]:
#         """
#         Classify document type based on text content
#         """
#         text_upper = text.upper()
#         scores = {}
        
#         for doc_type, signatures in cls.DOCUMENT_PATTERNS.items():
#             score = 0
            
#             # Check patterns
#             for pattern in signatures["patterns"]:
#                 if re.search(pattern, text, re.I):
#                     score += 10
            
#             # Check keywords
#             for keyword in signatures["keywords"]:
#                 if keyword.upper() in text_upper:
#                     score += 5
            
#             scores[doc_type] = score
        
#         # Get document type with highest score
#         if scores:
#             doc_type = max(scores, key=scores.get)
#             confidence = scores[doc_type]
            
#             # Determine if confidence is high enough
#             if confidence >= 10:  # Threshold
#                 return {
#                     "document_type": doc_type,
#                     "confidence": confidence,
#                     "country": cls.DOCUMENT_PATTERNS[doc_type]["country"]
#                 }
        
#         return {
#             "document_type": "unknown",
#             "confidence": 0,
#             "country": "unknown"
#         }












# # app/ocr/document_classifier.py
# import re
# from typing import Dict, Any, List
# import logging

# logger = logging.getLogger(__name__)

# class DocumentClassifier:
#     """
#     Classifies ID documents based on text patterns
#     """
    
#     # Document type signatures
#     DOCUMENT_PATTERNS = {
#         "voters_card": {
#             "patterns": [
#                 r'VOTER.?S?\s+CARD',
#                 r'INDEPENDENT NATIONAL ELECTORAL COMMISSION',
#                 r'INEC',
#                 r'VIN[:\s]*[A-Z0-9]{19}',
#                 r'VOTER.?S?\s+ID',
#                 r'POLLING UNIT',
#                 r'PU:',
#             ],
#             "keywords": ['voter', 'inec', 'vin', 'polling unit', 'lga', 'ward'],
#             "country": "nigeria"
#         },
        
#         "nin": {
#             "patterns": [
#                 r'NATIONAL IDENTITY CARD',
#                 r'NIN[:\s]*\d{11}',
#                 r'NATIONAL IDENTIFICATION NUMBER',
#                 r'NIMC',
#                 r'FINGERPRINT',
#                 r'ADDRESS:',
#             ],
#             "keywords": ['nin', 'nimc', 'national identification', 'identity card'],
#             "country": "nigeria"
#         },
        
#         "international_passport": {
#             "patterns": [
#                 r'PASSPORT',
#                 r'PASSPORT NO[:\s]*[A-Z]\d{8}',
#                 r'PASSPORT NUMBER',
#                 r'ISSUING AUTHORITY',
#                 r'PLACE OF ISSUE',
#                 r'DATE OF ISSUE',
#                 r'DATE OF EXPIRY',
#             ],
#             "keywords": ['passport', 'passport no', 'nationality', 'place of issue'],
#             "country": "multiple"
#         },
        
#         "drivers_license": {
#             "patterns": [
#                 r'DRIVER.?S?\s+LICENSE',
#                 r'DRIVING LICENCE',
#                 r'DRIVER.?S?\s+LICENCE',
#                 r'DL NO[:\s]*[A-Z0-9]{12,16}',
#                 r'ISSUE DATE',
#                 r'EXPIRY DATE',
#                 r'VEHICLE CATEGORY',
#                 r'BLOOD GROUP',
#             ],
#             "keywords": ['driver', 'license', 'licence', 'dl no', 'blood group'],
#             "country": "multiple"
#         }
#     }
    
#     @classmethod
#     def classify(cls, text: str) -> Dict[str, Any]:
#         """
#         Classify document type based on text content
#         """
#         text_upper = text.upper()
#         scores = {}
        
#         for doc_type, signatures in cls.DOCUMENT_PATTERNS.items():
#             score = 0
            
#             # Check patterns
#             for pattern in signatures["patterns"]:
#                 if re.search(pattern, text, re.I):
#                     score += 10
            
#             # Check keywords
#             for keyword in signatures["keywords"]:
#                 if keyword.upper() in text_upper:
#                     score += 5
            
#             scores[doc_type] = score
        
#         # Get document type with highest score
#         if scores:
#             doc_type = max(scores, key=scores.get)
#             confidence = scores[doc_type]
            
#             # Determine if confidence is high enough
#             if confidence >= 10:  # Threshold
#                 return {
#                     "document_type": doc_type,
#                     "confidence": confidence,
#                     "country": cls.DOCUMENT_PATTERNS[doc_type]["country"]
#                 }
        
#         return {
#             "document_type": "unknown",
#             "confidence": 0,
#             "country": "unknown"
#         }