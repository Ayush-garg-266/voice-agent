"""
Automated Pytest Suite for Q3 Multilingual Voice Bots (Philippines & Indonesia).
Tests system prompts, flow engines, politeness registers, regional accent tolerance,
fallbacks, escalations, formatters, and TTS/ASR evaluators.
"""

import pytest
from datetime import datetime
from q3_multilingual.philippines import PhilippinesBancassuranceBot, get_philippines_system_prompt, PH_BANCASSURANCE_KB
from q3_multilingual.indonesia import IndonesiaMultifinanceBot, get_indonesia_system_prompt, ID_MULTIFINANCE_KB
from q3_multilingual.localization.register_rules import REGISTER_RULES
from q3_multilingual.localization.fallbacks import get_localized_fallback, get_localized_escalation
from q3_multilingual.localization.date_amount_formatter import format_localized_amount, format_localized_date
from q3_multilingual.localization.examples import CONCRETE_LOCALIZATION_EXAMPLES
from q3_multilingual.speech.tts_evaluator import TTSEvaluator
from q3_multilingual.speech.asr_evaluator import ASREvaluator


def test_philippines_prompt_and_kb():
    """Verify Philippines system prompt contains required Taglish terms and rules."""
    prompt = get_philippines_system_prompt()
    assert "Maria" in prompt
    assert "Taglish" in prompt
    assert "premium" in prompt
    assert "policy" in prompt
    assert "beneficiary" in prompt
    assert "rider" in prompt
    assert "lapse" in prompt
    assert "coverage" in prompt
    assert "bank referral" in prompt
    assert "po" in prompt and "opo" in prompt
    assert PH_BANCASSURANCE_KB["product_name"] is not None


def test_indonesia_prompt_and_kb():
    """Verify Indonesia system prompt contains required finance terms and accent guidance."""
    prompt = get_indonesia_system_prompt()
    assert "Budi" in prompt
    assert "cicilan" in prompt
    assert "tenor" in prompt
    assert "denda" in prompt
    assert "DP" in prompt
    assert "jatuh tempo" in prompt
    assert "angsuran" in prompt
    assert "pembiayaan" in prompt
    assert "Bapak" in prompt or "Ibu" in prompt
    assert "Jawa" in prompt or "Sunda" in prompt
    assert ID_MULTIFINANCE_KB["company_name"] is not None


def test_philippines_formatting():
    """Verify Philippine Peso and date formatting."""
    amount_str = format_localized_amount(2500.0, "philippines")
    assert "₱2,500.00 Pesos" in amount_str

    dt = datetime(2026, 10, 15)
    date_str = format_localized_date(dt, "philippines")
    assert "Oktubre 15, 2026" in date_str


def test_indonesia_formatting():
    """Verify Indonesian Rupiah and date formatting."""
    amount_str = format_localized_amount(450000.0, "indonesia")
    assert "Rp 450.000,- (Rupiah)" in amount_str

    dt = datetime(2026, 10, 15)
    date_str = format_localized_date(dt, "indonesia")
    assert "15 Oktober 2026" in date_str


def test_localized_fallbacks_and_escalations():
    """Verify fallbacks and escalations remain in customer's native language."""
    ph_fb = get_localized_fallback("philippines")
    assert "Pasensya na po" in ph_fb or "po" in ph_fb
    assert "English" not in ph_fb

    id_fb = get_localized_fallback("indonesia")
    assert "Mohon maaf Bapak/Ibu" in id_fb or "Pak/Bu" in id_fb
    assert "English" not in id_fb

    ph_esc = get_localized_escalation("philippines")
    assert "Senior Bancassurance Specialist" in ph_esc
    assert "po" in ph_esc

    id_esc = get_localized_escalation("indonesia")
    assert "Customer Service Officer" in id_esc
    assert "Bapak/Ibu" in id_esc or "Pak/Bu" in id_esc


def test_concrete_localization_examples():
    """Verify at least 3 concrete localization examples exist per market."""
    assert len(CONCRETE_LOCALIZATION_EXAMPLES["philippines"]) >= 3
    assert len(CONCRETE_LOCALIZATION_EXAMPLES["indonesia"]) >= 3

    for ex in CONCRETE_LOCALIZATION_EXAMPLES["philippines"]:
        assert "differences_explained" in ex
        assert "wording" in ex["differences_explained"]
        assert "politeness" in ex["differences_explained"]
        assert "terminology" in ex["differences_explained"]
        assert "code_switching" in ex["differences_explained"]

    for ex in CONCRETE_LOCALIZATION_EXAMPLES["indonesia"]:
        assert "differences_explained" in ex
        assert "wording" in ex["differences_explained"]
        assert "politeness" in ex["differences_explained"]
        assert "terminology" in ex["differences_explained"]


def test_tts_and_asr_evaluators():
    """Verify TTS and ASR evaluator reports."""
    tts_report = TTSEvaluator.evaluate_gemini_tts()
    assert "provider" in tts_report
    assert "limitations" in tts_report

    asr_report = ASREvaluator.get_asr_documentation()
    assert "philippines" in asr_report
    assert "indonesia" in asr_report
    assert "known_errors" in asr_report["philippines"]
    assert "accent_limitations" in asr_report["indonesia"]


@pytest.mark.integration
def test_philippines_bot_turn():
    """Integration test for PH Bot turn processing."""
    bot = PhilippinesBancassuranceBot()
    res = bot.process_turn("Magandang araw po, magkano po ang aking monthly premium?")
    assert res["stage"] is not None
    assert "po" in res["response"].lower() or "opo" in res["response"].lower()


@pytest.mark.integration
def test_indonesia_bot_turn():
    """Integration test for ID Bot turn processing."""
    bot = IndonesiaMultifinanceBot(user_gender_honorific="Bapak")
    res = bot.process_turn("Selamat siang Pak, kapan tanggal jatuh tempo cicilan motor saya?")
    assert res["stage"] is not None
    assert "bapak" in res["response"].lower() or "pak" in res["response"].lower()
