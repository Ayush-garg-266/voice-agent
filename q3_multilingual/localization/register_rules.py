"""
Politeness and Register Rules for Philippines and Indonesia Localizations.
"""

REGISTER_RULES = {
    "philippines": {
        "culture": "Filipino Hospitality & Respectfulness (Pakikisama & Paggalang)",
        "honorifics": ["po", "opo", "Ma'am", "Sir"],
        "code_switching": "Natural Manila Taglish (mix of Tagalog grammar + English financial terms)",
        "prohibited": ["Overly formal archaic Tagalog (e.g. 'ipagkaloob')", "Direct demanding tone without 'po'"],
        "example_transformation": {
            "informal": "Magbayad ka na ng premium mo bukas.",
            "localized_polite": "Ipaalala lang po namin na ang inyong premium payment ay due na po bukas."
        }
    },
    "indonesia": {
        "culture": "Indonesian Customer Service Courtesy (Santun & Ramah)",
        "honorifics": ["Bapak", "Ibu", "Pak", "Bu"],
        "code_switching": "Formal/Colloquial Bahasa Indonesia + accepted English finance loanwords (VA, Tenor, Auto-debit)",
        "prohibited": ["Using 'Kamu' or 'Lu/Gua' in professional financial context", "Abrupt command imperative without Pak/Bu"],
        "example_transformation": {
            "informal": "Lu harus bayar cicilan sebelum jatuh tempo.",
            "localized_polite": "Mohon pembayaran angsuran dilakukan sebelum tanggal jatuh tempo ya Bapak/Ibu."
        }
    }
}
