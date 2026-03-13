import streamlit as st
import time
from engine import process_audio

st.set_page_config(page_title="Lofi AI Remixer | Akash Babu", page_icon="🎧", layout="centered")

if 'history' not in st.session_state: st.session_state.history = []
try:
    with open("styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError: pass

# --- हेडर ---
st.markdown("<h1 style='text-align: center;'>🎧 Lofi AI Remixer Pro</h1>", unsafe_allow_html=True)
st.markdown("<div class='brand-name'>Engineered with ❤️ by Akash Babu</div>", unsafe_allow_html=True)
st.markdown("<div class='made-in-india'>Proudly Made in India 🇮🇳</div>", unsafe_allow_html=True)

# --- भाषा का टॉगल ---
lang_is_english = st.toggle("🌐 Switch to English", value=False)
if lang_is_english: st.warning("⚠️ Note: Data here is temporary. Please download your remixes!")
else: st.warning("⚠️ ध्यान दें: यहाँ डेटा टेम्पररी है। कृपया अपना रिमिक्स डाउनलोड कर लें!")

# --- साइडबार हिस्ट्री ---
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
                    st.audio(item['audio_data'], format='audio/wav')
                    st.download_button("📥 Download", data=item['audio_data'], file_name=f"AkashBabu_{item['song']}.wav", key=f"dl_{i}")
                    if st.button("🗑️ Delete", key=f"del_{i}"):
                        st.session_state.history.remove(item)
                        st.rerun()
            st.divider()

# --- अपलोड सेक्शन ---
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
        # 🚨 जादू यहाँ है: सुकून वाले Presets!
        st.caption("चुटकी बजाते ही 'वाइब' बदलें:")
        presets = {
            "🎛️ Custom (Manual)": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "🌧️ Deep Lofi (सुकून और भारी बेस)": [6, 4, 2, 0, -2, -4, -6, -8, -10],
            "🎧 Late Night Drive (कार वाली फील)": [4, 3, 0, -2, -2, 1, 3, 4, 2],
            "📻 Vintage Radio (पुरानी यादें)": [-10, -8, -3, 2, 5, 3, -2, -6, -10],
            "✨ Acoustic Chill (साफ़ आवाज़)": [-2, -1, 0, 2, 4, 3, 2, 1, 0]
        }
        
        # यूज़र को ड्रॉपडाउन मेन्यू दिखाना
        selected_preset = st.selectbox("✨ Vibe चुनें (EQ Presets):", list(presets.keys()))
        current_eq = presets[selected_preset]
        
        st.divider()
        
        eq_bands = []
        cols = st.columns(3)
        freq_labels = ["60Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]
        
        # स्लाइडर्स अब प्रेसेट के हिसाब से अपने आप सेट हो जाएंगे!
        for i, label in enumerate(freq_labels):
            with cols[i % 3]:
                val = st.slider(label, -12, 12, current_eq[i], 1)
                eq_bands.append(val)

    st.write("") 

    if st.button("🔥 CREATE MY LOFI REMIX", type="primary", use_container_width=True):
        with st.spinner("Processing Studio Quality Audio... 🎵"):
            try:
                processed_audio = process_audio(
                    uploaded_file.getvalue(), uploaded_file.name, speed_factor, 
                    pitch_semitones, reverb_percent, stereo_percent, 
                    enable_8d, speed_8d, underwater_freq, eq_bands
                )
                st.success("✅ Masterpiece Ready!")
                st.balloons() 
                st.audio(processed_audio, format='audio/wav')
                st.session_state.history.append({"song": uploaded_file.name, "audio_data": processed_audio})
            except Exception as e:
                st.error(f"Error processing audio: {e}")

else:
    st.info("👆 शुरू करने के लिए ऊपर अपना गाना अपलोड करें।")

# --- Footer ---
st.markdown("""
    <div class="footer">
        © 2024 - 2026 | <span style="color: #ff4b4b; font-weight: bold;">Akash Babu Signature Edition</span> | 🇮🇳 All Rights Reserved
    </div>
""", unsafe_allow_html=True)