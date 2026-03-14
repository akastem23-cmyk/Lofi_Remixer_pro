import streamlit as st
import time
from engine import process_audio

st.set_page_config(page_title="Lofi AI Remixer | Akash Babu", page_icon="🎧", layout="centered")

if 'history' not in st.session_state: st.session_state.history = []
try:
    with open("styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError: pass

st.markdown("<h1 style='text-align: center;'>🎧 Lofi AI Remixer Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='brand-name'>Engineered with ❤️ by Akash Babu</div>", unsafe_allow_html=True)
st.markdown("<div class='made-in-india'>Proudly Made in India 🇮🇳</div>", unsafe_allow_html=True)

lang_is_english = st.toggle("🌐 Switch to English", value=False)
if lang_is_english: st.warning("⚠️ Note: Data here is temporary. Please download your remixes!")
else: st.warning("⚠️ ध्यान दें: यहाँ डेटा टेम्पररी है। कृपया अपना रिमिक्स डाउनलोड कर लें!")

with st.sidebar:
    if st.button("➕ New Remix", use_container_width=True, type="primary"): st.rerun()
    st.header("📜 My Remixes")
    if len(st.session_state.history) == 0:
        st.info("No recent remixes." if lang_is_english else "यहाँ आपके बनाये गए गाने दिखेंगे।")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            col1, col2 = st.columns([0.85, 0.15])
            with col1: st.markdown(f"**🎵 {item['song']}**")
            with col2:
                with st.popover("⋮"):
                    # जो फॉर्मेट चुना गया था, उसी फॉर्मेट में प्ले और डाउनलोड होगा
                    file_ext = item.get('ext', 'wav')
                    mime_type = "audio/mpeg" if file_ext == "mp3" else f"audio/{file_ext}"
                    
                    st.audio(item['audio_data'], format=mime_type)
                    st.download_button("📥 Download", data=item['audio_data'], file_name=f"AkashBabu_{item['song']}.{file_ext}", mime=mime_type, key=f"dl_{i}")
                    if st.button("🗑️ Delete", key=f"del_{i}"):
                        st.session_state.history.remove(item)
                        st.rerun()
            st.divider()

uploaded_file = st.file_uploader("Drop Audio File (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)
    st.success(f"🎵 '{uploaded_file.name}' Ready for Magic!")
    st.divider()

    st.markdown("### 🎛️ The Studio Controls")
    tab1, tab2, tab3 = st.tabs(["🎛️ Basic Tuning", "🌌 Spatial & FX", "🎚️ 9-Band EQ"])
    
    with tab1:
        speed_factor = st.slider("🏃‍♂️ Speed (x)", 0.5, 1.5, 0.85, 0.05)
        pitch_semitones = st.slider("🎤 Pitch (Semitones)", -12, 12, 0, 1)
        reverb_percent = st.slider("🌧️ Reverb (%)", 0, 100, 50, 5)

    with tab2:
        stereo_percent = st.slider("🎧 Stereo Width (%)", 0, 100, 30, 5)
        enable_underwater = st.toggle("🌊 Underwater / Muffled Filter", value=False)
        underwater_freq = st.slider("🌫️ Muffle Strength (Hz)", 100, 2000, 400) if enable_underwater else 3500
        st.divider()
        enable_8d = st.toggle("🌌 Enable 8D Sound", value=False)
        speed_8d = st.slider("🌀 8D Spin Speed (%)", 0, 100, 50, 5) if enable_8d else 50

    with tab3:
        st.caption("चुटकी बजाते ही 'वाइब' बदलें:")
        presets = {
            "🎛️ Custom (Manual)": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "🌧️ Deep Lofi (सुकून और भारी बेस)": [6, 4, 2, 0, -2, -4, -6, -8, -10],
            "🎧 Late Night Drive (कार वाली फील)": [4, 3, 0, -2, -2, 1, 3, 4, 2],
            "📻 Vintage Radio (पुरानी यादें)": [-10, -8, -3, 2, 5, 3, -2, -6, -10],
            "✨ Acoustic Chill (साफ़ आवाज़)": [-2, -1, 0, 2, 4, 3, 2, 1, 0]
        }
        selected_preset = st.selectbox("✨ Vibe चुनें (EQ Presets):", list(presets.keys()))
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
    
    # 🚨 नया फीचर: एक्सपोर्ट फॉर्मेट!
    st.markdown("### 💾 Export Settings")
    col_fmt, _ = st.columns([0.5, 0.5])
    with col_fmt:
        selected_format = st.selectbox("किस फॉर्मेट में डाउनलोड करना है?", ["MP3", "WAV", "M4A"])

    if st.button("🔥 CREATE MY LOFI REMIX", type="primary", use_container_width=True):
        with st.spinner(f"Processing & Saving as {selected_format}... 🎵"):
            try:
                # फॉर्मेट को छोटे अक्षरों (mp3, wav) में पास करें
                fmt_lower = selected_format.lower()
                
                processed_audio = process_audio(
                    uploaded_file.getvalue(), uploaded_file.name, speed_factor, 
                    pitch_semitones, reverb_percent, stereo_percent, 
                    enable_8d, speed_8d, underwater_freq, eq_bands, output_format=fmt_lower
                )
                st.success("✅ Masterpiece Ready!")
                st.balloons() 
                
                # ऑडियो प्लेयर भी उसी फॉर्मेट में बजेगा
                mime_type = "audio/mpeg" if fmt_lower == "mp3" else f"audio/{fmt_lower}"
                st.audio(processed_audio, format=mime_type)
                
                # हिस्ट्री में एक्सटेंशन भी सेव करें ताकि डाउनलोड सही से हो
                st.session_state.history.append({
                    "song": uploaded_file.name, 
                    "audio_data": processed_audio,
                    "ext": fmt_lower
                })
            except Exception as e:
                st.error(f"Error processing audio: {e}")

else:
    st.info("👆 शुरू करने के लिए ऊपर अपना गाना अपलोड करें।")

st.markdown("""
    <div class="footer">
        © 2024 - 2026 | <span style="color: #ff4b4b; font-weight: bold;">Akash Babu Signature Edition</span> | 🇮🇳 All Rights Reserved
    </div>
""", unsafe_allow_html=True)