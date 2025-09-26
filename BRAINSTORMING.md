This is a brainstorming file where to put your immagination about the possible future evolution of this project.

1) AI adoption
    a) AI hardware selection
    b) AI engine selection
    c) AI training needed?

2) Mesh network configuration

3) Solar panel integration

4) Is it worth to have the Micro:bit out of this project, or there could be some hidden benefits?
    a) How do you think about having Micro:bit as an optional device? Wireless connected via serial-bluethoot to the Raspberry, only to issue command to this one? 
    b) Is it worth to use PIR sensor instead of the SONAR one, and connect it directly to the Raspberry?

5) Are terminal based (text) images possible to inject as AI training? ASCII Art convertion could help reduce the complexity of the AI model and calculations?

6) Ham radio SSTV mode as a new option for sending images
    a) There is a Python module which enable image transformation into wav files
       Some instruction require installation of specific libraries, check inside GitHub repository of every library or software.
       The following may be needed: sudo apt install libgd-dev libmagic-dev
       a.1)
           The generated audio can be sent as a modulated FM signal over the antenna using PiFM 
           git clone https://github.com/dnet/pySSTV
           cd pySSTV ; python3 ./setup.y build ; sudo python3 ./setup.py install
           cd <where images are> ; python3 -m pysstv --mode MartinM2 --resize image.png output.wav 
           an image file of 35Kb result in an audio wav file of about 5.5 Mb.
       a.2) Raspberry pi is able to send FM mofulation as RF via a small antenna connected to the GPIO4
       git clone https://github.com/F5OEO/rpitx
       cd rpitx ; ./install.sh (the compile process somehow fail to compile some programs but we need the pifmrds which is orrectly available)
       reboot
       sudo ./pifmrds -freq 76 -audio /home/ilfarodargento/sent/pettirosso-inverno.wav
    b) per trasmettere a frequenze differenti dalla FM commerciale, come ad esempio a 433 Mhz la procedura è differente:
       si usa imagemagik per trasformare l'immagine in un formato adatto con il comando seguente
       convert <input> -resize '320x256^' -gravity center -extent 320x256 -depth 8 <output>.rgb
       poi si converte il file .rgb in formato .ft con il comando seguente
       pisstv <input>.rgb <output>.ft
       ed infine si avvia la trasmissione alla frequenza desiderata, il range è da pochi kHz fino a 700 Mhz, con il comandi seguente
       sudo rpitx -m RF -i <input>.ft -f <frequency in KHz>
       
...possibile utilizzo anche per le radiosonde che potrebbero inviare immagini
        
script funzionanti:

ilfarodargento@birdgarden:~/birdgarden $ cat encoderMicroFAX.py
from PIL import Image
import numpy as np
import wave
import struct
import math
import serial
import threading
import queue
import time

# Parametri SSTV semplificati
INPUT_IMAGE = "../images/Pettirosso.jpg"
CONVERTED_IMAGE = "../images/microfax_pettirosso.jpg"
OUTPUT_WAVE = "../images/microfax_signora.wav"
WIDTH, HEIGHT = 64, 64
GRAY_MIN, GRAY_MAX = 0, 255
FREQ_MIN, FREQ_MAX = 1500, 2300
PIXEL_DURATION = 0.05
SYNC_FREQ = 1200
SYNC_DURATION = 0.2
EOL_FREQ = 300          # Frequenza speciale fine riga
EOL_DURATION = 0.05     # Durata tono fine riga
SAMPLE_RATE = 44100
samples = 0

# Imposta la connessione seriale
ser_micro = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
if not ser_micro:
    logging.info('microbit not found')

def load_and_convert_image(path):
    img = Image.open(path).convert('L')
    img = img.resize((WIDTH, HEIGHT), Image.NEAREST)
    img.save(CONVERTED_IMAGE)
    return np.array(img)

def gray_to_freq(gray):
    micro_freq = FREQ_MIN + int((gray / 255) * (FREQ_MAX - FREQ_MIN))
    global samples
    samples += 1
    print(samples,micro_freq)
    ser_micro.write(str(micro_freq).encode('utf-8'))
    time.sleep(0.1)  # breve pausa per evitare collisioni
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
        audio_data += generate_tone(SYNC_FREQ, SYNC_DURATION) # Sync
        for pixel in row:
            freq = gray_to_freq(pixel)
            audio_data += generate_tone(freq, PIXEL_DURATION)
        audio_data += generate_tone(EOL_FREQ, EOL_DURATION) # Fine riga

    return audio_data

# Processo completo
image_path = INPUT_IMAGE
gray_matrix = load_and_convert_image(image_path)
audio = generate_sstv_audio(gray_matrix)
#save_wave(OUTPUT_WAVE, audio)

print("WAV Audio microFAX con tono di fine riga salvato")





ilfarodargento@birdgarden:~ $ cat receiver.py
import serial
import time
import numpy as np
import wave
import struct
import math
from PIL import Image

# Parametri SSTV semplificati
CONVERTED_IMAGE = "microfax_grayscale.jpg"
OUTPUT_WAVE = "microfax_grayscale.wav"
WIDTH, HEIGHT = 64, 64
GRAY_MIN, GRAY_MAX = 0, 255
FREQ_MIN, FREQ_MAX = 1500, 2300
PIXEL_DURATION = 0.05
SYNC_FREQ = 1200
SYNC_DURATION = 0.2
EOL_FREQ = 300          # Frequenza speciale fine riga
EOL_DURATION = 0.05     # Durata tono fine riga
SAMPLE_RATE = 44100
count = 0

ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)

def freq_to_gray(freq):
    gray = int(((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)) * 255)
    return gray

matrice_grigi = [[0 for x in range(64)] for y in range(64)]

for y in range(64):
    for x in range(64):
        line = ser.read(4).decode().strip()
        try:
            freq = int(line)
            gray = freq_to_gray(freq)
            count = count + 1
            print(count,y,x,gray)
        except ValueError:
            gray = 0
        matrice_grigi[y][x] = gray

# Converti la matrice in un array NumPy
array = np.array(matrice_grigi, dtype=np.uint8)

# Crea l'immagine in scala di grigi
immagine = Image.fromarray(array, mode='L')

# Salva come JPG
immagine.save("immagine.jpg")
