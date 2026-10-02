"""
Indonesia Localization Formatters for Q3 Multifinance / Consumer Finance Bot.
Handles currency (IDR / Rupiah), dates, payment instructions, and Indonesian politeness formatting.
"""

from datetime import datetime

def format_currency_id(amount: float) -> str:
    """Format numeric amount into Indonesian Rupiah representation."""
    formatted_num = f"{int(amount):,}".replace(",", ".")
    return f"Rp {formatted_num},- (Rupiah)"

def format_date_id(date_obj: datetime) -> str:
    """Format date into standard Indonesian representation."""
    months_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    month_str = months_id.get(date_obj.month, date_obj.strftime("%B"))
    return f"{date_obj.day} {month_str} {date_obj.year}"

def format_payment_explanation_id() -> str:
    """Returns Indonesian localized explanation of available payment channels."""
    return (
        "Pembayaran angsuran/cicilan pembiayaan dapat dilakukan melalui beberapa saluran berikut:\n"
        "1. Transfer Virtual Account (BCA, Mandiri, BRI, BNI) melalui M-Banking.\n"
        "2. Kasir minimarket (Indomaret atau Alfamart) dengan menunjukkan nomor kontrak pembiayaan.\n"
        "3. QRIS atau Autodebet rekening bank terdaftar sebelum tanggal jatuh tempo."
    )

def apply_politeness_id(text: str, gender_honorific: str = "Bapak/Ibu") -> str:
    """Ensure polite Indonesian customer service register using Pak/Bu or Bapak/Ibu."""
    if "bapak" not in text.lower() and "ibu" not in text.lower() and "pak" not in text.lower() and "bu" not in text.lower():
        return f"{text.strip()} {gender_honorific}."
    return text
