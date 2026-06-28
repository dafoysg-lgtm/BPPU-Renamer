# ============================================================
#  SCRIPT RENAME MASSAL BPPU (Bukti Pemotongan PPh Unifikasi)
#  Format nama baru: [Nomor Surat]_[Nama Perusahaan]_[Tanggal].pdf
#  Contoh: 2603WVWFF_TETSU_ARMACO_MANDIRI_05-Mei-2026.pdf
# ============================================================
#
#  LANGKAH PENGGUNAAN:
#  1. Pastikan Python dan Poppler sudah terinstall (lihat Panduan)
#  2. Ubah FOLDER_PDF di bawah sesuai lokasi folder PDF kamu
#  3. Simpan file ini (Ctrl+S)
#  4. Buka PowerShell di folder ini → ketik: python .\rename_bppu_final.py
#  5. Cek hasil simulasi → jika sudah benar, ubah MODE_SIMULASI = False
#  6. Jalankan lagi → selesai!
#
# ============================================================

import os
import re
import subprocess
import sys
from pathlib import Path


# ── KONFIGURASI ──────────────────────────────────────────────
# Ganti path di bawah sesuai lokasi folder PDF kamu
# Contoh: r"C:\Users\YourName\Documents\BUPOT_2026"

FOLDER_PDF = r"C:\path\to\your\pdf\folder"

# Path ke pdftotext.exe — jika Poppler sudah di PATH, biarkan "pdftotext"
PDFTOTEXT_PATH = r"pdftotext"

# MODE SIMULASI:
#   True  = hanya tampilkan rencana rename, TIDAK mengubah file apapun
#   False = eksekusi sungguhan, file benar-benar di-rename
# SELALU jalankan True dulu sebelum False!
MODE_SIMULASI = True

# ─────────────────────────────────────────────────────────────


