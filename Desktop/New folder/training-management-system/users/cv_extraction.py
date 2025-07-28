import os
from pyresparser import ResumeParser

def extract_cv_info(cv_path):
    """
    Extracts information from a CV file using pyresparser.
    Args:
        cv_path (str): Path to the CV file (PDF, DOCX, etc.)
    Returns:
        dict: Extracted data (name, email, skills, education, etc.)
    """
    if not os.path.exists(cv_path):
        raise FileNotFoundError(f"File not found: {cv_path}")
    data = ResumeParser(cv_path).get_extracted_data()
    return data
