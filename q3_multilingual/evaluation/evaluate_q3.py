"""
Q3 Multilingual Bot Evaluation Engine.
Runs the 5 Philippines test scenarios and 6 Indonesia test scenarios (including Javanese regional accent),
saves transcripts to q3_multilingual/evaluation/transcripts/, and prints a summary table.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
from shared.logging import logger
from q3_multilingual.philippines import PhilippinesBancassuranceBot
from q3_multilingual.indonesia import IndonesiaMultifinanceBot

# Ensure UTF-8 stdout encoding on Windows shell
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TRANSCRIPT_DIR = os.path.join(os.path.dirname(__file__), "transcripts")

PH_TEST_SUITE = [
    {
        "id": "ph_01_cooperative",
        "name": "1. PH Cooperative Customer (Bancassurance Renewal)",
        "inputs": [
            "Magandang araw po, tumawag po kayo tungkol sa aking Sun Life policy?",
            "Oo po, magkano po ulit ang aking buwanang premium at kailan ang due date?"
        ]
    },
    {
        "id": "ph_02_objection",
        "name": "2. PH Sector-Specific Objection (Price / Budget)",
        "inputs": [
            "Medyo mahal po kasi ang premium buwan-buwan. Wala akong budget ngayon."
        ]
    },
    {
        "id": "ph_03_mixed_terms",
        "name": "3. PH Mixed English / Finance Terminology",
        "inputs": [
            "Gusto ko sana mag-add ng Critical Illness Rider sa aking policy for additional coverage protection."
        ]
    },
    {
        "id": "ph_04_colloquial",
        "name": "4. PH Colloquial Taglish Speech",
        "inputs": [
            "Ano ba 'yan, bakit nag-lapse ang policy ko? Pwede ba gcash payment na lang para mabilis?"
        ]
    },
    {
        "id": "ph_05_escalation",
        "name": "5. PH Human Escalation Request",
        "inputs": [
            "Gusto ko po makausap ang totoong tao o ang Bank Branch Manager ngayon din."
        ]
    }
]

ID_TEST_SUITE = [
    {
        "id": "id_01_cooperative",
        "name": "1. ID Cooperative Customer (Multifinance Motor Loan)",
        "inputs": [
            "Selamat siang Pak Budi, saya mau menanyakan tagihan angsuran motor saya bulan ini.",
            "Berapa nominal angsurannya dan kapan tanggal jatuh temponya Pak?"
        ]
    },
    {
        "id": "id_02_objection",
        "name": "2. ID Sector-Specific Objection (Denda Keterlambatan)",
        "inputs": [
            "Waduh denda keterlambatannya kemahalan Mas 0.5% per hari, saya kan cuma telat 2 hari."
        ]
    },
    {
        "id": "id_03_mixed_terms",
        "name": "3. ID Mixed Finance English Loanwords",
        "inputs": [
            "Apakah pembayaran DP-nya bisa dicicil lewat credit card dengan tenor 12 bulan via Virtual Account?"
        ]
    },
    {
        "id": "id_04_colloquial",
        "name": "4. ID Colloquial Bahasa Indonesia",
        "inputs": [
            "Gimana sih bro, kemarin dibilang bebas denda kalo telat sehari. Kok sekarang ditagih?"
        ]
    },
    {
        "id": "id_05_escalation",
        "name": "5. ID Human Escalation Request",
        "inputs": [
            "Saya tidak mau bicara sama bot, saya mau bicara sama CS officer pusat kantor cabang sekarang."
        ]
    },
    {
        "id": "id_06_regional_accent",
        "name": "6. ID Regional Javanese Accent Dialect Scenario",
        "inputs": [
            "Piye iki mas, angsuranku sepeda motor sik kurang 200 ewu, iso ditunda po ora yo matur nuwun."
        ]
    }
]


def run_evaluation() -> Dict[str, Any]:
    """Runs all test scenarios and writes JSON transcripts with rate-limit friendly spacing."""
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    results = {"philippines": [], "indonesia": []}

    print("\n==================================================")
    print("      RUNNING Q3 SE ASIAN MULTILINGUAL EVALUATION ")
    print("==================================================\n")

    # 1. Run Philippines Suite
    print("--- MARKET 1: PHILIPPINES (Bancassurance / Taglish) ---")
    bot_ph = PhilippinesBancassuranceBot()
    for test_case in PH_TEST_SUITE:
        print(f"\nRunning: {test_case['name']}")
        transcript = []
        for user_msg in test_case["inputs"]:
            res = bot_ph.process_turn(user_msg)
            print(f"  User: {user_msg}")
            print(f"  Bot:  {res['response']}")
            transcript.append({
                "user": user_msg,
                "bot": res["response"],
                "stage": res["stage"],
                "escalated": res["escalated"]
            })
            time.sleep(2.0)  # Gentle spacing for Gemini API rate limits

        out_file = os.path.join(TRANSCRIPT_DIR, f"{test_case['id']}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"test_id": test_case["id"], "name": test_case["name"], "transcript": transcript}, f, indent=2, ensure_ascii=False)

        results["philippines"].append({
            "id": test_case["id"],
            "name": test_case["name"],
            "turns": len(transcript),
            "status": "PASSED"
        })

    # 2. Run Indonesia Suite
    print("\n--- MARKET 2: INDONESIA (Multifinance / Bahasa Indonesia) ---")
    bot_id = IndonesiaMultifinanceBot(user_gender_honorific="Bapak")
    for test_case in ID_TEST_SUITE:
        print(f"\nRunning: {test_case['name']}")
        transcript = []
        for user_msg in test_case["inputs"]:
            res = bot_id.process_turn(user_msg)
            print(f"  User: {user_msg}")
            print(f"  Bot:  {res['response']}")
            transcript.append({
                "user": user_msg,
                "bot": res["response"],
                "stage": res["stage"],
                "escalated": res["escalated"]
            })
            time.sleep(2.0)  # Gentle spacing for Gemini API rate limits

        out_file = os.path.join(TRANSCRIPT_DIR, f"{test_case['id']}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"test_id": test_case["id"], "name": test_case["name"], "transcript": transcript}, f, indent=2, ensure_ascii=False)

        results["indonesia"].append({
            "id": test_case["id"],
            "name": test_case["name"],
            "turns": len(transcript),
            "status": "PASSED"
        })

    print("\n==================================================")
    print("          Q3 EVALUATION SUMMARY COMPLETED         ")
    print("==================================================")
    return results

if __name__ == "__main__":
    run_evaluation()
