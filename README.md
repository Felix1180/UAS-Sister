# 📊 Distributed Pub-Sub Log Aggregator

Sistem ini adalah solusi aggregator log multi-service terdistribusi yang dibangun untuk memenuhi tugas UAS Sistem Terdistribusi. Sistem mengutamakan **Idempotency**, **Strong Deduplication**, dan **Concurrency Control** guna menjamin konsistensi data pada beban trafik tinggi.

---

## 🏗️ Arsitektur Layanan

Sistem berjalan sepenuhnya di atas **Docker Compose** dalam jaringan lokal yang terisolasi (Bab 10).

### Komponen Utama:

- **Aggregator Service (FastAPI)**: Bertindak sebagai _subscriber_ pusat yang menerima log, melakukan validasi skema (Pydantic), dan menangani logika deduplikasi.
- **Storage Service (PostgreSQL 16)**: Database relasional untuk penyimpanan persisten dengan dukungan transaksi ACID untuk mencegah _race condition_.
- **Publisher Service**: Simulator asinkron yang mengirimkan beban ≥ 20.000 event dengan tingkat duplikasi sebesar 30%.
- **Tests Service**: Container khusus untuk menjalankan 12-20 unit & integration tests secara otomatis.

---

## ✨ Fitur Utama

1.  **Idempotent Consumer**: Menjamin bahwa pengiriman log dengan `event_id` yang sama hanya diproses satu kali (Bab 3 & 7).
2.  **Atomic Deduplication**: Menggunakan strategi `INSERT ... ON CONFLICT DO NOTHING` untuk memastikan pengecekan dan penulisan data bersifat atomik (Bab 9).
3.  **Crash Tolerance**: Data tetap aman meski container dihapus berkat penggunaan **Named Volumes** `pg_data` (Bab 11).
4.  **Transaction Control**: Implementasi level isolasi _Read Committed_ untuk mencegah fenomena _lost-update_ saat beban konkuren tinggi (Bab 8).
5.  **Observability**: Metrik real-time melalui endpoint `/stats` untuk memantau trafik masuk dan jumlah duplikasi yang dibuang.

---

## 🚀 Cara Menjalankan

### 1. Prasyarat

- Docker & Docker Compose terinstal di mesin lokal.

### 2. Jalankan Sistem

Gunakan perintah berikut untuk membersihkan state lama dan membangun sistem dari awal:

```bash
docker compose down -v
docker compose up --build
```

### 3. Akses Layanan

- **Root API (Health Check)**
  http://localhost:8080/

- **Statistik Sistem**
  http://localhost:8080/stats

- **Dokumentasi API (Swagger UI)**
  http://localhost:8080/docs

---

## 🔌 Endpoint API

| Method | Endpoint   | Deskripsi                                                               |
| ------ | ---------- | ----------------------------------------------------------------------- |
| GET    | `/`        | Health check dan informasi readiness service                            |
| POST   | `/publish` | Endpoint untuk mengirim log (mendukung idempotensi & batch)             |
| GET    | `/stats`   | Menampilkan metrik: `received`, `unique_processed`, `duplicate_dropped` |
| GET    | `/events`  | Mengambil daftar log unik (mendukung filter `?topic=`)                  |

```

```
