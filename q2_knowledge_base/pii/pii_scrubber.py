import re
from typing import Tuple
from shared.logging import logger

class PIIScrubber:
    """
    Regex and rule-based PII scrubber to detect and mask sensitive customer data.
    Ensures zero actual PII is stored in Knowledge Base vector or keyword indexes.
    """

    # Email pattern
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

    # Phone number pattern (International & North American formats)
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

    # Social Security Numbers (SSN) & Tax IDs (EIN: 12-3456789 or SSN: 123-45-6789)
    SSN_EIN_REGEX = re.compile(r'\b(?:\d{3}-\d{2}-\d{4}|\d{2}-\d{7})\b')

    # Bank Account Numbers (8 to 17 digits preceded by account/acct/iban)
    ACCOUNT_REGEX = re.compile(r'\b(?:acct|account|iban|acc|no\.?)\s*[:#]?\s*([A-Z0-9]{8,17})\b', re.IGNORECASE)

    # Street Address Pattern (basic street number + name + suffix)
    ADDRESS_REGEX = re.compile(r'\b\d{1,5}\s+[A-Z0-9\.\s]{2,30}\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way)\b', re.IGNORECASE)

    def scrub(self, text: str) -> Tuple[str, bool]:
        """
        Detects and redacts PII fields.
        Returns:
            (redacted_text, pii_detected_flag)
        """
        pii_detected = False

        # Redact emails
        if self.EMAIL_REGEX.search(text):
            text = self.EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
            pii_detected = True

        # Redact SSN/EIN
        if self.SSN_EIN_REGEX.search(text):
            text = self.SSN_EIN_REGEX.sub("[REDACTED_TAX_ID]", text)
            pii_detected = True

        # Redact Bank Accounts
        if self.ACCOUNT_REGEX.search(text):
            text = self.ACCOUNT_REGEX.sub(r"account: [REDACTED_ACCOUNT]", text)
            pii_detected = True

        # Redact Phone Numbers (excluding standard 800/888 helpline numbers if desired, but masking all for safety)
        if self.PHONE_REGEX.search(text):
            text = self.PHONE_REGEX.sub("[REDACTED_PHONE]", text)
            pii_detected = True

        # Redact Addresses
        if self.ADDRESS_REGEX.search(text):
            text = self.ADDRESS_REGEX.sub("[REDACTED_ADDRESS]", text)
            pii_detected = True

        if pii_detected:
            logger.info("PII detected and redacted from text segment.")

        return text, pii_detected
