"""
Concrete Localization Examples for Philippines and Indonesia Markets.
Demonstrates specific differences in wording, politeness, terminology, code-switching,
and payment/date/amount explanations compared to generic literal translations.
"""

CONCRETE_LOCALIZATION_EXAMPLES = {
    "philippines": [
        {
            "scenario": "1. Premium Payment Reminder & Payment Channel Explanation",
            "generic_translation": "Your premium of 2500 pesos is due on October 15. Please pay using bank account.",
            "localized_taglish": "Magandang araw po! Ipaalala lang po namin na ang inyong policy premium na ₱2,500.00 Pesos ay due na po sa Oktubre 15, 2026. Pwede niyo pong bayaran sa GCash, Maya, o via Auto-Debit Arrangement (ADA) sa inyong BDO/BPI savings account po.",
            "differences_explained": {
                "wording": "Uses warm greeting ('Magandang araw po!') and polite framing ('Ipaalala lang po namin').",
                "politeness": "Consistently incorporates 'po' honorific register.",
                "terminology": "Uses domain terms 'policy premium', 'due date', 'Auto-Debit Arrangement (ADA)'.",
                "code_switching": "Natural Manila Taglish seamlessly combining Filipino syntax with banking terms.",
                "payment_date_amount": "Formats ₱2,500.00 Pesos, date 'Oktubre 15, 2026', and mentions local channels (GCash, Maya, ADA)."
            }
        },
        {
            "scenario": "2. Objection Handling: 'Mahal ang premium' (Price Objection)",
            "generic_translation": "The insurance price is not expensive because it has good coverage.",
            "localized_taglish": "Naiintindihan ko po ang inyong alalahanin sa budget. Ang maganda po sa aming VUL Life Plan, pwede po nating i-adjust ang buwanang premium down to ₱1,500.00 / buwan para pasok po sa inyong monthly savings habang buo pa rin ang inyong ₱1,000,000.00 coverage protection.",
            "differences_explained": {
                "wording": "Empathizes first ('Naiintindihan ko po ang inyong alalahanin') before presenting flexible solution.",
                "politeness": "Empathetic customer service tone with 'po'.",
                "terminology": "Uses 'VUL Life Plan', 'buwanang premium', 'coverage protection', 'sum assured'.",
                "code_switching": "Taglish financial negotiation language.",
                "payment_date_amount": "Explores flexible tiering from ₱2,500 to ₱1,500 monthly."
            }
        },
        {
            "scenario": "3. Human Escalation Request",
            "generic_translation": "I will connect you to a human manager now.",
            "localized_taglish": "Naiintindihan ko po. I-transfer ko po ang inyong tawag sa aming Senior Bancassurance Specialist sa pinakamalapit na BDO/BPI partner branch para mas maasikaso po kayo nang personal. Sandali lamang po.",
            "differences_explained": {
                "wording": "Reassures local branch presence and personal service.",
                "politeness": "Respectful deferral and hold reassurance ('Sandali lamang po').",
                "terminology": "Refers to 'Senior Bancassurance Specialist' and 'partner bank branch'.",
                "code_switching": "Professional banking Taglish.",
                "payment_date_amount": "N/A - focuses on escalation protocol."
            }
        }
    ],
    "indonesia": [
        {
            "scenario": "1. Installment & Late Fee Explanation (Pembiayaan & Denda)",
            "generic_translation": "Your installment is 450000 rupiah due October 15. Late fee is 0.5 percent per day.",
            "localized_indonesian": "Selamat siang Bapak/Ibu. Kami menginfokan bahwa angsuran pembiayaan kendaraan Bapak/Ibu sebesar Rp 450.000,- akan jatuh tempo pada 15 Oktober 2026. Untuk menghindari denda keterlambatan sebesar 0.5% per hari, pembayaran dapat dilakukan via M-Banking Virtual Account BCA/Mandiri atau di Indomaret/Alfamart terdekat ya Pak/Bu.",
            "differences_explained": {
                "wording": "Uses formal multifinance opening and respectful closing particle 'ya Pak/Bu'.",
                "politeness": "Strict adherence to Bapak/Ibu honorifics and 'santun' customer service register.",
                "terminology": "Uses 'angsuran pembiayaan', 'jatuh tempo', 'denda keterlambatan', 'Virtual Account'.",
                "code_switching": "Formal Bahasa Indonesia with natural financial English loanwords (Virtual Account, M-Banking).",
                "payment_date_amount": "Formats Rp 450.000,-, date '15 Oktober 2026', and mentions local channels (M-Banking VA, Indomaret, Alfamart)."
            }
        },
        {
            "scenario": "2. Regional Javanese Accent/Dialect Objection Handling",
            "generic_translation": "I cannot understand your regional dialect.",
            "localized_indonesian": "Matur nuwun Pak. Mboten menapa-napa (tidak apa-apa) Pak, kami sangat memahami maksud Bapak. Terkait angsuran yang masih kurang Rp 200.000,-, Bapak tetap dapat melakukan pembayaran parsial terlebih dahulu melalui Alfamart agar terhindar dari akumulasi denda yang lebih besar ya Pak.",
            "differences_explained": {
                "wording": "Acknowledges regional Javanese input with polite Javanese bridge ('Matur nuwun Pak, Mboten menapa-napa') before explaining partial payment.",
                "politeness": "Culturally sensitive respect to regional speakers outside Jakarta.",
                "terminology": "Uses 'angsuran', 'pembayaran parsial', 'akumulasi denda'.",
                "code_switching": "Code-bridging between Javanese politeness phrases and standard Indonesian consumer finance terms.",
                "payment_date_amount": "Handles partial payment of Rp 200.000,-."
            }
        },
        {
            "scenario": "3. Human Escalation Request",
            "generic_translation": "Please wait for customer support officer.",
            "localized_indonesian": "Baik Bapak/Ibu, saya bantu hubungkan langsung dengan Customer Service Officer (CSO) kami di kantor cabang terdekat untuk penanganan pembiayaan lebih lanjut. Mohon tunggu sebentar ya Pak/Bu.",
            "differences_explained": {
                "wording": "Clear, polite transfer sentence with local branch reassurance.",
                "politeness": "Repetitive honorific reinforcement ('Bapak/Ibu', 'Pak/Bu').",
                "terminology": "Refers to 'Customer Service Officer (CSO)' and 'kantor cabang terdekat'.",
                "code_switching": "Formal Indonesian customer care phrasing.",
                "payment_date_amount": "N/A - focuses on escalation protocol."
            }
        }
    ]
}
