from PIL import Image
import numpy as np
import wave
import struct
import math

# ⚙️ Parametri SSTV semplificati
INPUT_IMAGE = "C:/Users/taotr/OneDrive/Immagini/uccellini/signora.png"
CONVERTED_IMAGE = "C:/Users/taotr/Downloads/debug_microfax_signora_grayscale.jpg"
OUTPUT_WAVE = "C:/Users/taotr/Downloads/microfax_signora.wav"
WIDTH, HEIGHT = 64, 64
GRAY_MIN, GRAY_MAX = 0, 255
FREQ_MIN, FREQ_MAX = 1500, 2300
PIXEL_DURATION = 0.05
SYNC_FREQ = 1200
SYNC_DURATION = 0.2
EOL_FREQ = 300          # Frequenza speciale fine riga
EOL_DURATION = 0.05     # Durata tono fine riga
SAMPLE_RATE = 44100

def load_and_convert_image(path):
    img = Image.open(path).convert('L')
    img = img.resize((WIDTH, HEIGHT), Image.NEAREST)
    img.save(CONVERTED_IMAGE)
    return np.array(img)

def gray_to_freq(gray):
    micro_freq = FREQ_MIN + int((gray / 255) * (FREQ_MAX - FREQ_MIN))
    print(micro_freq)
    return micro_freq

def generate_tone(freq, duration):
    return [math.sin(2 * math.pi * freq * i / SAMPLE_RATE) for i in range(int(SAMPLE_RATE * duration))]

def save_wave(filename, data):
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for s in data:
            val = max(-1.0, min(1.0, s))
            wav.writeframes(struct.pack('<h', int(val * 32767)))

def generate_sstv_audio(gray_array):
    audio_data = []

    for row in gray_array:
        audio_data += generate_tone(SYNC_FREQ, SYNC_DURATION)  # 🔊 Sync
        for pixel in row:
            freq = gray_to_freq(pixel)
            audio_data += generate_tone(freq, PIXEL_DURATION)
        audio_data += generate_tone(EOL_FREQ, EOL_DURATION)     # 📍 Fine riga

    return audio_data

# 🔄 Processo completo
image_path = INPUT_IMAGE
gray_matrix = load_and_convert_image(image_path)
audio = generate_sstv_audio(gray_matrix)
save_wave(OUTPUT_WAVE, audio)

print("WAV Audio microFAX con tono di fine riga salvato")
