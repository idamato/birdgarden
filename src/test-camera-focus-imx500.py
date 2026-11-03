from picamera2 import Picamera2
import time
picam2 = Picamera2()
config=picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()
time.sleep(2.0)
print("Preparazione scatto...")
# Definisci il nome del file immagine
file_name = "/tmp/foto_ai_camera.jpg"
# Scatta e salva la foto
print(f"Scatto in corso... Salvataggio in {file_name}")
picam2.capture_file(file_name)
# Arresta e rilascia la telecamera
picam2.stop()
print("Foto scattata con successo!")
