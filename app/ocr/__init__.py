# app/ocr/__init__.py
from .ocr_engine import extract_text
from .document_classifier import DocumentClassifier

__all__ = ['extract_text', 'DocumentClassifier']