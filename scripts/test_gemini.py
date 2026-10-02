#!/usr/bin/env python3
"""
Phase 1 Gemini API Connection Verification Script.
Tests connectivity to Google Gemini API using google-genai SDK.
Does NOT output or expose API secrets.
"""

import sys
import os

# Add parent directory to path to allow importing shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config import settings
from shared.logging import logger
from shared.llm.gemini_client import get_gemini_client, GeminiClient

def main():
    print("=" * 60)
    print("  Phase 1: Google Gemini API Connectivity Test")
    print("=" * 60)

    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"

    if not api_key or not api_key.strip():
        print("\n[ERROR] GEMINI_API_KEY is not configured in .env or environment!")
        print("Please follow these steps to set up your key:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your key: GEMINI_API_KEY=<your_gemini_api_key>")
        print("  3. Re-run this script: python scripts/test_gemini.py\n")
        sys.exit(1)

    # Mask API key for secure console display
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
    print(f"[*] API Key Status: Configured ({masked_key})")
    print(f"[*] Target Model:   {model_name}")
    print("[*] Initiating minimal Gemini API test call...")

    try:
        client = get_gemini_client()
        prompt = "Hello Gemini! Respond in one concise sentence verifying that the connection is active."

        response = client.generate(
            prompt=prompt,
            model=model_name,
            temperature=0.2
        )

        print("\n" + "-" * 60)
        print("  Gemini API Response:")
        print("-" * 60)
        print(response.strip())
        print("-" * 60)
        print("\n[SUCCESS] Phase 1 Gemini connection verified successfully!")
        print("The system is now ready for Phase 2 Knowledge Base development.\n")

    except ValueError as ve:
        print(f"\n[CONFIGURATION ERROR] {str(ve)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[API TEST FAILED] {str(e)}")
        print("Please check your GEMINI_API_KEY validity, network connection, or quota.")
        sys.exit(1)

if __name__ == "__main__":
    main()
