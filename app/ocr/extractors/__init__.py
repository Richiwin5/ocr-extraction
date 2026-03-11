# app/ocr/extractors/__init__.py
from .base_extractor import BaseExtractor
from .voters_extractor import VotersCardExtractor
from .nin_extractor import NINExtractor
from .passport_extractor import PassportExtractor
from .drivers_license_extractor import DriversLicenseExtractor

__all__ = [
    'BaseExtractor',
    'VotersCardExtractor',
    'NINExtractor',
    'PassportExtractor',
    'DriversLicenseExtractor'
]