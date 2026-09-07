import requests
from bs4 import BeautifulSoup, Tag
import urllib3
from datetime import datetime as date
from datetime import timezone, timedelta
import os
import logging
import json
import time
from typing import cast

from fastapi import FastAPI

# Menyembunyikan peringatan keamanan SSL karena kita menggunakan verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

WIB = timezone(timedelta(hours=7))
sekarang = date.now(WIB)
istirahat = 16
bangun = 7

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

USERNAME_1 = os.environ["USERNAME_1"] # Akun Rifty
PASSWORD_1 = os.environ["PASSWORD_1"]
USERNAME_2 = os.environ["USERNAME_2"] # Akun Hisyam
PASSWORD_2 = os.environ["PASSWORD_2"]

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

# Timeout tiap call ke Telegram API.
# Fungsi serverless (Vercel Hobby) dibunuh di 10 detik,
# jadi tiap request harus selesai jauh sebelum itu.
HTTP_TIMEOUT = 8

# Logging configuration
LOG_LEVEL = "INFO"
TG_LOG_ENABLED = True
TG_LOG_MIN_INTERVAL_SYSTEM = 0.1
TG_LOG_MIN_INTERVAL_USER = 1.0

# Rate-limited Telegram log sender (separate buckets per category)
_last_tg_log_system = 0.0
_last_tg_log_user = 0.0

def tg_log(text: str, category: str = "user"):
    """Send log to Telegram with per-category rate limiting.
    
    category:
      - "system": triggered/completed/error (interval ~0.1s)
      - "user":   per-presensi notifications (interval ~1s)
    """
    global _last_tg_log_system, _last_tg_log_user
    if not TG_LOG_ENABLED:
        return
    if category == "system":
        last_log = _last_tg_log_system
        min_interval = TG_LOG_MIN_INTERVAL_SYSTEM
    else:
        last_log = _last_tg_log_user
        min_interval = TG_LOG_MIN_INTERVAL_USER
    now = time.time()
    if now - last_log < min_interval:
        return
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text[:4000]},
            timeout=HTTP_TIMEOUT
        )
        if category == "system":
            _last_tg_log_system = now
        else:
            _last_tg_log_user = now
    except Exception as e:
        logger.warning('{"event":"tg_log_failed","error":%s}', json.dumps(str(e)))

