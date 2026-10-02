import re
import hashlib
from typing import List, Tuple, Dict, Set, Any
from shared.logging import logger

class TextCleaner:
    """
    Deterministic Python text cleaning pipeline.
    Performs whitespace, heading, date, and terminology normalization.
    """

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        # Replace non-breaking spaces
        text = text.replace("\u00a0", " ").replace("\r\n", "\n")
        # Collapse multi-spaces into single space on same line
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse >3 consecutive newlines into 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def normalize_headings(text: str) -> str:
        # Standardize Markdown headers to ensure a single space after '#'
        lines = []
        for line in text.splitlines():
            m = re.match(r'^(#{1,6})[ \t]*(.*)', line)
            if m:
                hashes, title = m.groups()
                lines.append(f"{hashes} {title.strip()}")
            else:
                lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def normalize_dates(text: str) -> str:
        """
        Normalizes dates to ISO format (YYYY-MM-DD).
        Handles formats like MM/DD/YYYY, YYYY/MM/DD.
        """
        # MM/DD/YYYY to YYYY-MM-DD
        text = re.sub(
            r'\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(20\d{2})\b',
            r'\3-\1-\2',
            text
        )
        # YYYY/MM/DD to YYYY-MM-DD
        text = re.sub(
            r'\b(20\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])\b',
            r'\1-\2-\3',
            text
        )
        return text

    @staticmethod
    def normalize_terminology(text: str) -> str:
        """
        Standardizes financial terms for search index consistency while retaining original terms.
        e.g., 'annual turnover' -> 'annual revenue (turnover)'
        """
        # Replace instances of standalone 'turnover' with 'revenue (turnover)' if not already combined
        # Keep replacement idempotent
        text = re.sub(r'\bannual turnover\b', 'annual revenue (turnover)', text, flags=re.IGNORECASE)
        text = re.sub(r'\bEMI\b', 'monthly installment (EMI)', text)
        return text

    def clean_text(self, text: str) -> str:
        text = self.normalize_whitespace(text)
        text = self.normalize_headings(text)
        text = self.normalize_dates(text)
        text = self.normalize_terminology(text)
        return text


class Deduplicator:
    """
    Detects exact and near-duplicate document content.
    """

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_exact_hashes: Set[str] = set()
        self.seen_token_sets: List[Tuple[str, Set[str]]] = []

    @staticmethod
    def compute_hash(text: str) -> str:
        normalized = re.sub(r'\s+', '', text.lower())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return set(words)

    @staticmethod
    def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0

    def is_exact_duplicate(self, text: str) -> bool:
        content_hash = self.compute_hash(text)
        if content_hash in self.seen_exact_hashes:
            return True
        self.seen_exact_hashes.add(content_hash)
        return False

    def is_near_duplicate(self, doc_id: str, text: str) -> Tuple[bool, float, str]:
        tokens = self._tokenize(text)
        if not tokens:
            return False, 0.0, ""

        for existing_id, existing_tokens in self.seen_token_sets:
            sim = self.jaccard_similarity(tokens, existing_tokens)
            if sim >= self.similarity_threshold:
                logger.info(f"Near duplicate detected between {doc_id} and {existing_id} (similarity: {sim:.2f})")
                return True, sim, existing_id

        self.seen_token_sets.append((doc_id, tokens))
        return False, 0.0, ""
