import requests
from bs4 import BeautifulSoup
import urllib3
import re  # Untuk pencarian pola teks (regex) jika diperlukan

# Menyembunyikan peringatan SSL (Hanya untuk keperluan edukasi/testing)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def jalankan_presensi():
    # Kredensial dan URL dasar
    USERNAME = "123230016"
    PASSWORD = "Ayudyaprameswari112@"
    
    # URL ini harus disesuaikan dengan ID modul presensi yang sedang aktif hari ini
    URL_MODUL_PRESENSI = "https://spada.upnyk.ac.id/mod/attendance/view.php?id=809066"
    URL_LOGIN = "https://spada.upnyk.ac.id/login/index.php"
    URL_SUBMIT = "https://spada.upnyk.ac.id/mod/attendance/attendance.php"

    session = requests.Session()

    print("=== TAHAP 1 & 2: LOGIN DAN BYPASS CSRF ===")
    print("[*] Mengambil logintoken...")
    get_login = session.get(URL_LOGIN, verify=False)
    soup_login = BeautifulSoup(get_login.text, 'html.parser')
    
    token_element = soup_login.find('input', {'name': 'logintoken'})
    if not token_element:
        print("[-] Gagal menemukan logintoken.")
        return
        
    login_token = token_element.get('value')
    
    payload_login = {
        "username": USERNAME,
        "password": PASSWORD,
        "logintoken": login_token
    }

    print("[*] Mengirim data login...")
    post_login = session.post(URL_LOGIN, data=payload_login, verify=False)
    
    if "login" in post_login.url:
        print("[-] Login gagal! Periksa kembali username dan password.")
        return
    print("[+] Login berhasil!")

    print("\n=== TAHAP 3: EKSTRAK SESSKEY ===")
    soup_dash = BeautifulSoup(post_login.text, 'html.parser')
    sesskey = ""
    
    # Mencari sesskey dari tag input tersembunyi atau link logout
    sesskey_element = soup_dash.find('input', {'name': 'sesskey'})
    if sesskey_element:
        sesskey = sesskey_element.get('value')
    else:
        logout_link = soup_dash.find('a', href=lambda href: href and "logout.php?sesskey=" in href)
        if logout_link:
            sesskey = logout_link['href'].split('sesskey=')[1]

    if not sesskey:
        print("[-] Gagal mendapatkan sesskey.")
        return
    print(f"[+] Sesskey didapatkan: {sesskey}")

    print("\n=== TAHAP 4: MENUJU HALAMAN PRESENSI ===")
    print(f"[*] Mengakses {URL_MODUL_PRESENSI}...")
    view_presensi = session.get(URL_MODUL_PRESENSI, verify=False)
    soup_view = BeautifulSoup(view_presensi.text, 'html.parser')

    # Mencari link yang menuju ke attendance.php untuk mengekstrak sessid kelas
    link_eksekusi = soup_view.find('a', href=lambda href: href and "attendance.php?sessid=" in href)
    
    if not link_eksekusi:
        print("[-] Tombol 'Ajukan presensi' tidak ditemukan. Mungkin belum waktunya absen.")
        return
        
    url_eksekusi = link_eksekusi['href']
    # Memisahkan string URL untuk mengambil angka ID di akhir (misal: 1095928)
    sessid_kelas = url_eksekusi.split('sessid=')[1].split('&')[0]
    print(f"[+] Sesi Kelas (sessid) ditemukan: {sessid_kelas}")

    print("\n=== TAHAP 5: EKSEKUSI PRESENSI ===")
    # Mengakses halaman form presensi untuk mencari ID Status (misal: 502110 untuk "Hadir")
    form_presensi = session.get(url_eksekusi, verify=False)
    soup_form = BeautifulSoup(form_presensi.text, 'html.parser')
    
    # Mencari radio button pertama (Biasanya "Hadir" ada di urutan paling kiri/atas)
    # Ini mencari elemen input bertipe radio dan mengambil value-nya
    status_hadir = soup_form.find('input', {'type': 'radio'})
    
    if not status_hadir:
        print("[-] Opsi pilihan absen tidak ditemukan di halaman.")
        return
        
    status_id = status_hadir.get('value')
    print(f"[+] ID Status Hadir ditemukan: {status_id}")

    # Menyusun Payload Final seperti yang kamu temukan di Network Tab
    payload_final = {
        "sessid": sessid_kelas,
        "sesskey": sesskey,
        "_qf__mod_attendance_form_studentattendance": "1",
        "mform_isexpanded_id_session": "1",
        "status": status_id,
        "submitbutton": "Save changes"
    }

    print("[*] Mengirimkan payload presensi final...")
    hasil_akhir = session.post(URL_SUBMIT, data=payload_final, verify=False)

    if hasil_akhir.status_code == 200 or len(hasil_akhir.history) > 0:
        print("[+] PRESENSI BERHASIL DIEKSEKUSI! Selamat!")
    else:
        print(f"[-] Terjadi kesalahan. Status code: {hasil_akhir.status_code}")

# Menjalankan fungsi utama
if __name__ == "__main__":
    jalankan_presensi()