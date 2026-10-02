"""
Localized Fallback and Human Escalation Handlers for Philippines and Indonesia.
Ensures fallback and escalation remain strictly in the customer's native language/register.
"""

def get_localized_fallback(market: str) -> str:
    """Returns fallback message in native language/register."""
    if market.lower() in ["philippines", "ph"]:
        return "Pasensya na po, medyo naputol po ang linya o hindi ko po masyadong naintindihan. Pwede niyo po bang ulitin?"
    elif market.lower() in ["indonesia", "id"]:
        return "Mohon maaf Bapak/Ibu, suara kurang terdengar jelas. Bisa tolong diulangi kembali Pak/Bu?"
    else:
        return "I apologize, I did not catch that. Could you please repeat?"

def get_localized_escalation(market: str, details: str = "") -> str:
    """Returns escalation message in native language/register."""
    if market.lower() in ["philippines", "ph"]:
        return (
            "Naiintindihan ko po. I-transfer ko po ang tawag ninyo sa aming Senior Bancassurance Specialist "
            "sa pinakamalapit na BDO/BPI branch para mas maasikaso po kayo. Sandali lamang po."
        )
    elif market.lower() in ["indonesia", "id"]:
        return (
            "Baik Bapak/Ibu, saya bantu hubungkan langsung dengan Customer Service Officer (CSO) kami "
            "di kantor cabang terdekat untuk penanganan lebih lanjut. Mohon tunggu sebentar ya Pak/Bu."
        )
    else:
        return "Transferring your call to a human specialist now. Please hold."