def ekstrak_teks_pdf(path_pdf):
    """Baca teks dari dalam file PDF menggunakan pdftotext."""
    try:
        result = subprocess.run(
            [PDFTOTEXT_PATH, "-layout", path_pdf, "-"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30
        )
        return result.stdout
    except FileNotFoundError:
        print("\n[ERROR] pdftotext tidak ditemukan!")
        print("Pastikan Poppler sudah diinstall dan sudah ditambahkan ke PATH Windows.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        return ""


def bersihkan_nama_file(nama):
    """Hapus karakter yang tidak boleh ada di nama file Windows."""
    nama = re.sub(r'[\\/:*?"<>|]', '', nama)
    nama = ' '.join(nama.split()).strip()
    return nama.replace(' ', '_')


def format_tanggal(tanggal_raw):
    """Ubah format tanggal: '05 Mei 2026' menjadi '05-Mei-2026'."""
    tanggal_raw = tanggal_raw.strip()
    match = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', tanggal_raw)
    if match:
        hari, bulan, tahun = match.groups()
        return f"{hari.zfill(2)}-{bulan}-{tahun}"
    return tanggal_raw.replace(' ', '-')


def parse_info_bppu(teks):
    """Ambil 3 informasi utama dari teks PDF BPPU."""
    info = {"nomor_surat": None, "nama_perusahaan": None, "tanggal": None}

    # Nomor Surat: token pertama di baris yang mengandung pola Masa Pajak (MM-YYYY)
    lines = teks.split('\n')
    for line in lines:
        if re.search(r'\b\d{2}-\d{4}\b', line):
            tokens = line.strip().split()
            if tokens and re.match(r'^[A-Z0-9]{5,20}$', tokens[0]):
                info["nomor_surat"] = tokens[0]
                break

    # Nama Perusahaan Pemotong: dari baris C.3
    m = re.search(r'C\.3\s+NAMA PEMOTONG DAN/ATAU PEMUNGUT\s*(?:PPh\s*)?:\s*(.+?)(?:\n|$)', teks)
    if m:
        info["nama_perusahaan"] = m.group(1).strip()

    # Tanggal: dari baris C.4
    m = re.search(r'C\.4\s+TANGGAL\s*:\s*(.+?)(?:\n|$)', teks)
    if m:
        info["tanggal"] = format_tanggal(m.group(1).strip())

    return info


def proses_semua_pdf(folder):
    """Proses semua PDF di folder dan subfolder."""
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"[ERROR] Folder tidak ditemukan: {folder}")
        sys.exit(1)

    # Cari semua PDF termasuk di subfolder
    semua_pdf = sorted(set(
        list(folder_path.rglob("*.pdf")) + list(folder_path.rglob("*.PDF"))
    ))

    if not semua_pdf:
        print(f"[INFO] Tidak ada file PDF ditemukan di: {folder}")
        return

    print(f"\n{'='*60}")
    print(f"  RENAME MASSAL BPPU")
    print(f"  Mode    : {'SIMULASI (tidak ada yg diubah)' if MODE_SIMULASI else 'EKSEKUSI SUNGGUHAN'}")
    print(f"  Folder  : {folder}")
    print(f"  Total   : {len(semua_pdf)} file PDF ditemukan")
    print(f"{'='*60}\n")

    sukses = 0; gagal = 0; dilewati = 0; log_gagal = []

    for i, path_pdf in enumerate(semua_pdf, 1):
        nama_asli = path_pdf.name
        subfolder = path_pdf.parent.name
        print(f"[{i:03d}/{len(semua_pdf)}] [{subfolder}] {nama_asli}")

        teks = ekstrak_teks_pdf(str(path_pdf))
        if not teks.strip():
            print(f"       GAGAL - tidak bisa baca teks PDF")
            log_gagal.append((f"{subfolder}/{nama_asli}", "Gagal baca teks"))
            gagal += 1; continue

        info = parse_info_bppu(teks)
        field_kosong = [k for k, v in info.items() if v is None]
        if field_kosong:
            print(f"       GAGAL - info tidak ditemukan: {', '.join(field_kosong)}")
            log_gagal.append((f"{subfolder}/{nama_asli}", f"Field kosong: {field_kosong}"))
            gagal += 1; continue

        # FORMAT NAMA BARU: [Nomor Surat]_[Nama Perusahaan]_[Tanggal].pdf
        n = bersihkan_nama_file(info["nomor_surat"])
        p = bersihkan_nama_file(info["nama_perusahaan"])
        t = bersihkan_nama_file(info["tanggal"])
        nama_baru = f"{n}_{p}_{t}.pdf"

        if nama_asli == nama_baru:
            print(f"       Sudah sesuai format, dilewati")
            dilewati += 1; continue

        path_baru = path_pdf.parent / nama_baru
        if path_baru.exists():
            nama_baru = f"{n}_{p}_{t}_DUPLIKAT.pdf"
            path_baru = path_pdf.parent / nama_baru

        print(f"       --> {nama_baru}")

        if not MODE_SIMULASI:
            try:
                path_pdf.rename(path_baru)
                sukses += 1
            except Exception as e:
                print(f"       ERROR rename: {e}")
                log_gagal.append((f"{subfolder}/{nama_asli}", str(e)))
                gagal += 1
        else:
            sukses += 1

    print(f"\n{'='*60}")
    print(f"  {'Siap di-rename' if MODE_SIMULASI else 'Berhasil rename'} : {sukses} file")
    print(f"  Dilewati              : {dilewati} file")
    print(f"  Gagal                 : {gagal} file")
    if log_gagal:
        print(f"\n  File yang gagal:")
        for nama, alasan in log_gagal:
            print(f"    - {nama}: {alasan}")
    if MODE_SIMULASI:
        print(f"\n  [!] INI SIMULASI. Ubah MODE_SIMULASI = False untuk eksekusi sungguhan.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    proses_semua_pdf(FOLDER_PDF)
