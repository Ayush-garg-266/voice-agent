import re
import uuid
from typing import List, Dict, Any, Tuple, Optional
from q2_knowledge_base.ingestion.loader import RawDocument
from q2_knowledge_base.cleaning.cleaner import TextCleaner
from q2_knowledge_base.pii.pii_scrubber import PIIScrubber
from shared.logging import logger

class KBChunk:
    """
    Structured Knowledge Base Chunk object with full attribution metadata.
    """
    def __init__(
        self,
        record_id: str,
        chunk_id: str,
        title: str,
        category: str,
        source_id: str,
        source_name: str,
        source_type: str,
        version: str,
        section: str,
        content: str,
        created_at: str,
        pii_flag: bool = False,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        self.record_id = record_id
        self.chunk_id = chunk_id
        self.title = title
        self.category = category
        self.source_id = source_id
        self.source_name = source_name
        self.source_type = source_type
        self.version = version
        self.section = section
        self.content = content
        self.created_at = created_at
        self.pii_flag = pii_flag
        self.extra_metadata = extra_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "category": self.category,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "version": self.version,
            "section": self.section,
            "content": self.content,
            "created_at": self.created_at,
            "pii_flag": self.pii_flag,
            "extra_metadata": self.extra_metadata
        }


class SemanticChunker:
    """
    Structure-aware chunker preserving header sections and document context.
    Integrates cleaning and PII masking.
    """

    def __init__(self, target_chunk_size: int = 600, overlap: int = 50):
        self.cleaner = TextCleaner()
        self.scrubber = PIIScrubber()
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def chunk_document(self, raw_doc: RawDocument) -> List[KBChunk]:
        cleaned_text = self.cleaner.clean_text(raw_doc.content)
        sections = self._split_into_sections(cleaned_text, raw_doc.source_type)

        chunks: List[KBChunk] = []
        chunk_idx = 1

        for sec_title, sec_content in sections:
            scrubbed_content, pii_flag = self.scrubber.scrub(sec_content)
            if not scrubbed_content.strip():
                continue

            sub_blocks = self._sub_split_text(scrubbed_content, self.target_chunk_size)

            for sub_content in sub_blocks:
                rec_id = f"kb_{raw_doc.source_id.lower()}_{chunk_idx:03d}"
                c_id = f"chunk_{uuid.uuid4().hex[:8]}"

                chunk_obj = KBChunk(
                    record_id=rec_id,
                    chunk_id=c_id,
                    title=raw_doc.extra_metadata.get("title", raw_doc.source_name),
                    category=raw_doc.category,
                    source_id=raw_doc.source_id,
                    source_name=raw_doc.source_name,
                    source_type=raw_doc.source_type,
                    version=raw_doc.version,
                    section=sec_title,
                    content=sub_content.strip(),
                    created_at=raw_doc.created_at,
                    pii_flag=pii_flag,
                    extra_metadata=raw_doc.extra_metadata
                )
                chunks.append(chunk_obj)
                chunk_idx += 1

        logger.info(f"Chunked [{raw_doc.source_id}] {raw_doc.source_name} -> {len(chunks)} chunks")
        return chunks

    def _split_into_sections(self, text: str, source_type: str) -> List[Tuple[str, str]]:
        """
        Splits text into (section_title, section_body) tuples based on Markdown/HTML structure.
        """
        if source_type in ["markdown", "md", "txt", "html"]:
            header_pattern = re.compile(r'^(#{1,4}\s+.*)', re.MULTILINE)
            splits = header_pattern.split(text)

            sections: List[Tuple[str, str]] = []
            current_title = "Overview / General"
            current_buffer = []

            for part in splits:
                if header_pattern.match(part):
                    if current_buffer:
                        sections.append((current_title, "\n".join(current_buffer).strip()))
                        current_buffer = []
                    current_title = part.lstrip("#").strip()
                else:
                    current_buffer.append(part)

            if current_buffer:
                sections.append((current_title, "\n".join(current_buffer).strip()))

            return [(title, body) for title, body in sections if body.strip()]
        else:
            return [("Main Policy Body", text)]

    def _sub_split_text(self, text: str, max_words: int) -> List[str]:
        words = text.split()
        if len(words) <= max_words:
            return [text]

        sub_blocks = []
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            block_words = words[start:end]
            sub_blocks.append(" ".join(block_words))
            start += max_words - self.overlap
        return sub_blocks
