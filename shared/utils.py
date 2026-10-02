import re

def redact_pii(text: str) -> str:
    """
    Basic PII masking utility for email, phone numbers, SSNs, and Tax IDs.
    """
    # Mask emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    # Mask phone numbers
    text = re.sub(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[REDACTED_PHONE]', text)
    # Mask SSN / Tax IDs (simple 9-digit format)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_TAX_ID]', text)
    return text
