import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from shared.logging import logger

class RawDocument:
    """
    Represents an ingested raw document with mandatory metadata fields.
    """
    def __init__(
        self,
        content: str,
        source_id: str,
        source_name: str,
        source_type: str,
        version: str = "1.0",
        category: str = "general",
        original_location: str = "",
        created_at: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.source_id = source_id
        self.source_name = source_name
        self.source_type = source_type
        self.version = version
        self.category = category
        self.original_location = original_location
        self.ingestion_timestamp = datetime.utcnow().isoformat() + "Z"
        self.created_at = created_at or self.ingestion_timestamp
        self.extra_metadata = extra_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "version": self.version,
            "category": self.category,
            "ingestion_timestamp": self.ingestion_timestamp,
            "created_at": self.created_at,
            "original_location": self.original_location,
            "extra_metadata": self.extra_metadata,
            "content_length": len(self.content)
        }


class DocumentLoader:
    """
    Ingestion pipeline supporting Markdown, TXT, CSV, JSON, HTML, PDF, and DOCX formats.
    Retains full source attribution and metadata.
    """

    def __init__(self, raw_dir: str):
        self.raw_dir = os.path.abspath(raw_dir)
        self.manifest_path = os.path.join(self.raw_dir, "source_manifest.json")
        self.manifest_data = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load source_manifest.json: {e}")
        return {"sources": []}

    def _get_manifest_meta(self, filename: str) -> Dict[str, Any]:
        for src in self.manifest_data.get("sources", []):
            if src.get("filename") == filename:
                return src
        # Fallback default metadata if file not in manifest
        base_name = os.path.splitext(filename)[0]
        return {
            "source_id": f"SRC_{base_name.upper()}",
            "title": base_name.replace("_", " ").title(),
            "source_type": os.path.splitext(filename)[1].lstrip("."),
            "version": "1.0",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d"),
            "category": "general"
        }

    def load_file(self, filename: str) -> RawDocument:
        file_path = os.path.join(self.raw_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        meta = self._get_manifest_meta(filename)
        ext = os.path.splitext(filename)[1].lower()

        content = ""
        if ext in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        elif ext == ".html":
            with open(file_path, "r", encoding="utf-8") as f:
                html_raw = f.read()
                soup = BeautifulSoup(html_raw, "html.parser")
                # Remove navigation and scripts
                for elem in soup(["script", "style", "nav", "header", "footer"]):
                    elem.decompose()
                content = soup.get_text(separator="\n\n").strip()
        elif ext == ".csv":
            rows = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for r in reader:
                    if r and not r[0].startswith("#"):
                        rows.append(" | ".join(r))
            content = "\n".join(rows)
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                content = json.dumps(data, indent=2)
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                content = "\n\n".join(pages)
            except Exception as e:
                logger.error(f"Failed to read PDF {filename}: {e}")
                content = f"[PDF Extraction Error: {e}]"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        return RawDocument(
            content=content,
            source_id=meta.get("source_id", "SRC_UNKNOWN"),
            source_name=filename,
            source_type=meta.get("source_type", ext.lstrip(".")),
            version=meta.get("version", "1.0"),
            category=meta.get("category", "general"),
            original_location=file_path,
            created_at=meta.get("created_at"),
            extra_metadata=meta
        )

    def load_all(self) -> List[RawDocument]:
        documents = []
        if not os.path.exists(self.raw_dir):
            logger.warning(f"Raw directory does not exist: {self.raw_dir}")
            return []

        for fname in os.listdir(self.raw_dir):
            if fname.endswith(".json") and fname == "source_manifest.json":
                continue
            if os.path.isfile(os.path.join(self.raw_dir, fname)):
                try:
                    doc = self.load_file(fname)
                    documents.append(doc)
                    logger.info(f"Ingested [{doc.source_id}] {fname} ({doc.source_type}, {len(doc.content)} chars)")
                except Exception as e:
                    logger.error(f"Failed to load document {fname}: {e}")
        return documents
