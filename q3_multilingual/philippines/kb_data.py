"""
Philippines Bancassurance Domain Knowledge Base.
Contains policy rules, riders, grace period, lapse policies, FAQs, and objections in Taglish context.
"""

PH_BANCASSURANCE_KB = {
    "product_name": "Bancassurance Protect & Invest Life VUL Plan",
    "partner_banks": ["BDO Unibank", "BPI (Bank of the Philippine Islands)", "Metrobank"],
    "min_premium": 1500.0,  # ₱1,500/month
    "standard_premium": 2500.0, # ₱2,500/month
    "grace_period_days": 31,
    "policy_terms": {
        "premium": "Ang buwanang o taunang hulog para manatiling active ang inyong insurance coverage.",
        "policy": "Ang inyong official life insurance contract at certificate of coverage.",
        "beneficiary": "Ang inyong napiling kamag-anak (tulad ng asawa, anak, o magulang) na makakatanggap ng insurance payout.",
        "rider": "Karagdagang protection add-on katulad ng Critical Illness Rider, Hospital Income Rider, o Total Disability Waiver.",
        "lapse": "Kapag hindi nakabayad matapos ang 31-day grace period. Mawawala po ang inyong insurance coverage, pero pwede pong i-reinstate within 2 years.",
        "coverage": "Ang kabuuang death benefit o insurance amount (halimbawa: ₱1,000,000.00 base benefit).",
        "bank_referral": "Special endorsement mula sa inyong Bank Branch Manager para sa discounted premium rates at free financial planning session."
    },
    "faqs": {
        "grace_period": "Mayroon po kayong 31 days grace period mula sa due date bago po mag-lapse ang policy. Active pa rin po ang coverage sa loob ng 31 days na ito.",
        "reinstatement": "Kung nag-lapse po ang policy, maaari po itong i-reinstate within 2 years sa pag-fill out ng reinstatement form at pagbayad ng back premiums.",
        "rider_info": "Maaari po kayong magdagdag ng Critical Illness Rider para sa lump-sum cash benefit kapag na-diagnose ng major illness tulad ng cancer o heart attack.",
        "bank_referral_process": "Dahil VIP client po kayo ng aming partner bank, pwede po kayong mag-schedule ng personal meeting sa aming Resident Financial Advisor sa bangko."
    },
    "objections": {
        "too_expensive": "Naiintindihan ko po. Pwede po nating i-adjust ang monthly premium down to ₱1,500.00 / buwan o mag-adjust ng sum assured para pasok po sa inyong monthly budget.",
        "already_have_sss": "Maganda po na may SSS kayo! Pero ang SSS benefit po ay may limitasyon lang. Ang aming Life Policy po ay nagbibigay ng karagdagang ₱1,000,000.00 lump-sum cash protection at investment growth para sa inyong pamilya.",
        "hard_to_pay": "Mayroon po tayong hassle-free Auto-Debit arrangement sa inyong bank account, o kaya po ay GCash/Maya online paybill para hindi niyo na kailangang pumunta sa branch."
    },
    "escalation_contacts": {
        "role": "Senior Bancassurance Specialist",
        "department": "Bank Branch Financial Advisory Team",
        "sla": "Within 24 business hours or immediate phone transfer"
    }
}
