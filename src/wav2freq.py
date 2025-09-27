from pydub import AudioSegment
import numpy as np
import scipy.signal
import struct
from PIL import Image

def comprimi_toni(lista):
    if not lista:
        return []

    ottimizzata = []
    freq_corrente, durata_totale = lista[0]

    for freq, durata in lista[1:]:
        if freq == freq_corrente:
            durata_totale += durata
        else:
            ottimizzata.append((freq_corrente, durata_totale))
            freq_corrente, durata_totale = freq, durata

    ottimizzata.append((freq_corrente, durata_totale))
    return ottimizzata

#Mappiamo ogni livello di grigio ad una frequenza
def grayscale_to_freq(value):
    value = int(value)
    # 8 livelli: 0–224 → 1500–2300 Hz
    return 1500 + (value // 32) * 100

img = Image.new("RGB", (320, 256), "black")
for x in range(0, 320, 40):
    for y in range(256):
        img.putpixel((x, y), (255, 255, 255))  # Linea bianca ogni 40px

img.save("C:/Users/taotr/Downloads/test_martin1.png")

#img = Image.open("C:/Users/taotr/Downloads/cincia2.jpg").convert("L")  # Scala di grigi
#img_resized = img.resize((128, 128))
#arr = np.array(img)
# Quantizzazione: da 0–255 a 8 livelli
#quantized = (arr // 128) * 128  # Ogni livello ha ampiezza 128
#frequenze = [grayscale_to_freq(val) for val in quantized.flatten()]
#img_resized.save("C:/Users/taotr/Downloads/test_martin1_128x128.png")

#image = Image.open("C:/Users/taotr/Downloads/test_martin1.png")
#sstv = MartinM1(image, 44100)
#with open("C:/Users/taotr/Downloads/martin1_test.wav", "wb") as f:
#    sstv.write_wav(f)

# Carica il file WAV
# audio = AudioSegment.from_wav("C:/Users/taotr/Downloads/sstv_signal.wav").set_channels(1)
audio = AudioSegment.from_wav("C:/Users/taotr/Downloads/cincia2.wav").set_channels(1)
fout_ott = open("C:/Users/taotr/Downloads/tones_ott.txt", "w")
#fout = open("C:/Users/taotr/Downloads/tones.txt", "w")

samples = np.array(audio.get_array_of_samples())
sample_rate = audio.frame_rate
# Parametri della finestra
#nperseg = int(sample_rate * 0.006)  # ~5 ms
#f, t, Sxx = scipy.signal.spectrogram(samples, sample_rate, nperseg=nperseg)
# Estrazione dei toni dominanti
#frequenze_durata = []
#time_step_ms = int((t[1] - t[0]) * 1000)
#
#for i in range(len(t)):
#    spectrum = Sxx[:, i]
#    freq = int(f[np.argmax(spectrum)])
#    if 1200 < freq < 2600:  # filtro frequenze utili SSTV
#        frequenze_durata.append((freq, time_step_ms))
        #print(f"({freq},{time_step_ms}),")
#for freq, dur in frequenze_durata:
#    fout.write(f"({freq},{dur}),\n")

#Robot36
# Parametri temporali (es. 5 ms)
step_ms = 5
step_samples = int(sample_rate * step_ms / 1000)
frequenze_durata = []

for i in range(0, len(samples) - step_samples, step_samples):
    chunk = samples[i:i+step_samples]
    f, Pxx = scipy.signal.periodogram(chunk, sample_rate)
    freq = int(f[np.argmax(Pxx)])
    if 1400 <= freq <= 2400:
        frequenze_durata.append((freq, step_ms))

sequenza_ottimizzata = comprimi_toni(frequenze_durata)

for freq, dur in sequenza_ottimizzata:
    fout_ott.write(f"({freq},{dur}),\n")

