"""
Philippines Localization Formatters for Q3 Bancassurance / Life Insurance Bot.
Handles currency (PHP), dates, payment instructions, and Taglish politeness formatting.
"""

from datetime import datetime

def format_currency_ph(amount: float) -> str:
    """Format numeric amount into Philippine Peso representation."""
    formatted_num = f"{amount:,.2f}"
    return f"₱{formatted_num} Pesos"

def format_date_ph(date_obj: datetime) -> str:
    """Format date into natural Filipino/Taglish representation."""
    months_tagalog = {
        1: "Enero", 2: "Pebrero", 3: "Marso", 4: "Abril",
        5: "Mayo", 6: "Hunyo", 7: "Hulyo", 8: "Agosto",
        9: "Setyembre", 10: "Oktubre", 11: "Nobyembre", 12: "Disyembre"
    }
    month_str = months_tagalog.get(date_obj.month, date_obj.strftime("%B"))
    return f"{month_str} {date_obj.day}, {date_obj.year}"

def format_payment_explanation_ph() -> str:
    """Returns Taglish localized explanation of available payment channels."""
    return (
        "Pwede niyo pong bayaran ang inyong premium insurance sa pamamagitan ng mga sumusunod:\n"
        "1. Auto-debit arrangement (ADA) mula sa inyong BDO o BPI savings account.\n"
        "2. E-wallets katulad ng GCash at Maya (pumunta sa Pay Bills -> Insurance -> SunLife/Philam).\n"
        "3. Over-the-counter sa alinmang Bayad Center o partner bank branches nationwide."
    )

def apply_politeness_ph(text: str) -> str:
    """Ensure respectful Filipino customer service register (po/opo)."""
    if "po" not in text.lower() and "opo" not in text.lower():
        # Append polite closing if missing
        return text.strip() + " po."
    return text