# JSON logger setup for Vercel
logging.basicConfig(
    level=LOG_LEVEL,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":%(message)s}',
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

@app.get("/api")
def home():
    return {
        "status": "success",
        "message": "Telegram Scanner Bot API is running"
    }
    

# Data Jadwal Kuliah
users = [
    {
        "username": USERNAME_1,
        "password": PASSWORD_1,
        "jadwal": [
            {
                "mata_kuliah": "Sistem Operasi",
                "id": 812101,
                "hari": 1,
                "jam": 10,
                "menit": 0
            },
            {
                "mata_kuliah": "Prak IOT",
                "id": 814196,
                "hari": 1,
                "jam": 8,
                "menit": 0
            },
            {
                "mata_kuliah": "Prak DS",
                "id": 819138,
                "hari": 2,
                "jam": 8,
                "menit": 0
            },
            {
                "mata_kuliah": "Kriptografi",
                "id": 812142,
                "hari": 2,
                "jam": 12,
                "menit": 30
            },
            {
                "mata_kuliah": "Data Science",
                "id": 809066,
                "hari": 3,
                "jam": 10,
                "menit": 0
            },
            {
                "mata_kuliah": "Pengamanan Sistem Jaringan",
                "id": 799728,
                "hari": 3,
                "jam": 12,
                "menit": 45
            },
            {
                "mata_kuliah": "Manajemen Proyek Perangkat Lunak",
                "id": 808322,
                "hari": 3,
                "jam": 15,
                "menit": 0
            },
            {
                "mata_kuliah": "Internet of Thinks",
                "id": 808954,
                "hari": 4,
                "jam": 10,
                "menit": 0
            },
            {
                "mata_kuliah": "Pengolahan Citra",
                "id": 808663,
                "hari": 4,
                "jam": 13,
                "menit": 0
            },
            {
                "mata_kuliah": "Penginderaan Jarak Jauh",
                "id": 816759,
                "hari": 4,
                "jam": 15,
                "menit": 30
            },
            {
                "mata_kuliah": "Kapita Selekta",
                "id": 808956,
                "hari": 5,
                "jam": 7,
                "menit": 30
            }
        ]
    },
    {
        "username": USERNAME_2,
        "password": PASSWORD_2,
        "jadwal": [ 
            {
            "mata_kuliah": "Kriptografi",
            "id": 801568,
            "hari": 0,
            "jam": 7,
            "menit": 30
            },
            {
            "mata_kuliah": "Praktikum Internet of Things (IoT)",
            "id": 818499,
            "hari": 0,
            "jam": 10,
            "menit": 30
            },
            {
            "mata_kuliah": "Sistem Operasi",
            "id": 812101,
            "hari": 1,
            "jam": 10,
            "menit": 0
            },
            {
            "mata_kuliah": "Pembelajaran Mesin",
            "id": 809914,
            "hari": 3,
            "jam": 7,
            "menit": 30
            },
            {
            "mata_kuliah": "Praktikum Data Science",
            "id": 817796,
            "hari": 3,
            "jam": 13,
            "menit": 0
            },
            {
            "mata_kuliah": "Manajemen Proyek Perangkat Lunak",
            "id": 808322,
            "hari": 3,
            "jam": 15,
            "menit": 0
            },
            {
            "mata_kuliah": "Data Science",
            "id": 811113,
            "hari": 4,
            "jam": 7,
            "menit": 30
            },
            {
            "mata_kuliah": "Internet of Things (IoT)",
            "id": 808954,
            "hari": 4,
            "jam": 10,
            "menit": 0
            },
            {
            "mata_kuliah": "Penginderaan Jarak Jauh",
            "id": 811820,
            "hari": 4,
            "jam": 15,
            "menit": 30
            },
            {
            "mata_kuliah": "Kapita Selekta",
            "id": 808956,
            "hari": 5,
            "jam": 7,
            "menit": 30
            }
        ]
    }
]

def jalankan_bot_presensi(username, password, id_modul_presensi, mata_kuliah, username_label):
    try:
        logger.info('{"event":"presensi_start"}')
        
        # Membuat session agar cookies/sesi tetap tersimpan di setiap request
        session = requests.Session()
        login_url = "https://spada.upnyk.ac.id/login/index.php"
        
        # ==============================================================
        # TAHAP 1: MENGAMBIL LOGIN TOKEN (CSRF Protection)
        # ==============================================================
        logger.info('{"step":1,"msg":"akses halaman login"}')
        response_get = session.get(login_url, verify=False)
        soup_login = BeautifulSoup(response_get.text, 'html.parser')
        
        token_element = soup_login.find('input', {'name': 'logintoken'})
        if not token_element or not isinstance(token_element, Tag):
            logger.error('{"error":"logintoken tidak ditemukan"}')
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Logintoken tidak ditemukan", category="user")
            return
        
        login_token = token_element.get('value')
        logger.info('{"step":1,"msg":"logintoken didapat","token":%s}', json.dumps(login_token))

        # ==============================================================
        # TAHAP 2: EKSEKUSI LOGIN
        # ==============================================================
        logger.info('{"step":2,"msg":"kirim kredensial"}')
        payload_login = {
            "username": username,
            "password": password,
            "logintoken": login_token
        }
        
        response_post = session.post(login_url, data=payload_login, verify=False)
        
        if "login" in response_post.url:
            logger.error('{"error":"login ditolak, cek username/password"}')
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Login gagal (cek username/password)", category="user")
            return
        logger.info('{"step":2,"msg":"login berhasil"}')

        # ==============================================================
        # TAHAP 3: MENGAMBIL SESSKEY DARI DASHBOARD
        # ==============================================================
        logger.info('{"step":3,"msg":"ekstrak sesskey"}')
        soup_dash = BeautifulSoup(response_post.text, 'html.parser')
        
        # Mencari sesskey dari URL logout (Pola umum Moodle)
        logout_link = None
        for a in soup_dash.find_all('a', href=True):
            if isinstance(a, Tag):
                href = a.get('href') or ''
                if "logout.php?sesskey=" in href:
                    logout_link = a
                    break
        if logout_link:
            href_val = cast(str, logout_link.get('href', ''))
            sesskey = href_val.split('sesskey=')[1]
            logger.info('{"step":3,"msg":"sesskey didapat","sesskey":%s}', json.dumps(sesskey))
        else:
            logger.error('{"error":"sesskey tidak ditemukan di dashboard"}')
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Sesskey tidak ditemukan di dashboard", category="user")
            return

        # ==============================================================
        # TAHAP 4: MENUJU MODUL PRESENSI & AMBIL DATA DINAMIS
        # ==============================================================
        # Menggunakan ID modul presensi (Contoh Data Science: 809066)
        url_view = f"https://spada.upnyk.ac.id/mod/attendance/view.php?id={id_modul_presensi}"
        logger.info('{"step":4,"msg":"buka modul presensi","id_modul":%d}', id_modul_presensi)
        
        response_view = session.get(url_view, verify=False)
        soup_view = BeautifulSoup(response_view.text, 'html.parser')
        
        # Mencari tombol "Ajukan Presensi" yang mengandung sessid hari ini
        link_eksekusi = None
        for a in soup_view.find_all('a', href=True):
            if isinstance(a, Tag):
                href = a.get('href') or ''
                if "attendance.php?sessid=" in href:
                    link_eksekusi = a
                    break

        if not link_eksekusi:
            logger.error('{"error":"tombol ajukan presensi tidak ditemukan"}')
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Tombol ajukan presensi tidak ditemukan (belum buka/jadwal salah)", category="user")
            return
        
        href_val = cast(str, link_eksekusi.get('href', ''))
        url_form_presensi = href_val
        # Parsing ID sesi (sessid) dari URL
        sessid_hari_ini = href_val.split('sessid=')[1].split('&')[0]
        logger.info('{"step":4,"msg":"jadwal aktif","sessid":%s}', json.dumps(sessid_hari_ini))

        # ==============================================================
        # TAHAP 5: SUBMIT KEHADIRAN (Bypass Form & Tembak POST)
        # ==============================================================
        logger.info('{"step":5,"msg":"submit kehadiran"}')
        
        # Akses form presensi untuk mencari ID status (radio button)
        response_form = session.get(url_form_presensi, verify=False)
        soup_form = BeautifulSoup(response_form.text, 'html.parser')
        
        # Secara otomatis mengambil 'value' dari radio button PERTAMA 
        # (Di Moodle, opsi pertama biasanya adalah "Hadir" / "Present")
        radio_hadir = soup_form.find('input', {'type': 'radio', 'name': 'status'})
        
        if not radio_hadir or not isinstance(radio_hadir, Tag):
            logger.error('{"error":"opsi status kehadiran tidak ditemukan"}')
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Opsi status kehadiran tidak ditemukan", category="user")
            return
            
        status_id = radio_hadir.get('value')
        logger.info('{"step":5,"msg":"status hadir didapat","status_id":%s}', json.dumps(status_id))

        # Merakit payload final sesuai dengan tab Network
        submit_url = "https://spada.upnyk.ac.id/mod/attendance/attendance.php"
        payload_final = {
            "sessid": sessid_hari_ini,
            "sesskey": sesskey,
            "_qf__mod_attendance_form_studentattendance": "1",
            "mform_isexpanded_id_session": "1",
            "status": status_id,
            "submitbutton": "Save changes"
        }

        # Eksekusi Submit
        response_akhir = session.post(submit_url, data=payload_final, verify=False)
        
        # Validasi Hasil Akhir
        if response_akhir.status_code == 200 or len(response_akhir.history) > 0:
            logger.info('{"event":"presensi_sukses"}')
            tg_log(f"✅ [{username_label}] {mata_kuliah} - Presensi berhasil", category="user")
        else:
            logger.error('{"event":"presensi_gagal","status_code":%d}', response_akhir.status_code)
            tg_log(f"❌ [{username_label}] {mata_kuliah} - Submit gagal (status: {response_akhir.status_code})", category="user")
    except Exception as e:
        logger.exception('{"event":"presensi_error","error":%s}', json.dumps(str(e)))
        tg_log(f"⚠️ [{username_label}] {mata_kuliah} - Error: {e}", category="user")
        raise

def presensi_otomatis():
    

    for u in users:
        for jadwal in u['jadwal']:
            # mencari jadwal yang sama harinya dengan hari ini
            if sekarang.weekday() == jadwal['hari']:
                # mencari selisih menit antara jadwal dan sekarang
                target = date(sekarang.year, sekarang.month, sekarang.day, jadwal['jam'], jadwal['menit'], tzinfo=WIB)
                selisih = (sekarang - target).total_seconds() / 60 
                # jika masih dalam selisih jalankan presensi
                if 0 <= selisih <= 15:
                    label = "Rifty" if u['username'] == USERNAME_1 else "Hisyam"
                    jalankan_bot_presensi(u['username'], u['password'], jadwal['id'], jadwal['mata_kuliah'], label)
                elif selisih < 0:
                    logger.info('{"event":"not_time_yet","mata_kuliah":%s}', json.dumps(jadwal['mata_kuliah']))
                else:
                    logger.info('{"event":"past_time","mata_kuliah":%s}', json.dumps(jadwal['mata_kuliah']))
            else:
                logger.info('{"event":"no_schedule_today","hari":%d}', sekarang.weekday())

def run_presensi_with_logging():
    # Reset rate-limit timer setiap invocation agar tidak terblokir oleh sisa timer lama
    global _last_tg_log_system, _last_tg_log_user
    _last_tg_log_system = 0.0
    _last_tg_log_user = 0.0

    if sekarang.hour > 7 and sekarang.hour < 16 and sekarang.weekday() != 6:
        """Wrapper untuk background task dengan logging lengkap."""
        logger.info('{"event":"presensi_triggered","source":"HEAD /api/ping"}')
        tg_log("🔔 Presensi triggered via HEAD /api/ping", category="system")
        try:
            presensi_otomatis()
            logger.info('{"event":"presensi_completed"}')
            tg_log("✅ Presensi cycle completed", category="system")
        except Exception as e:
            logger.exception('{"event":"presensi_failed","error":%s}', json.dumps(str(e)))
            tg_log(f"❌ Presensi error: {e}", category="system")
    else:
        # libur presensinya blok
        logger.info('{"event":"Libur"}')

    

@app.head("/api/ping")
def ping_head():
    run_presensi_with_logging()
    return {"status": "ok"}