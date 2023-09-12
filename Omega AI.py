import streamlit as st
import speech_recognition as sr
import wikipedia
import pyttsx3
import threading
from PIL import Image

# Inisialisasi recognizer
r = sr.Recognizer()

# Inisialisasi engine text-to-speech
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# Mengatur tampilan Streamlit dengan tema Poe
st.set_page_config(
    page_title="Pencarian Wikipedia",
    page_icon=":book:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mengatur logo dan judul
image = Image.open("poe_logo.png")
st.sidebar.image(image, use_column_width=True)
st.sidebar.title("Pencarian Wikipedia")

# Layout UI Streamlit
col1, col2 = st.columns([1, 3])
with col1:
    st.sidebar.write("")  # Mengatur jarak antara logo dan tombol mikrofon

with col2:
    st.sidebar.text("Silakan masukkan kata kunci:")
    search_input = st.sidebar.text_input("")

# Fungsi untuk membacakan teks
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Fungsi untuk mengenali suara pengguna
def recognize_speech():
    with sr.Microphone() as source:
        st.sidebar.write("Mulai mendengarkan...")
        audio = r.listen(source)

    try:
        st.sidebar.write("Mengenali teks...")
        query = r.recognize_google(audio)
        st.sidebar.write(f"Pengguna mengatakan: {query}")
        return query
    except sr.UnknownValueError:
        st.sidebar.write("Maaf, tidak dapat mengenali suara.")
        return ""
    except sr.RequestError:
        st.sidebar.write("Maaf, terjadi kesalahan saat memproses permintaan suara.")
        return ""

# Variabel untuk menyimpan status pembacaan suara
is_speaking = False
speak_thread = None

# Mencari informasi berdasarkan kata kunci yang dimasukkan
if st.sidebar.button("Cari"):
    if search_input:
        query = search_input
    else:
        query = recognize_speech()

    try:
        # Menghentikan pembacaan suara jika sedang berlangsung
        if is_speaking and speak_thread is not None:
            speak_thread.join()  # Menunggu pembacaan suara selesai
            is_speaking = False

        if query:
            results = wikipedia.search(query)
            if len(results) > 0:
                page = wikipedia.page(results[0])
                st.subheader(page.title)
                st.write(page.summary)
                st.write("URL artikel:", page.url)
                speak_thread = threading.Thread(target=speak, args=(page.summary,))
                speak_thread.start()  # Membacakan ringkasan artikel
                is_speaking = True
            else:
                st.write("Tidak ada hasil ditemukan.")
                threading.Thread(target=speak, args=("Maaf, tidak ada hasil ditemukan.",)).start()
    except wikipedia.exceptions.DisambiguationError as e:
        st.write("Masukkan lebih spesifik. Contoh: ", e.options[:5])
        threading.Thread(target=speak, args=("Masukkan lebih spesifik.",)).start()
    except wikipedia.exceptions.PageError:
        st.write("Tidak ada hasil ditemukan.")
        threading.Thread(target=speak, args=("Maaf, tidak ada hasil ditemukan.",)).start()
else:
    # Menghentikan pembacaan suara jika tidak ada input
    if is_speaking and speak_thread is not None:
        speak_thread.join()  # Menunggu pembacaan suara selesai
        is_speaking = False