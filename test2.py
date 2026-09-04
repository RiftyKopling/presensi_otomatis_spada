import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime as date

# Menyembunyikan peringatan keamanan SSL karena kita menggunakan verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cek_jam():
    hari_ini = date.today().strftime("%Y-%m-%d")
    print(hari_ini)

def jalankan_bot_presensi(username, password, id_modul_presensi):
    print("=== MEMULAI PROSES OTOMASI PRESENSI ===")
    
    # Membuat session agar cookies/sesi tetap tersimpan di setiap request
    session = requests.Session()
    login_url = "https://spada.upnyk.ac.id/login/index.php"
    
    # ==============================================================
    # TAHAP 1: MENGAMBIL LOGIN TOKEN (CSRF Protection)
    # ==============================================================
    print("[1/5] Mengakses halaman login...")
    response_get = session.get(login_url, verify=False)
    soup_login = BeautifulSoup(response_get.text, 'html.parser')
    
    token_element = soup_login.find('input', {'name': 'logintoken'})
    if not token_element:
        print("[-] Gagal: logintoken tidak ditemukan di halaman.")
        return
    
    login_token = token_element.get('value')
    print(f"      Logintoken didapat: {login_token}")

    # ==============================================================
    # TAHAP 2: EKSEKUSI LOGIN
    # ==============================================================
    print("[2/5] Mengirim kredensial...")
    payload_login = {
        "username": username,
        "password": password,
        "logintoken": login_token
    }
    
    response_post = session.post(login_url, data=payload_login, verify=False)
    
    if "login" in response_post.url:
        print("[-] Gagal: Login ditolak. Periksa kembali username dan password.")
        return
    print("      Login berhasil!")

    # ==============================================================
    # TAHAP 3: MENGAMBIL SESSKEY DARI DASHBOARD
    # ==============================================================
    print("[3/5] Mengekstrak sesskey aktif...")
    soup_dash = BeautifulSoup(response_post.text, 'html.parser')
    
    # Mencari sesskey dari URL logout (Pola umum Moodle)
    logout_link = soup_dash.find('a', href=lambda href: href and "logout.php?sesskey=" in href)
    if logout_link:
        sesskey = logout_link['href'].split('sesskey=')[1]
        print(f"      Sesskey didapat: {sesskey}")
    else:
        print("[-] Gagal: Tidak bisa menemukan sesskey di dashboard.")
        return

    # ==============================================================
    # TAHAP 4: MENUJU MODUL PRESENSI & AMBIL DATA DINAMIS
    # ==============================================================
    # Menggunakan ID modul presensi (Contoh Data Science: 809066)
    url_view = f"https://spada.upnyk.ac.id/mod/attendance/view.php?id={id_modul_presensi}"
    print(f"[4/5] Membuka modul presensi (ID: {id_modul_presensi})...")
    
    response_view = session.get(url_view, verify=False)
    soup_view = BeautifulSoup(response_view.text, 'html.parser')
    
    # Mencari tombol "Ajukan Presensi" yang mengandung sessid hari ini
    link_eksekusi = soup_view.find('a', href=lambda href: href and "attendance.php?sessid=" in href)
    
    if not link_eksekusi:
        print("[-] Gagal: Tombol 'Ajukan Presensi' tidak ditemukan.")
        print("      Kemungkinan kelas belum dimulai atau jadwal sudah ditutup.")
        return
        
    url_form_presensi = link_eksekusi['href']
    # Parsing ID sesi (sessid) dari URL
    sessid_hari_ini = url_form_presensi.split('sessid=')[1].split('&')[0]
    print(f"      Jadwal aktif ditemukan! SessID: {sessid_hari_ini}")

    # ==============================================================
    # TAHAP 5: SUBMIT KEHADIRAN (Bypass Form & Tembak POST)
    # ==============================================================
    print("[5/5] Memindai form dan menembak payload...")
    
    # Akses form presensi untuk mencari ID status (radio button)
    response_form = session.get(url_form_presensi, verify=False)
    soup_form = BeautifulSoup(response_form.text, 'html.parser')
    
    # Secara otomatis mengambil 'value' dari radio button PERTAMA 
    # (Di Moodle, opsi pertama biasanya adalah "Hadir" / "Present")
    radio_hadir = soup_form.find('input', {'type': 'radio', 'name': 'status'})
    
    if not radio_hadir:
        print("[-] Gagal: Tidak menemukan opsi status kehadiran di formulir.")
        return
        
    status_id = radio_hadir.get('value')
    print(f"      ID Status Hadir didapat: {status_id}")

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
        print("\n[+] STATUS: PRESENSI SUKSES DIEKSEKUSI!")
    else:
        print(f"\n[-] STATUS: GAGAL. Server merespons dengan kode {response_akhir.status_code}")


# ==============================================================
# CARA MENJALANKAN SCRIPT
# ==============================================================
if __name__ == "__main__":
    # Ganti dengan data aslimu
    USER = "123240093"
    PASS = "Muhammad@2005"
    
    # ID Modul Presensi yang kamu temukan (misal: 809066 untuk Data Science)
    ID_MODUL = "812142" 
    
    cek_jam()
    
    jalankan_bot_presensi(USER, PASS, ID_MODUL)