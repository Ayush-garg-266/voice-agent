"""
Indonesia Multifinance / Consumer Finance Domain Knowledge Base.
Contains loan terms, DP specs, late fees (denda), payment channels, FAQs, and objections.
"""

ID_MULTIFINANCE_KB = {
    "company_name": "Nusa Finance Multifinance",
    "supported_products": ["Pembiayaan Motor (Motorcycle Loan)", "Pembiayaan Mobil (Car Loan)", "Dana Tunai BPKB"],
    "min_dp_percent": 15.0,  # 15% DP minimum
    "tenor_options": [12, 24, 36, 48],  # months
    "late_fee_rate": "0.5% per hari dari nilai angsuran bulanan",
    "grace_period_days": 3,
    "finance_terms": {
        "cicilan": "Pembayaran kewajiban angsuran bulanan pembiayaan.",
        "tenor": "Jangka waktu pembiayaan dalam hitungan bulan (misal: 12, 24, atau 36 bulan).",
        "denda": "Biaya keterlambatan sebesar 0.5% per hari jika pembayaran melewati tanggal jatuh tempo.",
        "DP": "Down Payment atau uang muka minimal 15% dari harga OTR kendaraan.",
        "jatuh_tempo": "Tanggal batas akhir pembayaran angsuran setiap bulannya (misal: tanggal 10 atau 20).",
        "angsuran": "Besaran tagihan tetap yang wajib dibayarkan nasabah setiap bulan.",
        "pembiayaan": "Fasilitas pinjaman kredit konsumen resmi yang diawasi OJK."
    },
    "faqs": {
        "denda_policy": "Biaya denda keterlambatan adalah 0.5% per hari dari jumlah angsuran bulanan. Kami menyarankan pembayaran dilakukan sebelum tanggal jatuh tempo untuk menghindari denda.",
        "dp_requirement": "Minimal DP kendaraan bermotor adalah 15% dari harga OTR. DP dapat dibayarkan saat persetujuan aplikasi pembiayaan.",
        "payment_channels": "Pembayaran angsuran dapat dilakukan melalui M-Banking (Virtual Account BCA/Mandiri), Indomaret, Alfamart, atau QRIS."
    },
    "objections": {
        "denda_too_high": "Kami memahami kekhawatiran Bapak/Ibu. Denda 0.5% per hari dihitung transparan dari nilai angsuran bulanan. Agar terhindar dari denda, Bapak/Ibu bisa mengaktifkan layanan autodebet M-Banking.",
        "dp_too_high": "Untuk program promo bulan ini, Bapak/Ibu bisa mengambil skema DP ringan mulai dari 10% atau opsi subsidi DP khusus nasabah setia.",
        "want_tenor_extension": "Perpanjangan tenor dapat diajukan melalui proses restrukturisasi pembiayaan dengan menghubungi tim Customer Service di kantor cabang terdekat."
    },
    "regional_accents": {
        "javanese_medok": {
            "features": "Penggunaan fonem b/d/g yang tebal, partikel 'tah', 'ta', kata bentukan seperti 'piye', 'pripun', 'sampeyan', 'mboten', 'nggih'.",
            "syntax_adaptation": "Dapat mengenali kata 'piye angsuranku' sebagai 'bagaimana status angsuran saya'.",
            "limitation_note": "Model ASR standar mungkin mengalami miss-transcription pada kata slang Jawa kasar/dialek lokal ekstrim."
        },
        "sundanese": {
            "features": "Pertukaran bunyi 'f/v' menjadi 'p', partikel 'teh', 'mah', 'pisan'.",
            "syntax_adaptation": "Dapat mengenali 'cicilan pirtual account teh' sebagai 'cicilan via Virtual Account'.",
            "limitation_note": "Aksen Sunda secara umum dapat ditranskripsikan dengan baik oleh ASR Bahasa Indonesia modern."
        }
    },
    "escalation_contacts": {
        "role": "Customer Service Officer (CSO)",
        "department": "Kantor Cabang Multifinance Terdekat",
        "sla": "Pengalihan telepon langsung atau max 1 jam kerja"
    }
}
