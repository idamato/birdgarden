#!/usr/bin/python

from time import sleep
from picamera2 import Picamera2
from libcamera import controls
import serial
import os
# from gpiozero import LED
# from gpiozero import MotionSensor

# funzione per la gestione della lettura dei dati dalla porta seriale
porta = '/dev/ttyACM0'
baudrate = 115200

def leggi_dati_seriale(porta, baudrate):
    while True:
        try:
            # Apertura della connessione seriale
            with serial.Serial(porta, baudrate, timeout=1) as ser:
                # print(f"Connesso a {porta} a {baudrate} baud.")
                while True:
                    # Lettura dei dati
                    dati = ser.readline().decode('utf-8').rstrip()
                    if dati:
                        return dati

        except serial.SerialException as e:
            # Gestione errore di connessione
            print(f"Errore di connessione: {e}")
            print("Tentativo di riconnessione tra 5 minuti...")
            sleep(300)  # Attendi 5 minuti e riprova

# ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# la funzione verifica se è arrivato il comando di shutdown
def verifica_halt(array):
    if len(array) == 5 and all(elemento == '0' for elemento in array):
        return True
    return False

# funzione che impartisce il comando di chiusura del sistema
def arresta_sistema():
    try:
        # Esegue il comando di halt
        os.system("sudo shutdown -h now")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

# inizializza la fotocamera
camera = Picamera2()
# l'anodo del LED (gamba lunga) è collegato al GPIO 17
# fra il catodo (gamba corta) e GROUND è necessario collegare una resistenza di almeno 100 ohm
# flash_led = LED(17)
# nel caso di utilizzo di motion sensor
# sensor = MotionSensor(14)

id = 0
# capture_config = camera.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640,480)})

# imposta il modo autofocus nel continuo
# camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# imposta il modo autofocus con alta velocità
#camera.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})

# imposta il focus in modalità manuale a 10cm, il minimo
# camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

# imposta la cattura di tre immagini consecutive
# camera.start_and_capture_files("fastfocus{:d}.jpg", num_files=3, delay=0.5)

# capture_config = camera.create_still_configuration()
# camera.configure(capture_config)

print ("Hello this is the start!")

while True:
    # rcv = ser.readline()
    # cmd = rcv.decode('utf-8').rstrip()
    cmd = leggi_dati_seriale(porta, baudrate)
    values = cmd.split(',')
    print(values)
    if len(values) == 5: 
      luce, temperatura, audio, pin0, sonar = [int(value) for value in values]
      print(luce, temperatura, audio, pin0, sonar)
      if verifica_halt(values):
         # Execute the sudo halt command
         print('devo arrestare il sistema')
         arresta_sistema()
      if pin0:
        id += 1
        print('fare foto!')
        camera.start()
        # capture_config = camera.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640,480)})
        capture_config = camera.create_still_configuration()
        filename = "/usr/local/birdgarden/departures/" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar)
        # flash_led.on()
        camera.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
        # attendo un secondo per la messa a fuoco
        sleep(1)
        # esegue la foto
        camera.switch_mode_and_capture_file(capture_config, filename + ".jpg")
        # in caso di video
        camera.start_and_record_video(filename + ".mp4", duration=30)
        # flash_led.off()
        camera.stop()
        print('missione compiuta: ', filename)
      # sleep(1)
done
