cd C:\Users\Michelle Ohello\Documents\Streamlit\Masjidimport streamlit as st
import os
import requests
from datetime import datetime, timedelta
import time
import locale

# Atur konfigurasi halaman
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Fungsi untuk menyembunyikan tombol deploy
def hide_streamlit_menu():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

# Fungsi untuk mengatur background
def set_background(image_path):
    if image_path:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{image_path}");
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Fungsi untuk menampilkan header dengan icon speaker jika speaker aktif
def display_header(title, header_bg_color, kas_masjid, running_text, running_speed):
    # Icon speaker (hanya ditampilkan jika speaker aktif)
    speaker_icon = "🔊" if st.session_state.get("speaker_active", False) else ""

    st.markdown(
        f"""
        <style>
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: {header_bg_color};
            color: white;
            text-align: center;
            padding: 5px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: auto;
            z-index: 1000;
        }}
        .header-left {{
            flex: 1;
            text-align: left;
            padding-left: 10px;
            font-size: 1em;
            overflow: hidden;
            white-space: nowrap;
        }}
        .header-left span {{
            display: inline-block;
            animation: scroll {running_speed}s linear infinite;
        }}
        @keyframes scroll {{
            0% {{
                transform: translateX(100%);
            }}
            100% {{
                transform: translateX(-100%);
            }}
        }}
        .header-center {{
            flex: 2;
            text-align: center;
        }}
        .header-right {{
            flex: 1;
            text-align: right;
            padding-right: 10px;
            font-size: 1em;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }}
        .speaker-icon {{
            margin-left: 15px;
            font-size: 1.5em;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.5em;
            line-height: 1.2;
        }}

        /* Responsiveness */
        @media (max-width: 768px) {{
            .header {{
                flex-direction: column;
                padding: 10px;
            }}
            .header-left, .header-center, .header-right {{
                text-align: center;
                padding: 5px 0;
            }}
            .header h1 {{
                font-size: 1.2em;
            }}
            .header-right {{
                font-size: 0.9em;
            }}
        }}
        </style>
        <div class="header">
            <div class="header-left">
                <span>{running_text}</span>
            </div>
            <div class="header-center">
                <h1>{title}</h1>
            </div>
            <div class="header-right">
                <p>Kas Masjid Hari Ini: <strong>Rp {kas_masjid:,}</strong></p>
                <span class="speaker-icon">{speaker_icon}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fungsi untuk menampilkan footer
def display_footer(jadwal_sholat, footer_bg_color):
    st.markdown(
        f"""
        <style>
        footer {{
            visibility: hidden;
        }}
        .footer {{
            visibility: visible;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: {footer_bg_color};
            color: white;
            text-align: center;
            padding: 10px;
            display: flex;
            justify-content: space-around;
        }}
        .footer-box {{
            flex: 1;
            margin: 0 5px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.1); /* Warna default kotak jadwal sholat */
            border-radius: 5px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .footer-box p {{
            margin: 5px 0;
            font-size: 1.2em;
        }}

        /* Responsiveness */
        @media (max-width: 768px) {{
            .footer {{
                flex-direction: column;
                padding: 15px;
            }}
            .footer-box {{
                margin: 10px 0;
                padding: 15px;
            }}
            .footer-box p {{
                font-size: 1em;
            }}
        }}
        @media (max-width: 480px) {{
            .footer-box p {{
                font-size: 0.5em;
            }}
        }}
        </style>
        <div class="footer">
            <div class="footer-box">
                <p>Subuh</p>
                <p>{jadwal_sholat['subuh']}</p>
            </div>
            <div class="footer-box">
                <p>Dzuhur</p>
                <p>{jadwal_sholat['dzuhur']}</p>
            </div>
            <div class="footer-box">
                <p>Ashar</p>
                <p>{jadwal_sholat['ashar']}</p>
            </div>
            <div class="footer-box">
                <p>Maghrib</p>
                <p>{jadwal_sholat['maghrib']}</p>
            </div>
            <div class="footer-box">
                <p>Isya</p>
                <p>{jadwal_sholat['isya']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fungsi CMS sederhana
def cms():
    st.sidebar.title("CMS - Pengaturan")
    title = st.sidebar.text_input("Judul Header", "Masjid Al-Falah")
    
    # Warna header dan footer
    header_bg_color = st.sidebar.color_picker("Warna Background Header", "#262730")
    footer_bg_color = st.sidebar.color_picker("Warna Background Footer", "#262730")
    
    # Input lokasi untuk jadwal sholat
    st.sidebar.title("Lokasi Jadwal Sholat")
    city = st.sidebar.text_input("Kota", "Jakarta")
    country = st.sidebar.text_input("Negara", "Indonesia")
    
    # Ambil jadwal sholat dari API
    jadwal_sholat = get_prayer_times(city, country)

    # Input kas masjid
    st.sidebar.title("Info Kas Masjid")
    kas_masjid = st.sidebar.number_input("Jumlah Kas Masjid (Rp)", value=1000000, step=1000)

    # Input running text
    st.sidebar.title("Running Text")
    running_text = st.sidebar.text_input("Teks Running Text", "Selamat datang di Masjid Al-Falah!")
    running_speed = st.sidebar.slider("Kecepatan Running Text (detik)", min_value=5, max_value=30, value=15)

    # Toggle speaker
    st.sidebar.title("Pengaturan Speaker")
    if "speaker_active" not in st.session_state:
        st.session_state["speaker_active"] = False
    st.session_state["speaker_active"] = st.sidebar.checkbox("Aktifkan Speaker Adzan", st.session_state["speaker_active"])

    # Upload background image
    st.sidebar.title("Background")
    uploaded_file = st.sidebar.file_uploader("Unggah Gambar Background", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        # Simpan file yang diunggah ke folder sementara
        with open("temp_background.png", "wb") as f:
            f.write(uploaded_file.getbuffer())
        background_path = "temp_background.png"
    else:
        background_path = None

    # Upload suara adzan lokal
    st.sidebar.title("Upload Suara Adzan")
    adzan_file = st.sidebar.file_uploader(
        "Unggah Suara Adzan (mp3/wav)", 
        type=["mp3", "wav"],
        accept_multiple_files=False,
        key="adzan_file_uploader",
        label_visibility="visible",
        disabled=False
    )
    adzan_path = "adzan.mp3"
    if adzan_file is not None:
        adzan_path = f"temp_adzan.{adzan_file.type.split('/')[-1]}"
        with open(adzan_path, "wb") as f:
            f.write(adzan_file.getbuffer())
    # Tidak ada st.audio(adzan_file) atau st.audio(adzan_path) di sini!

    return title, header_bg_color, footer_bg_color, jadwal_sholat, kas_masjid, running_text, running_speed, background_path, adzan_path

# Fungsi untuk mendapatkan jadwal sholat dari API
def get_prayer_times(city, country):
    try:
        # URL API Aladhan
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=11"
        response = requests.get(url)
        data = response.json()

        # Ambil waktu sholat dari respons API
        timings = data['data']['timings']

        # Koreksi waktu Subuh dan Isya (hilangkan zona waktu jika ada, dan pastikan format 24 jam)
        def fix_time(t):
            # Ambil hanya jam dan menit, buang info zona waktu jika ada
            return t.split(' ')[0][:5]

        return {
            "subuh": fix_time(timings['Fajr']),
            "dzuhur": fix_time(timings['Dhuhr']),
            "ashar": fix_time(timings['Asr']),
            "maghrib": fix_time(timings['Maghrib']),
            "isya": fix_time(timings['Isha'])
        }
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil jadwal sholat: {e}")
        return {
            "subuh": "N/A",
            "dzuhur": "N/A",
            "ashar": "N/A",
            "maghrib": "N/A",
            "isya": "N/A"
        }

# Fungsi untuk menampilkan tanggal dan jam digital secara real-time
def display_datetime(datetime_placeholder):
    # Atur lokal ke bahasa Indonesia
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')  # Untuk sistem berbasis Unix/Linux
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'Indonesian_Indonesia.1252')  # Untuk sistem Windows

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # Format jam:menit:detik
    current_date = now.strftime("%A, %d %B %Y")  # Format hari, tanggal bulan tahun dalam bahasa Indonesia

    # Letakkan jam di kanan atas, DI BAWAH footer (footer fixed di bawah, jadi jam di atasnya)
    datetime_placeholder.markdown(
        f"""
        <style>
        .datetime-rightcenter {{
            position: fixed;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
            background-color: rgba(38, 39, 48, 0.35);
            color: #fff;
            padding: 8px 18px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            font-size: 2em;
            text-align: right;
            z-index: 2001;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.10);
        }}
        .datetime-rightcenter .date {{
            font-size: 1em;
            opacity: 1;
        }}
        .datetime-rightcenter .time {{
            font-size: 1.2em;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        </style>
        <div class="datetime-rightcenter">
            <div class="date">{current_date}</div>
            <div class="time">{current_time}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fungsi untuk memutar suara adzan
def play_adzan(adzan_path=None):
    if st.session_state.get("speaker_active", False) and adzan_path is not None:
        audio_bytes = None
        with open(adzan_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

# Main aplikasi
def main():
    # Sembunyikan menu Streamlit
    hide_streamlit_menu()

    # CMS untuk mengatur konten
    title, header_bg_color, footer_bg_color, jadwal_sholat, kas_masjid, running_text, running_speed, background_path, adzan_path = cms()

    # Atur background
    if background_path:
        import base64
        with open(background_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        set_background(encoded_string)

    # Placeholder untuk elemen dinamis
    datetime_placeholder = st.empty()

    # Tampilkan header
    display_header(title, header_bg_color, kas_masjid, running_text, running_speed)

    # Tampilkan footer
    display_footer(jadwal_sholat, footer_bg_color)

    # Perbarui tanggal dan jam digital
    display_datetime(datetime_placeholder)

    # Putar suara adzan jika speaker aktif dan file tersedia
    play_adzan(adzan_path)

    # Loop untuk memperbarui elemen dinamis
    while True:
        display_datetime(datetime_placeholder)
        time.sleep(1)

if __name__ == "__main__":
    main()
