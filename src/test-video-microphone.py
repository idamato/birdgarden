#!/usr/bin/env python3
import subprocess
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

def find_usb_microphone():
    """
    WORK IN PROGRESS...
    Rileva automaticamente un microfono USB tramite PulseAudio o ALSA.
    Restituisce il nome del dispositivo audio utilizzabile da FfmpegOutput.
    """
    # Tentativo 1: PulseAudio (Bookworm)
    try:
        result = subprocess.check_output(
            ["pactl", "list", "sources"], text=True
        )
        for line in result.splitlines():
            if "Name:" in line and ("usb" in line.lower() or "microphone" in line.lower()):
                return line.split("Name:")[1].strip()
    except Exception:
        pass

    # Tentativo 2: ALSA (fallback)
    try:
        result = subprocess.check_output(["arecord", "-l"], text=True)
        for line in result.splitlines():
            if "USB" in line:
                # es: "card 1: Device [USB Audio Device], device 0: USB Audio"
                parts = line.split()
                card = parts[1].replace(":", "")
                device = parts[5].replace(":", "")
                return f"hw:{card},{device}"
    except Exception:
        pass

    return None


def main():
    # nel mio caso ho evitato di chiamare la funzione di ricerca del microfono ed ho inserito direttamente il risultato
    # audio_device = find_usb_microphone()
    audio_device = "hw:1,0"
    if not audio_device:
        raise RuntimeError("Nessun microfono USB trovato!")
    print(f"Microfono USB rilevato: {audio_device}")
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration({'size': (1280, 720), 'format': 'YUV420'})
    picam2.configure(video_config)
    encoder = H264Encoder(bitrate=6_000_000)
    encoder.audio = True
    output = PyavOutput("/tmp/registrazione.mp4")
    print("Avvio registrazione...")
    picam2.start_recording(encoder, output)
    time.sleep(10)  # durata registrazione
    print("Stop registrazione...")
    picam2.stop_recording()
    print("File salvato come /tmp/registrazione.mp4")

if __name__ == "__main__":
    main()
