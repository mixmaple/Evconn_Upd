# Rekru Profile Web

Proyek web sederhana untuk menampilkan profil kelompok orang. Aplikasi memiliki dua halaman utama:

- `Home`: menampilkan judul, ringkasan, anggota unggulan, dan daftar profil anggota.
- `Dashboard`: mengelola konten home dan data anggota yang tersimpan di database SQL.

Stack yang digunakan:

- Python 3.12
- Flask
- PostgreSQL
- Docker Compose

## Akun Default Dashboard

Dashboard memiliki user default yang dibuat otomatis saat aplikasi pertama kali berjalan.

```text
URL: http://localhost:5000/dashboard
Username: admin
Password: admin12345
```

Nilai default ini bisa diubah melalui environment variable `DEFAULT_ADMIN_USERNAME` dan `DEFAULT_ADMIN_PASSWORD` di `docker-compose.yml`.

## Menjalankan Proyek

Pastikan Docker dan Docker Compose sudah terpasang, lalu jalankan:

```bash
docker compose up --build
```

Buka aplikasi di browser:

```text
Home: http://localhost:5000
Dashboard: http://localhost:5000/dashboard
```

Untuk menghentikan container:

```bash
docker compose down
```

Untuk menghapus database volume dan mengulang data dari awal:

```bash
docker compose down -v
```

## Struktur Proyek

```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── home.html
    ├── login.html
    ├── member_form.html
    └── partials/
        └── member_fields.html
```

## Fitur

- Tampilan home responsif dengan profil anggota.
- Dashboard login dengan session.
- CRUD data anggota.
- Form pengelolaan konten utama home.
- Data tersimpan di PostgreSQL melalui SQLAlchemy.
- Seed data otomatis untuk konten awal, anggota awal, dan user admin.

## Catatan Produksi

Sebelum dipakai di lingkungan produksi, ubah nilai `SECRET_KEY`, `DEFAULT_ADMIN_PASSWORD`, dan password PostgreSQL pada `docker-compose.yml`.
