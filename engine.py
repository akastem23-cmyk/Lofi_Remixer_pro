import os
import tempfile
import numpy as np
import subprocess
from pedalboard import Pedalboard, Reverb, Compressor, LowpassFilter, Chorus, PitchShift, PeakFilter
from pedalboard.io import AudioFile

def process_audio(input_bytes, file_name, speed_factor, pitch_semitones, reverb_percent, stereo_percent, enable_8d, speed_8d, underwater_freq, eq_bands):
    ext = os.path.splitext(file_name)[1].lower()
    
    # 1. टेम्परेरी फाइल बनाना
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
        tmp_in.write(input_bytes)
        tmp_in_path = tmp_in.name

    # 🚨 .m4a को पढ़ने के लिए WAV में बदलना
    if ext == ".m4a":
        wav_path = tmp_in_path.replace(".m4a", ".wav")
        subprocess.run(['ffmpeg', '-i', tmp_in_path, wav_path, '-y'], check=True, capture_output=True)
        os.remove(tmp_in_path)
        tmp_in_path = wav_path

    output_path = tmp_in_path + "_processed.wav"

    try:
        with AudioFile(tmp_in_path) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        new_samplerate = int(samplerate * speed_factor)
        effects = []

        # इफ़ेक्ट्स लगाना
        effects.append(LowpassFilter(cutoff_frequency_hz=underwater_freq))

        if pitch_semitones != 0:
            effects.append(PitchShift(semitones=pitch_semitones))

        freqs = [60, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        for freq, gain in zip(freqs, eq_bands):
            if gain != 0:
                effects.append(PeakFilter(cutoff_frequency_hz=freq, gain_db=gain, q=1.5))

        if stereo_percent > 0:
            effects.append(Chorus(rate_hz=0.5, depth=stereo_percent/100.0 * 0.5, mix=stereo_percent/100.0))

        effects.append(Reverb(room_size=reverb_percent/100.0, wet_level=reverb_percent/100.0))
        effects.append(Compressor(threshold_db=-15, ratio=4))

        board = Pedalboard(effects)
        processed_audio = board(audio, samplerate)

        # 🌌 8D Effect (Panning)
        if enable_8d and processed_audio.shape[0] == 2:
            lfo_hz = 0.1 + (speed_8d / 100.0) * 1.9  
            duration = processed_audio.shape[1] / samplerate
            t = np.linspace(0, duration, processed_audio.shape[1], endpoint=False)
            pan_lfo = np.sin(2 * np.pi * lfo_hz * t)
            angle = (pan_lfo + 1) * (np.pi / 4)
            left_gain = np.cos(angle)
            right_gain = np.sin(angle)
            processed_audio[0, :] = processed_audio[0, :] * left_gain
            processed_audio[1, :] = processed_audio[1, :] * right_gain

        # प्रोसेस हुए गाने को WAV में सेव करना
        with AudioFile(output_path, 'w', new_samplerate, processed_audio.shape[0]) as f:
            f.write(processed_audio)

        # फाइल को पढ़कर वापस भेजना
        with open(output_path, 'rb') as f:
            return f.read()

    finally:
        # कचरा साफ़ करना (सर्वर को हल्का रखने के लिए)
        if os.path.exists(tmp_in_path): os.remove(tmp_in_path)
        if os.path.exists(output_path): os.remove(output_path)

# 🚨 नया फंक्शन: डाउनलोड के समय यूज़र की पसंद के फॉर्मेट में बदलने के लिए
def convert_format(wav_bytes, target_format):
    if target_format == "wav": return wav_bytes
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        tmp_wav.write(wav_bytes)
        wav_path = tmp_wav.name
        
    out_path = wav_path.replace(".wav", f".{target_format}")
    try:
        # FFmpeg से कन्वर्ट करना (High Quality)
        if target_format == "mp3":
            subprocess.run(['ffmpeg', '-i', wav_path, '-b:a', '320k', out_path, '-y'], check=True, capture_output=True)
        elif target_format == "m4a":
            subprocess.run(['ffmpeg', '-i', wav_path, '-c:a', 'aac', '-b:a', '256k', out_path, '-y'], check=True, capture_output=True)
            
        with open(out_path, 'rb') as f:
            return f.read()
    finally:
        # सफाई
        if os.path.exists(wav_path): os.remove(wav_path)
        if os.path.exists(out_path): os.remove(out_path)