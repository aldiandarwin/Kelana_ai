# Session 12 - Demo and Submission Checklist

## So What?

Rekam bukti bahwa KelanaAI berjalan di URL publik, bukan hanya menampilkan kode
atau localhost. Video baru siap dikumpulkan setelah bisa diputar oleh penilai
melalui link Google Drive tanpa meminta akses.

**Status sekarang: panduan siap; deployment publik, video, link Drive, dan
pengumpulan LMS belum terverifikasi.**

## Sumber dan batas tugas

- Materi: `12 Graduation Day (1).pdf`, dengan prasyarat deployment Sesi 11.
- Instruksi LMS yang Aldian kirim: rekam video demo singkat, unggah ke Google Drive,
  ubah akses menjadi Anyone with the link, kirim tautan ke LMS.
- Deadline dari instruksi Aldian: **9 September 2026, 23:59 WIB**.
- Materi menyebut presentasi live 10-15 menit. Instruksi video yang diberikan
  tidak menetapkan durasi angka. Alur 5-7 menit di bawah adalah rekomendasi,
  bukan syarat resmi baru; ikuti batas terbaru jika LMS mencantumkannya.

## Sebelum menekan Record

- [ ] Selesaikan semua gate publik di `session-11-deployment.md`.
- [ ] Buka URL produksi Vercel dan lakukan satu rehearsal utuh.
- [ ] Gunakan akun demo dengan data non-sensitif; siapkan akun sebelum merekam
  jika proses registrasi tidak akan ditampilkan. Jangan tampilkan input password.
- [ ] Tutup `.env`, dashboard env cloud, terminal token, browser storage dan notifikasi pribadi.
- [ ] Pastikan microphone, suara, ukuran teks, kursor dan area rekaman jelas.
- [ ] Siapkan tiga tab: aplikasi publik, README arsitektur, dan dokumen sumber RAG.
- [ ] Cek ketersediaan Bedrock dan waktu tunggu dengan permintaan nyata.
  Jangan mengganti output nyata dengan teks hardcoded untuk terlihat berhasil.

## Alur rekaman yang disarankan

| Bagian | Aksi di layar | Narasi inti |
|---|---|---|
| 0:00-0:30 | About/halaman awal dan address bar Vercel | "Saya Aldian. KelanaAI membantu pengguna menyusun itinerary, mencari jawaban dari dokumen, dan melanjutkan diskusi perjalanan." |
| 0:30-1:10 | Register/login, lalu halaman planner | "Setiap pengguna memiliki trip dan percakapan sendiri. Backend memeriksa identitas dan pemilik data." |
| 1:10-2:20 | Isi Dhaka, Bangladesh; 3 hari; budget 900 USD sesuai label form; Solo. Generate dan buka hasil | "Aturan menghitung budget harian. Amazon Bedrock menyusun itinerary dari preferensi pengguna, lalu hasil disimpan." |
| 2:20-2:50 | My trips, buka detail, reload | "Hasil bukan sekadar teks sementara: itinerary tetap ada setelah halaman dibuka kembali." |
| 2:50-3:50 | Assistant, kirim pertanyaan sumber di bawah dan tampilkan sumber jawabannya | "RAG mengambil bagian dokumen terlebih dahulu. Sumber membantu memeriksa jawaban; isi brochure tetap perlu diperiksa kesegarannya." |
| 3:50-5:10 | Chat baru, dua turn, beri judul, reload, pilih lagi, lanjutkan | "Model dasarnya stateless. Backend menyimpan pesan lalu mengirimkan riwayat yang relevan pada setiap turn." |
| 5:10-5:50 | README atau About, jelaskan hosting terpisah | "Next.js di Vercel meneruskan permintaan ke FastAPI Cloud. Neon menyimpan data; backend memanggil Bedrock untuk AI." |
| 5:50-6:20 | Logout/akses private, lalu penutup | "Akses tetap terlindungi. Pengembangan berikutnya: menyatukan grounding dokumen dan memori chat dengan pengujian sumber yang lebih kuat." |

Durasi menyesuaikan latency. Potong bagian tunggu bila diperlukan dan beri label
bahwa waktu tunggu dipersingkat; jangan memotong kegagalan lalu menyebutnya berhasil.
Jika muncul error, perbaiki dan ulangi alur sebelum menyatakan aplikasi siap.

### Pertanyaan RAG siap pakai

Gunakan Q1 dari `knowledge/evaluation-questions.json` agar sumber dapat diperiksa:

> According to the Bangladesh Tourist Hand Book, how far is Khagrachari from
> Chattogram, which three rivers pass through the district, and what is its main attraction?

Kriteria dari fixture Sesi 9: jawaban menyebut 112 km; Chengi, Kasalong, Maini;
Alutila; serta sumber `bangladesh-tourist-handbook.pdf`. Ini isi dokumen acuan,
bukan jaminan kondisi perjalanan terkini. Jika sumber salah atau retrieval kosong,
berhenti dan cek ingestion Neon; jangan menarasikan jawaban itu sebagai grounded.

### Percakapan memori siap pakai

1. "Remember this two-day plan: Day 1 is Dhaka and Day 2 is Khulna. Confirm briefly."
2. "Which city did I assign to Day 2? Reply with only the city name."
3. Pastikan jawabannya **Khulna**, lalu ubah judul menjadi `Bangladesh demo`.
4. Reload, buka lagi percakapan yang sama, lalu tanya:
   "Which city did I assign to Day 1? Reply with only the city name."
5. Pastikan jawabannya **Dhaka**; tunjukkan judul, urutan pesan, timestamp dan indikator mengetik.

Ekspektasi di atas berasal dari fakta yang sengaja diberikan pada turn pertama,
bukan pengetahuan umum model. Catat output yang benar-benar muncul. Assistant
RAG dan Chat memori masih dua alur terpisah dalam implementasi saat ini.

## Upload, izin akses dan pengumpulan

- [ ] Simpan video final, contoh `KelanaAI_Aldian_Darwin_Putra_Session12.mp4`.
- [ ] Putar file dari awal sampai akhir: gambar terbaca, audio ada, tidak ada credential.
- [ ] Upload ke folder Google Drive yang tepat dan tunggu pemrosesan video selesai.
- [ ] Share -> General access -> **Anyone with the link** -> **Viewer**.
- [ ] Salin link file video, bukan link folder yang salah atau link localhost.
- [ ] Buka link melalui browser private/incognito atau akun lain yang tidak diberi
  akses khusus; pastikan video bisa diputar tanpa request access.
- [ ] Kirim link itu pada tugas Sesi 12 di LMS sebelum deadline.
- [ ] Pastikan LMS menunjukkan submission berhasil; simpan screenshot konfirmasi.

Permintaan mengunggah knowledge Sesi 9 tidak otomatis menentukan folder video
Sesi 12. Gunakan folder video yang dipilih Aldian atau yang ditentukan LMS.
Status "video diupload" belum sama dengan "sudah terkumpul".

## Isian bukti setelah benar-benar selesai

- URL frontend publik: **pending**
- URL backend publik: **pending**
- Commit/tag deployment terverifikasi: **pending**
- Hasil rehearsal dan tanggal: **pending**
- Link video Google Drive: **pending**
- Uji akses tanpa login: **pending**
- Konfirmasi submission LMS: **pending**

Checkpoint akhir `Complete KelanaAI AI Native Bootcamp` / `v1.0-bootcamp` dari
materi hanya dibuat setelah hasil final ditinjau dan Aldian mengizinkan commit/tag/push.
