"""
Localized Date and Amount Formatter for SE Asian Markets (PH & ID).
"""

from datetime import datetime

def format_localized_amount(amount: float, market: str) -> str:
    """Format currency for Philippines (PHP) or Indonesia (IDR)."""
    if market.lower() in ["philippines", "ph"]:
        return f"₱{amount:,.2f} Pesos"
    elif market.lower() in ["indonesia", "id"]:
        formatted = f"{int(amount):,}".replace(",", ".")
        return f"Rp {formatted},- (Rupiah)"
    return f"${amount:,.2f}"

def format_localized_date(date_obj: datetime, market: str) -> str:
    """Format date for Philippines or Indonesia."""
    if market.lower() in ["philippines", "ph"]:
        months = {1: "Enero", 2: "Pebrero", 3: "Marso", 4: "Abril", 5: "Mayo", 6: "Hunyo",
                  7: "Hulyo", 8: "Agosto", 9: "Setyembre", 10: "Oktubre", 11: "Nobyembre", 12: "Disyembre"}
        return f"{months.get(date_obj.month, '')} {date_obj.day}, {date_obj.year}"
    elif market.lower() in ["indonesia", "id"]:
        months = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
                  7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
        return f"{date_obj.day} {months.get(date_obj.month, '')} {date_obj.year}"
    return date_obj.strftime("%Y-%m-%d")
