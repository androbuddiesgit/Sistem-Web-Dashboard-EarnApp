# EarnApp Cluster Dashboard

Sistem Manajemen Terpusat (Master Node) berbasis Web untuk memantau dan mengendalikan banyak bot Docker EarnApp yang tersebar di berbagai STB (Set-Top Box) Armbian dalam satu jaringan rumah.

## 🚀 Fitur Utama

- **Multi-Node Cluster:** Tambahkan banyak STB ke dalam satu layar pemantauan via SSH.
- **Monitoring Real-Time:** Lihat status *Online/Offline* dan jumlah bot yang berjalan di setiap STB.
- **1-Click Auto Deploy (Bypass SSL):** Tanam bot EarnApp baru ke STB secara otomatis (termasuk *auto-generate UUID* dan *Force API Registration* via Curl) tanpa perlu berurusan dengan masalah sertifikat `AxiosError`.
- **Remote Control:** Start, Stop, Restart, dan Delete (rm -f) bot EarnApp dari jarak jauh.
- **Live Log Viewer:** Pantau *terminal output* dari masing-masing bot.
- **Super Ringan:** Dibangun menggunakan Python FastAPI dan Vanilla JS (tanpa Node.js Build), sehingga STB Anda tidak akan panas atau kehabisan RAM.

## 💻 Panduan Instalasi (Untuk STB Master)

Anda hanya perlu menginstal Dashboard ini di **satu STB saja** (sebagai Master). STB lain cukup dihubungkan via IP dan SSH Password melalui tampilan Web.

Jalankan perintah ajaib ini di terminal STB Master Anda:

```bash
wget -qO- https://raw.githubusercontent.com/androbuddiesgit/Sistem-Web-Dashboard-EarnApp/main/install.sh > /tmp/install.sh && sudo bash /tmp/install.sh
```

## 🛠️ Cara Mengakses Web Dashboard

Setelah instalasi selesai, buka *browser* di PC atau HP Anda, lalu ketikkan Alamat IP dari STB Master tersebut diikuti dengan port `8080`.

Contoh:
`http://192.168.1.10:8080`

## 📸 Tampilan Antarmuka
Sistem ini menggunakan desain gaya modern **Glassmorphism** dengan TailwindCSS dan Mode Gelap (Dark Mode) bawaan.

*(Dikembangkan khusus untuk mengatasi masalah Sertifikat SSL dan Manajemen Cgroup pada Kernel STB lama).*
