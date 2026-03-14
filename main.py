import streamlit as st
import time
from engine import process_audio, convert_format

st.set_page_config(page_title="Lofi AI Remixer | Akash Babu", page_icon="🎧", layout="centered")

# Smooth animation ke liye CSS
st.markdown("""
<style>
@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.4s ease-in-out; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_download_audio(wav_bytes, fmt):
    return convert_format(wav_bytes, fmt)

if 'history' not in st.session_state: st.session_state.history = []

try:
    with open("styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError: pass

# 🌐 Bhasha (Language) badalne ka logic
lang_is_english = st.toggle("🌐 Switch to English", value=False)

def t(en_text, hi_text):
    return en_text if lang_is_english else hi_text

st.markdown("<h1 style='text-align: center;'>🎧 Lofi AI Remixer Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='brand-name'>Engineered with ❤️ by Akash Babu</div>", unsafe_allow_html=True)

# 🚨 Copyright aur Warning Section
warn_hi = "⚠️ **ध्यान दें:** यहाँ डेटा टेम्पररी है। कृपया रिमिक्स डाउनलोड कर लें! <br>⚖️ **कॉपीराइट:** आप जो गाना रिमिक्स कर रहे हैं, उसके कॉपीराइट के लिए आप खुद ज़िम्मेदार हैं। बिना परमिशन के किसी का गाना कमर्शियल यूज़ न करें।"
warn_en = "⚠️ **Note:** Data is temporary. Download your remixes! <br>⚖️ **Copyright:** You are solely responsible for the copyright of the audio you remix. Do not use copyrighted material commercially without permission."
st.warning(t(warn_en, warn_hi), icon="⚠️")

uploaded_file = st.file_uploader(t("Drop Audio File (MP3, WAV, M4A)", "अपना गाना यहाँ डालें (MP3, WAV, M4A)"), type=["mp3", "wav", "m4a"])

if uploaded_file:
    if 'current_file' not in st.session_state or st.session_state['current_file'] != uploaded_file.name:
        st.session_state['current_file'] = uploaded_file.name
        if 'latest_remix' in st.session_state: del st.session_state['latest_remix']

    st.audio(uploaded_file)
    st.success(t(f"🎵 '{uploaded_file.name}' Ready for Magic!", f"🎵 '{uploaded_file.name}' जादू के लिए तैयार!"))
    st.divider()

    st.markdown(t("### 🎛️ The Studio Controls", "### 🎛️ स्टूडियो कंट्रोल्स"))
    tab1, tab2, tab3 = st.tabs([
        t("🎛️ Basic Tuning", "🎛️ बेसिक ट्यूनिंग"), 
        t("🌌 Spatial & FX", "🌌 स्पेशल & FX"), 
        t("🎚️ 9-Band EQ", "🎚️ 9-बैंड EQ")
    ])
    
    with tab1:
        speed_factor = st.slider(t("🏃‍♂️ Speed (x)", "🏃‍♂️ स्पीड (रफ़्तार)"), 0.5, 1.5, 0.85, 0.05)
        pitch_semitones = st.slider(t("🎤 Pitch (Semitones)", "🎤 पिच (आवाज़ भारी/पतली)"), -12, 12, 0, 1)
        reverb_percent = st.slider(t("🌧️ Reverb (%)", "🌧️ गूंज (Reverb %)"), 0, 100, 50, 5)

    with tab2:
        stereo_percent = st.slider(t("🎧 Stereo Width (%)", "🎧 स्टीरियो चौड़ाई (%)"), 0, 100, 30, 5)
        
        enable_underwater = st.toggle(t("🌊 Underwater / Muffled Filter", "🌊 अंडरवाटर / मफ़ल इफ़ेक्ट"), value=False)
        # 🚨 Hide/Show Logic (Ab ye gayab rahega jab band hoga)
        if enable_underwater:
            st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
            underwater_freq = st.slider(t("🌫️ Muffle Strength (Hz)", "🌫️ इफ़ेक्ट की ताकत (Hz)"), 100, 2000, 400)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            underwater_freq = 3500 # Default off value
            
        st.divider()
        enable_8d = st.toggle(t("🌌 Enable 8D Sound", "🌌 8D साउंड चालू करें"), value=False)
        if enable_8d:
            st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
            speed_8d = st.slider(t("🌀 8D Spin Speed (%)", "🌀 8D घूमने की स्पीड (%)"), 0, 100, 50, 5)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            speed_8d = 50

    with tab3:
        presets_en = {
            "🎛️ Custom (Manual)": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "🌧️ Deep Lofi (Relaxing & Heavy Bass)": [6, 4, 2, 0, -2, -4, -6, -8, -10],
            "🎧 Late Night Drive (Car Vibe)": [4, 3, 0, -2, -2, 1, 3, 4, 2],
            "📻 Vintage Radio (Nostalgia)": [-10, -8, -3, 2, 5, 3, -2, -6, -10],
            "✨ Acoustic Chill (Clear Vocals)": [-2, -1, 0, 2, 4, 3, 2, 1, 0]
        }
        presets_hi = {
            "🎛️ कस्टम (मैनुअल)": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "🌧️ Deep Lofi (सुकून और भारी बेस)": [6, 4, 2, 0, -2, -4, -6, -8, -10],
            "🎧 Late Night Drive (कार वाली फील)": [4, 3, 0, -2, -2, 1, 3, 4, 2],
            "📻 Vintage Radio (पुरानी यादें)": [-10, -8, -3, 2, 5, 3, -2, -6, -10],
            "✨ Acoustic Chill (साफ़ आवाज़)": [-2, -1, 0, 2, 4, 3, 2, 1, 0]
        }
        presets = presets_en if lang_is_english else presets_hi
        selected_preset = st.selectbox(t("✨ Choose Vibe (EQ Presets):", "✨ Vibe चुनें (EQ Presets):"), list(presets.keys()))
        current_eq = presets[selected_preset]
        st.divider()
        
        eq_bands = []
        cols = st.columns(3)
        freq_labels = ["60Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]
        for i, label in enumerate(freq_labels):
            with cols[i % 3]:
                val = st.slider(label, -12, 12, current_eq[i], 1)
                eq_bands.append(val)

    st.write("") 
    
    btn_text = t("🔥 CREATE MY LOFI REMIX", "🔥 मेरा लोफी रिमिक्स बनाओ")
    if st.button(btn_text, type="primary", use_container_width=True):
        with st.spinner(t("Processing your Masterpiece... 🎵", "आपका रिमिक्स बन रहा है... 🎵")):
            try:
                processed_wav = process_audio(
                    uploaded_file.getvalue(), uploaded_file.name, speed_factor, 
                    pitch_semitones, reverb_percent, stereo_percent, 
                    enable_8d, speed_8d, underwater_freq, eq_bands
                )
                st.session_state['latest_remix'] = {
                    "data": processed_wav,
                    "name": uploaded_file.name
                }
                st.rerun() 
            except Exception as e:
                st.error(f"Error: {e}")

    # 🚨 Download Box (Generate hone ke baad aayega)
    if 'latest_remix' in st.session_state and st.session_state['current_file'] == uploaded_file.name:
        st.divider()
        st.success(t("✅ Your Remix is Ready!", "✅ आपका रिमिक्स तैयार है!"))
        st.balloons() # Bubbles yaha safe hain!
        
        st.audio(st.session_state['latest_remix']['data'], format="audio/wav")
        
        st.markdown(t("### 💾 Export & Download", "### 💾 एक्सपोर्ट और डाउनलोड"))
        col_fmt, col_btn = st.columns([0.4, 0.6])
        
        with col_fmt:
            selected_format = st.selectbox(t("Format:", "फॉर्मेट चुनें:"), ["WAV", "MP3", "M4A"])
            
        with col_btn:
            fmt_lower = selected_format.lower()
            mime_type = "audio/mpeg" if fmt_lower == "mp3" else f"audio/{fmt_lower}"
            
            with st.spinner(t(f"Preparing {selected_format}...", f"{selected_format} तैयार हो रहा है...")):
                dl_bytes = get_download_audio(st.session_state['latest_remix']['data'], fmt_lower)
                
            st.write("") 
            dl_label = t(f"📥 Download {selected_format}", f"📥 {selected_format} डाउनलोड करें")
            st.download_button(
                label=dl_label, 
                data=dl_bytes, 
                file_name=f"AkashBabu_{uploaded_file.name}.{fmt_lower}", 
                mime=mime_type, 
                type="primary", 
                use_container_width=True
            )

else:
    st.info(t("👆 Drop an audio file above to start.", "👆 शुरू करने के लिए ऊपर अपना गाना अपलोड करें।"))

st.markdown("""
    <div class="footer">
        © 2024 - 2026 | <span style="color: #ff4b4b; font-weight: bold;">Akash Babu Signature Edition</span> | 🇮🇳 All Rights Reserved
    </div>
""", unsafe_allow_html=True)