# EarnApp Cluster Dashboard V2 Master

Sistem Manajemen Terpusat (Master Node) berbasis Web untuk memantau dan mengendalikan banyak bot Docker EarnApp yang tersebar di berbagai STB (Set-Top Box) Armbian dalam satu jaringan rumah. Dilengkapi dengan antarmuka **Glassmorphism** modern, pemantauan *real-time*, dan sistem Bypass API tingkat tinggi.

## 🚀 Fitur Baru di V2 (Mega Update)

- **Modular Backend:** Dibangun menggunakan struktur FastAPI yang bersih dan ringan agar penggunaan CPU/RAM di STB master tetap hemat.
- **Global Analytics Dashboard:** Lihat total STB, bot berjalan, bot berhenti, dan node mati dalam satu layar raksasa.
- **Hardware System Monitor:** Pemantauan Suhu (Temperature), RAM, dan CPU STB secara *real-time* langsung dari Dashboard.
- **Bulk Deploy & Proxy Injection (Tanam Massal):** Membuat puluhan kontainer bot sekaligus dalam sekali klik dan langsung menyuntikkan `HTTP_PROXY` yang berbeda-beda untuk tiap bot.
- **Ternak Siluman (Hardware Spoofing):** Mengelabui server EarnApp dengan menyuntikkan file `/proc/cpuinfo` dan `/proc/meminfo` palsu (virtual) ke dalam kontainer.
- **Auto-Fix Network:** Memperbaiki masalah STB *no internet* akibat bug Docker di Armbian (`ip_forward=1` & `iptables ACCEPT`) otomatis atau via tombol "Fix Net".
- **Dynamic Port:** Port bisa diatur sesuka hati via parameter `--port` agar tidak bentrok dengan Mikrotik/Panel lain.
- **Sponsor/Referral Anti-Kiddies:** Dilengkapi *Welcome Modal* untuk mencari *referral* baru dengan link terenkripsi (Anti *Inspect Element*).
- **Mobile-First Responsive:** Tampilan Web sangat cantik, bisa dibuka dari PC, Laptop, maupun *Smartphone*.
- **Remote Action:** Ganti Nama STB, Ganti Nama Bot, Restart Semua Bot, Hapus Bot (rm -f), dan Live Logs Viewer.

## 💻 Panduan Instalasi (Untuk STB Master)

Anda hanya perlu menginstal Dashboard ini di **satu STB saja** (sebagai Master). STB bawahan (budak) lainnya tidak perlu diinstal apa-apa, cukup dihubungkan via IP dan SSH Password melalui tampilan Web Master.

Jalankan perintah ajaib ini di terminal STB Master Anda:

```bash
wget -qO- https://raw.githubusercontent.com/androbuddiesgit/Sistem-Web-Dashboard-EarnApp/main/install.sh > /tmp/install.sh && sudo bash /tmp/install.sh
```

## 🛠️ Cara Mengakses Web Dashboard

Secara *default*, Web Dashboard berjalan di port `8000`. Buka *browser* dan kunjungi:
`http://<IP_STB_MASTER>:8000` 
*(Contoh: `http://192.168.1.10:8000`)*

### Mengganti Port (Opsional)
Jika port 8000 bentrok dengan aplikasi lain, edit file *service*:
```bash
sudo nano /etc/systemd/system/earnapp-dashboard.service
```
Pada bagian `ExecStart`, tambahkan `--port 8080` di akhir baris:
```ini
ExecStart=/usr/bin/python3 /opt/earnapp-dashboard/main.py --port 8080
```
Lalu simpan dan *restart* sistem:
```bash
sudo systemctl daemon-reload
sudo systemctl restart earnapp-dashboard
```

## 📸 Antarmuka V2.0 Glassmorphism
Sistem ini menggunakan desain web ultra-premium bergaya **Glassmorphism** dengan bantuan *Vue.js 3* dan *Tailwind CSS*. Sangat memanjakan mata, enteng, dan responsif.
