import numpy as np
import matplotlib.pyplot as plt
import wave

# Parametri del segnale
INPUT_WAVE = "C:/Users/taotr/Downloads/microfax_signora.wav"
OUTPUT_IMAGE = "C:/Users/taotr/Downloads/microfax_signora.png"
PIXEL_DURATION = 0.05
SAMPLE_RATE = 44100
FREQS = np.linspace(1500, 2300, 256)      # Miglior mappatura pixel
END_OF_LINE_FREQ = 300                    # Tono fine riga
EOL_TOLERANCE = 15                        # ± tolleranza Hz per il riconoscimento

def load_audio(filename):
    with wave.open(filename, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        signal = np.frombuffer(frames, dtype=np.int16)
        return signal

def decode(signal, width):
    chunk_size = int(SAMPLE_RATE * PIXEL_DURATION)
    num_chunks = len(signal) // chunk_size

    image = []
    row = []

    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = signal[start:end]

        # FFT → Frequenza dominante
        fft = np.abs(np.fft.fft(chunk))[:len(chunk)//2]
        freqs_axis = np.fft.fftfreq(len(chunk), d=1/SAMPLE_RATE)[:len(chunk)//2]
        dominant_freq = freqs_axis[np.argmax(fft)]

        if abs(dominant_freq - END_OF_LINE_FREQ) <= EOL_TOLERANCE:
            # È il tono di fine riga → salva riga e resetta
            if row:
                image.append(row)
                row = []
        else:
            index = np.argmin(np.abs(FREQS - dominant_freq))
            row.append(index)

    # 🔚 Aggiungi ultima riga se non terminata
    if row:
        image.append(row)

    return np.array(image)

def visualize(pixels, filename):
    plt.imshow(pixels, cmap='gray', interpolation='nearest')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Immagine salvata come: {filename}")
    print("Dimensione:", pixels.shape)

# Esempio d’uso
if __name__ == '__main__':
    audio = load_audio(INPUT_WAVE)
    pixel_matrix = decode(audio, width=64)
    visualize(pixel_matrix, filename=OUTPUT_IMAGE)
