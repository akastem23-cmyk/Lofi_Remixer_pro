import os
import tempfile
import numpy as np
import subprocess
from pedalboard import Pedalboard, Reverb, Compressor, LowpassFilter, Chorus, PitchShift, PeakFilter
from pedalboard.io import AudioFile

# यहाँ नया पैरामीटर 'output_format' जोड़ा गया है
def process_audio(input_bytes, file_name, speed_factor, pitch_semitones, reverb_percent, stereo_percent, enable_8d, speed_8d, underwater_freq, eq_bands, output_format="wav"):
    ext = os.path.splitext(file_name)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
        tmp_in.write(input_bytes)
        tmp_in_path = tmp_in.name

    # .m4a को पढ़ने के लिए WAV में बदलना
    if ext == ".m4a":
        wav_path = tmp_in_path.replace(".m4a", ".wav")
        subprocess.run(['ffmpeg', '-i', tmp_in_path, wav_path, '-y'], check=True, capture_output=True)
        os.remove(tmp_in_path)
        tmp_in_path = wav_path

    # यह प्रोसेस होने के बाद की टेम्परेरी फाइल है
    output_wav_path = tmp_in_path + "_processed.wav"
    final_output_path = output_wav_path

    try:
        with AudioFile(tmp_in_path) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        new_samplerate = int(samplerate * speed_factor)
        effects = []

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

        # 8D Effect
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

        # 1. पहले WAV फॉर्मेट में सेव करें
        with AudioFile(output_wav_path, 'w', new_samplerate, processed_audio.shape[0]) as f:
            f.write(processed_audio)

        # 2. 🚨 जादू: यूज़र की पसंद के हिसाब से कन्वर्ट करें!
        if output_format == "mp3":
            final_output_path = output_wav_path.replace(".wav", ".mp3")
            subprocess.run(['ffmpeg', '-i', output_wav_path, '-b:a', '320k', final_output_path, '-y'], check=True, capture_output=True)
        elif output_format == "m4a":
            final_output_path = output_wav_path.replace(".wav", ".m4a")
            subprocess.run(['ffmpeg', '-i', output_wav_path, '-c:a', 'aac', '-b:a', '256k', final_output_path, '-y'], check=True, capture_output=True)

        # फाइनल फाइल पढ़ें और वापस भेजें
        with open(final_output_path, 'rb') as f:
            return f.read()

    finally:
        # सफाई (ताकि सर्वर फुल न हो)
        if os.path.exists(tmp_in_path): os.remove(tmp_in_path)
        if os.path.exists(output_wav_path): os.remove(output_wav_path)
        if final_output_path != output_wav_path and os.path.exists(final_output_path): 
            os.remove(final_output_path)