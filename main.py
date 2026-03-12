import streamlit as st
import os
import time
import json
import numpy as np
from pedalboard import Pedalboard, Reverb, LowpassFilter, Chorus, Compressor
from pedalboard.io import AudioFile

# --- 1. SETUP & MULTI-CHAT DATABASE ---
for folder in ['inputs', 'outputs', 'history']:
    if not os.path.exists(folder): os.makedirs(folder)

DB_FILE = "history/chats_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # Default initial state
    return {"chat_1": {"title": "New Song Making", "messages": []}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="Lofi AI Remixer Pro", page_icon="🎧", layout="wide")

# क्लीन और डार्क थीम (कोई गंदे बॉर्डर्स नहीं)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_chat" not in st.session_state:
    st.session_state.current_chat = list(st.session_state.db.keys())[0]

active_chat_id = st.session_state.current_chat
active_data = st.session_state.db[active_chat_id]

# --- 3. LAYOUT (3 Columns) ---
col_ctrl, col_main, col_hist = st.columns([1.2, 3, 1.2])

# --- LEFT: Clean Mixing Console ---
with col_ctrl:
    st.header("🎚️ Console")
    
    # Clean Sliders (No minus/plus buttons)
    s_speed = st.slider("1. Speed (गति)", 0.5, 2.0, 1.0, 0.05)
    s_pitch = st.slider("2. Pitch (गहराई)", 0.5, 1.5, 0.85, 0.05)
    s_reverb = st.slider("3. Reverb %", 0, 100, 40, 5) / 100
    s_stereo = st.slider("4. Stereo Width %", 0, 100, 50, 5) / 25
    
    st.divider()
    # 8D Toggle Switch
    use_8d = st.toggle("🌀 Enable 3D/8D Effect", value=False)
    s_8d = 0.0
    if use_8d:
        s_8d = st.slider("8D Orbit Speed %", 0, 100, 20, 5) / 10

# --- RIGHT: Multi-Chat History & 3-Dot Menu ---
with col_hist:
    st.header("📜 History")
    
    # New Chat Button
    if st.button("➕ New Song Making", use_container_width=True):
        new_id = f"chat_{int(time.time())}"
        st.session_state.db[new_id] = {"title": "New Song Making", "messages": []}
        st.session_state.current_chat = new_id
        save_db(st.session_state.db)
        st.rerun()
    
    st.divider()
    
    # List all chats
    for chat_id, chat_data in reversed(st.session_state.db.items()):
        # Active chat highlighting
        is_active = (chat_id == active_chat_id)
        
        # Row layout for Title and 3-Dot Menu
        hc1, hc2 = st.columns([4, 1])
        with hc1:
            btn_label = f"📁 {chat_data['title'][:20]}" if not is_active else f"🟢 {chat_data['title'][:20]}"
            if st.button(btn_label, key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat = chat_id
                st.rerun()
        
        # 3-Dot Menu (Popover) only for active chat
        with hc2:
            if is_active:
                with st.popover("⋮"):
                    st.markdown("**Options**")
                    new_title = st.text_input("Rename", value=chat_data['title'], label_visibility="collapsed")
                    if st.button("Save", key="save_rename"):
                        st.session_state.db[chat_id]['title'] = new_title
                        save_db(st.session_state.db)
                        st.rerun()
                    if st.button("🗑️ Delete", key="del_chat"):
                        del st.session_state.db[chat_id]
                        if not st.session_state.db: # If all deleted, make a new one
                            st.session_state.db = {"chat_1": {"title": "New Song Making", "messages": []}}
                        st.session_state.current_chat = list(st.session_state.db.keys())[0]
                        save_db(st.session_state.db)
                        st.rerun()

# --- CENTER: Professional Chat & Processing ---
with col_main:
    st.title("🎵 Lofi Remixer AI")
    st.caption(f"Current Working File: **{active_data['title']}**")
    st.divider()
    st.warning("⚠️ **DISCLAIMER:** This tool is for personal & educational use only. We do not own the copyright to the uploaded songs. Please do not monetize the remixed tracks.")
    
    # Clean Native Chat Interface
    chat_container = st.container(height=500)
    with chat_container:
        for i, m in enumerate(active_data["messages"]):
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if "audio" in m:
                    st.audio(m["audio"])
                    if st.button(f"🔄 Regenerate", key=f"regen_{active_chat_id}_{i}"):
                        # Find the prompt that triggered this audio
                        st.session_state.regen_msg = active_data["messages"][i-1]["content"]

    # Input Section
    uploaded_file = st.file_uploader("Upload Song (Drag & Drop)", type=['mp3', 'wav'])
    prompt = st.chat_input("सर, अपना प्रॉम्प्ट लिखें (e.g. 'Make it slow and spatial')...")

    # Target prompt (either newly typed or regenerated)
    target_prompt = prompt or st.session_state.get("regen_msg")
    if "regen_msg" in st.session_state: del st.session_state["regen_msg"]

    if target_prompt:
        if not uploaded_file and not any("audio" in msg for msg in active_data["messages"]):
            st.error("सर, कृपया पहले एक गाना अपलोड करें!")
        else:
            # Smart Naming Fix: Change title if it's a new song
            if uploaded_file and (active_data["title"] == "New Song Making" or active_data["title"] == "New Remix"):
                active_data["title"] = uploaded_file.name.replace(".mp3", "").replace(".wav", "")

            # Add user message
            active_data["messages"].append({"role": "user", "content": target_prompt})
            save_db(st.session_state.db)
            
            with st.chat_message("assistant"):
                st.toast("Processing started...", icon="⏳") # Quick animation
                with st.spinner("सर, AI आपके गाने को रिमिक्स कर रहा है... कृपया 10-20 सेकंड रुकें।"):
                    
                    # File handling
                    if uploaded_file:
                        in_p = os.path.join("inputs", uploaded_file.name)
                        with open(in_p, "wb") as f: f.write(uploaded_file.getbuffer())
                        st.session_state.last_uploaded = in_p
                    else:
                        in_p = st.session_state.last_uploaded # Use last uploaded if regenerating

                    # Audio Engine
                    out_p = os.path.join("outputs", f"Remix_{int(time.time())}.wav")
                    with AudioFile(in_p) as f_in:
                        audio = f_in.read(f_in.frames)
                        sr = f_in.samplerate
                        
                        # 8D Logic (Only if toggled ON)
                        if use_8d and s_8d > 0:
                            t = np.linspace(0, audio.shape[1]/sr, audio.shape[1])
                            pan = (np.sin(2 * np.pi * (s_8d/10) * t) + 1) / 2
                            audio[0, :] *= pan
                            audio[1, :] *= (1 - pan)
                            
                        board = Pedalboard([
                            Compressor(), 
                            LowpassFilter(cutoff_frequency_hz=2800), 
                            Chorus(depth=s_stereo/10), 
                            Reverb(room_size=0.8, wet_level=s_reverb)
                        ])
                        eff = board(audio, sr)
                        final_sr = int((sr * s_speed) / s_pitch)
                        
                        with AudioFile(out_p, 'w', final_sr, eff.shape[0]) as o: 
                            o.write(eff)
                
                # Success Animation & Save
                st.balloons() # Cool animation
                ans = f"✅ सर, आपका रिमिक्स तैयार है! (Speed: {s_speed}x, Pitch: {s_pitch}x)"
                st.markdown(ans)
                st.audio(out_p)
                
                active_data["messages"].append({"role": "assistant", "content": ans, "audio": out_p})
                save_db(st.session_state.db)
                st.rerun()