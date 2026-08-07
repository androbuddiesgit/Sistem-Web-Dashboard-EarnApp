# EarnApp Cluster Dashboard V3 — Sultan Edition 👑

Sistem Manajemen Terpusat (Master Node) berbasis Web untuk memantau dan mengendalikan banyak bot Docker EarnApp yang tersebar di berbagai STB (Set-Top Box) Armbian dalam satu jaringan rumah. Dilengkapi dengan antarmuka **Glassmorphism** ultra-premium, sistem keamanan berlapis, dan fitur-fitur canggih tingkat enterprise.

## 🚀 Fitur Lengkap

### 🔒 Keamanan
- **Login Password:** Dashboard dilindungi sistem login. Password default: `admin` (wajib diganti setelah login pertama).
- **Enkripsi Fernet:** Semua password SSH STB dienkripsi menggunakan algoritma *Fernet* (AES-128-CBC) sebelum disimpan. Tidak ada lagi password mentah di `nodes.json`.
- **Cookie Auth:** Sesi login menggunakan token acak yang disimpan di HTTPOnly cookie.

### 📊 Pemantauan Real-Time
- **Global Analytics:** Total STB, bot aktif, bot berhenti, dan node offline dalam satu layar.
- **System Monitor:** CPU (%), RAM (%), dan Suhu STB secara *real-time*.
- **Auto-Refresh:** Dashboard memperbarui data setiap 30 detik secara otomatis.
- **Earnings Estimator:** Perkiraan pendapatan harian & bulanan berdasarkan jumlah bot aktif.

### 🚀 Deployment & Manipulasi
- **1-Click Deploy:** Tanam bot EarnApp baru dengan UUID otomatis dan *Force API Registration*.
- **Tanam Massal (Bulk Deploy):** Buat puluhan bot sekaligus dalam sekali klik.
- **Proxy Injection:** Suntikkan `HTTP_PROXY` berbeda-beda untuk setiap bot.
- **Ternak Siluman (HW Spoofing):** Kelabui server EarnApp dengan `/proc/cpuinfo` dan `/proc/meminfo` palsu.
- **Auto-Fix Network:** Perbaiki masalah Docker di Armbian (`ip_forward` & `iptables`) otomatis saat tambah STB atau via tombol.

### 🎨 Antarmuka Premium
- **Glassmorphism Dark Theme:** Desain web ultra-premium dengan efek kaca dan gradien dinamis.
- **Toast Notification:** Notifikasi elegan di pojok kanan bawah (bukan popup `alert()` jelek).
- **Glassmorphism Confirm Modal:** Dialog konfirmasi cantik bergaya kaca untuk aksi berbahaya.
- **Per-Bot Loading:** Spinner hanya muncul di baris bot yang sedang diproses, bukan seluruh tabel.
- **Mobile Responsive:** Tampilan menyesuaikan otomatis di HP, tablet, dan PC.
- **Bahasa Indonesia:** Seluruh antarmuka dalam Bahasa Indonesia yang konsisten.

### 🔧 Manajemen & Utilitas
- **Remote Control:** Start, Stop, Restart, Hapus, dan Ganti Nama bot dari jarak jauh.
- **Restart All Bots:** Restart semua bot di satu STB dalam sekali klik.
- **Live Log Viewer:** Pantau output terminal dari masing-masing bot.
- **Cek IP Publik:** Lihat IP publik yang digunakan setiap bot.
- **Ganti Nama STB & Bot:** Beri label pada setiap STB dan bot untuk manajemen yang rapi.

### 📡 Notifikasi & Backup
- **Telegram Bot Alert:** Kirim notifikasi ke Telegram saat ada bot mati atau STB offline.
- **Export/Import Config:** Backup dan restore konfigurasi `nodes.json` langsung dari Dashboard.
- **Activity Log:** Riwayat lengkap semua aktivitas (deploy, restart, hapus, dll).

### 🛡️ Sponsor & Referral
- **Welcome Modal:** Layar sambutan untuk pengguna baru dengan link referral.
- **Anti-Kiddies Obfuscation:** Link referral dienkripsi agar tidak bisa diganti oleh pengguna nakal.

## 💻 Panduan Instalasi

Jalankan perintah ini di **satu STB Master** saja:

```bash
wget -qO- https://raw.githubusercontent.com/androbuddiesgit/Sistem-Web-Dashboard-EarnApp/main/install.sh > /tmp/install.sh && sudo bash /tmp/install.sh
```

STB bawahan tidak perlu diinstal apa-apa. Cukup hubungkan via IP dan SSH Password melalui Dashboard.

## 🛠️ Cara Mengakses

Buka browser dan kunjungi:
```
http://<IP_STB_MASTER>:8080
```
Contoh: `http://192.168.1.10:8080`

**Login default:**
- Password: `admin`
- ⚠️ **Segera ganti password** melalui menu Pengaturan (ikon ⚙️ di navbar).

### Mengganti Port (Opsional)
```bash
sudo nano /etc/systemd/system/earnapp-dashboard.service
# Ubah --port 8080 menjadi port yang diinginkan
sudo systemctl daemon-reload
sudo systemctl restart earnapp-dashboard
```

## 📁 Struktur Proyek

```
earnapp-dashboard/
├── main.py                    # Entry point FastAPI + Auth Middleware
├── requirements.txt           # Dependencies (pinned versions)
├── install.sh                 # Auto-installer untuk Armbian
├── .gitignore
├── app/
│   ├── models.py              # Pydantic models
│   ├── core/
│   │   ├── auth.py            # Login, token, password management
│   │   ├── crypto.py          # Fernet encryption/decryption
│   │   ├── db.py              # Thread-safe JSON database
│   │   ├── logger.py          # Activity log writer
│   │   └── ssh.py             # SSH command executor
│   └── routers/
│       ├── auth.py            # Login/Logout/Change Password API
│       ├── bots.py            # Bot management API
│       ├── deploy.py          # Bulk deploy + proxy + spoofing API
│       ├── monitor.py         # System monitor API
│       ├── nodes.py           # STB node management API
│       └── settings.py        # Telegram, Export/Import, Earnings API
└── static/
    ├── index.html             # Frontend UI (Vue 3 + Tailwind)
    └── app.js                 # Frontend logic
```
