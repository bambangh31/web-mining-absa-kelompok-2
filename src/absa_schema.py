"""Skema ABSA bersama: kategori aspek, label, dan aturan agregasi.

Tugas proyek adalah aspect category sentiment analysis (ACSA) multi-aspek.
Setiap ulasan mendapat satu label untuk setiap kategori aspek. Satu ulasan
bisa memuat beberapa aspek dengan sentimen berbeda.

Anotasi rinci (lembar Excel) mencatat setiap penyebutan aspek: kata aspek
persis dari ulasan, kategori, sentimen, dan bukti. ``aggregate_mentions``
mengubah daftar penyebutan itu menjadi label per ulasan dengan aturan yang
sama untuk label manual dan label LLM, agar keduanya bisa dibandingkan.
"""

from collections import Counter

# `umum` harus tetap terakhir: aturan "umum hanya bila tidak ada aspek khusus"
# memakai ASPECTS[:-1] sebagai daftar aspek khusus.
ASPECTS = (
    "akun_login",
    "registrasi_data",
    "fitur_kesehatan",
    "performa",
    "kemudahan_penggunaan",
    "pembaruan_aplikasi",
    "layanan_pelanggan",
    "umum",
)
SPECIFIC = ASPECTS[:-1]
NONE = "tidak_disebut"
LABELS = (NONE, "positif", "negatif", "netral")
POLAR = ("positif", "negatif", "netral")

# Nama tampilan tanpa garis bawah untuk lembar Excel dan laporan.
ASPECT_NAMES = {a: a.replace("_", " ") for a in ASPECTS}
LABEL_NAMES = {label: label.replace("_", " ") for label in LABELS}
ASPECT_TITLES = {a: ASPECT_NAMES[a].title() for a in ASPECTS}

# Deskripsi singkat untuk masukan sentence-pair IndoBERT dan prompt LLM.
ASPECT_DESCRIPTIONS = {
    "akun_login": "akun dan login: masuk aplikasi, PIN, OTP, kode verifikasi, kata sandi, email atau nomor untuk masuk",
    "registrasi_data": "registrasi dan data diri: pendaftaran akun, NIK, nama, nomor telepon, profil, ubah data, data sudah terdaftar",
    "fitur_kesehatan": "fitur kesehatan: sertifikat dan riwayat vaksin, cek kesehatan gratis, hasil pemeriksaan, tiket, faskes, informasi kesehatan",
    "performa": "performa teknis: tidak bisa dibuka, error, force close, lambat, loading, stuck di logo, server, bug",
    "kemudahan_penggunaan": "kemudahan penggunaan: tampilan, alur, mudah, ribet, bingung, susah dipakai",
    "pembaruan_aplikasi": "pembaruan aplikasi: update dan versi, diminta update terus, perubahan dari PeduliLindungi ke SATUSEHAT",
    "layanan_pelanggan": "layanan pelanggan: customer service, helpdesk, aduan lewat email atau WhatsApp, tanggapan pengembang",
    "umum": "penilaian umum aplikasi secara keseluruhan tanpa aspek khusus",
}


def aspect_from_name(name):
    """Terima `akun_login`, `akun login`, atau `Akun Login`."""
    key = str(name).strip().lower().replace(" ", "_")
    if key not in ASPECTS:
        raise ValueError(f"Kategori aspek tidak dikenal: {name!r}")
    return key


def label_from_name(name):
    """Terima `tidak_disebut`, `tidak disebut`, atau huruf besar."""
    key = str(name).strip().lower().replace(" ", "_")
    if key not in LABELS:
        raise ValueError(f"Label tidak dikenal: {name!r}")
    return key


def empty_labels():
    return {a: NONE for a in ASPECTS}


def resolve_polarity(labels):
    """Satu label untuk beberapa penyebutan aspek yang sama.

    Netral hanya bila semua penyebutan netral. Bila ada pujian dan keluhan,
    pilih yang lebih banyak; seri dihitung negatif karena pada ulasan
    aplikasi keluhan menjadi informasi utama (aturan dicatat di panduan).
    """
    counts = Counter(labels)
    if not counts:
        return NONE
    positive, negative = counts["positif"], counts["negatif"]
    if positive == negative == 0:
        return "netral"
    return "positif" if positive > negative else "negatif"


def aggregate_mentions(mentions):
    """Daftar (aspek, label) satu ulasan -> label untuk kedelapan aspek."""
    grouped = {}
    for aspect, label in mentions:
        aspect, label = aspect_from_name(aspect), label_from_name(label)
        if label == NONE:
            continue
        grouped.setdefault(aspect, []).append(label)
    result = empty_labels()
    for aspect, labels in grouped.items():
        result[aspect] = resolve_polarity(labels)
    if any(result[a] != NONE for a in SPECIFIC):
        result["umum"] = NONE
    return result


def validate_labels(row, source="label"):
    for aspect in ASPECTS:
        if row.get(aspect) not in LABELS:
            raise ValueError(f"{source}: {row.get('reviewId')} / {aspect}: label kosong/tidak valid")
    if row["umum"] != NONE and any(row[a] != NONE for a in SPECIFIC):
        raise ValueError(f"{source}: {row.get('reviewId')}: umum tidak boleh bersamaan dengan aspek khusus")
