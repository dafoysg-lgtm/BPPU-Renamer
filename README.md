# BPPU Renamer 🗂️
> Bulk PDF renaming automation for tax document archiving — 826 files in 2 minutes.

## Problem
Di divisi pajak PT Indocement Tunggal Prakarsa Tbk, proses pengarsipan 
Bukti Potong (BPPU) dari Coretax dilakukan secara manual:

- Setiap file PDF harus dibuka satu per satu
- 3 komponen (Nomor Surat, Nama Perusahaan, Tanggal) dicatat manual
- File di-rename satu per satu sesuai format standar
- Preview mode tidak support copy-paste, jadi harus diketik ulang

Dengan ratusan file per periode, proses ini memakan **9+ jam** 
dan rentan human error.

## Solution
Mengidentifikasi bahwa PDF dari Coretax bersifat *text-selectable* 
(bukan scanned), sehingga tidak butuh OCR.

Workflow otomasi:
1. Buka folder bulan yang ditentukan
2. Extract 3 komponen kunci dari tiap PDF via Poppler
3. Generate nama file baru sesuai format: `NomorSurat_NamaPerusahaan_Tanggal`
4. Rename otomatis — file yang sudah diproses di-skip (logged)

## Impact
|       Metrik        | Manual    | BPPU Renamer|
|------------------- -|-------------------------|
| Total file diproses | 826 files | 826 files   |
| Waktu pengerjaan    | ~9 jam    |  ~2 menit   |
| Risiko human error  | Tinggi    |    ~1%      |

## Tech Stack
- Python
- Poppler (`pdftotext.exe`) — ekstraksi teks dari PDF
- PowerShell — eksekusi script di environment kantor

## How It Works
```
Folder Bulan
    └── PDF Files
          ↓
    [pdftotext.exe] ← Poppler
          ↓
    Extract: Nomor Surat + Nama Perusahaan + Tanggal
          ↓
    Generate new filename
          ↓
    Rename + Log (skip if already renamed)
