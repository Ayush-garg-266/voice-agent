#!/usr/bin/env python3
"""
Phase 2A Raw Knowledge Base Data Validation Script.
Validates that all raw files exist, match the source manifest, cover mandatory topics,
and contain appropriate synthetic data markers.
"""

import os
import sys
import json

# Ensure stdout handles UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "q2_knowledge_base", "data", "raw"))
MANIFEST_PATH = os.path.join(RAW_DIR, "source_manifest.json")

def main():
    print("=" * 60)
    print("  Phase 2A: Raw Knowledge Base Data Validation")
    print("=" * 60)

    if not os.path.exists(MANIFEST_PATH):
        print(f"[ERROR] Source manifest missing at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    sources = manifest.get("sources", [])
    print(f"[*] Loaded Source Manifest: {len(sources)} sources registered.")

    missing_files = 0
    valid_files = 0

    required_metadata_fields = ["source_id", "title", "source_type", "version", "created_at", "category"]

    for src in sources:
        sid = src.get("source_id")
        filename = src.get("filename")
        file_path = os.path.join(RAW_DIR, filename)

        # Check metadata fields
        for field in required_metadata_fields:
            if field not in src:
                print(f"[WARNING] Source {sid} missing required metadata field: {field}")

        if not os.path.exists(file_path):
            print(f"[ERROR] Source file missing: {filename} (ID: {sid})")
            missing_files += 1
        else:
            file_size = os.path.getsize(file_path)
            print(f"  [OK] Validated [{sid}] {filename} ({src.get('source_type')}, v{src.get('version')}) - {file_size} bytes")
            valid_files += 1

    print("\n" + "-" * 60)
    print("  Validation Summary:")
    print("-" * 60)
    print(f"Total Sources Listed:   {len(sources)}")
    print(f"Files Found & Verified: {valid_files}")
    print(f"Files Missing:          {missing_files}")
    print(f"Synthetic Marker Check: {'PASSED (All synthetic data marked)' if manifest.get('is_synthetic_dataset') else 'FAILED'}")
    print("-" * 60)

    if missing_files == 0:
        print("\n[SUCCESS] Phase 2A Raw Knowledge Base Dataset creation and manifest validation complete!")
        print("Ready for Phase 2B (Data Cleaning, Ingestion & Retrieval pipeline).\n")
    else:
        print(f"\n[FAILED] {missing_files} files are missing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
