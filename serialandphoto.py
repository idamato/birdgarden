#!/usr/bin/python

from time import sleep
from picamera2 import Picamera2
from libcamera import controls
import serial
# from gpiozero import LED
# from gpiozero import MotionSensor

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
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
camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

# imposta la cattura di tre immagini consecutive
# camera.start_and_capture_files("fastfocus{:d}.jpg", num_files=3, delay=0.5)

capture_config = camera.create_still_configuration()
# camera.configure(capture_config)

print ("Hello this is the start!")

while True:
    rcv = ser.readline()
    cmd = rcv.decode('utf-8').rstrip()
    values = cmd.split(',')
    print(values)
    if len(values) == 5: 
      luce, temperatura, audio, pin0, sonar = [int(value) for value in values]
      print(luce, temperatura, audio, pin0, sonar)
      if pin0:
        id += 1
        print('fare foto!')
        camera.start()
        # capture_config = camera.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640,480)})
        capture_config = camera.create_still_configuration()
        filename = "/home/ilfarodargento/departures/" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar)
        # flash_led.on()
        sleep(1)
        # esegue la foto
        camera.switch_mode_and_capture_file(capture_config, filename + ".jpg")
        # in caso di video
        # camera.start_and_record_video(filename + ".mp4", duration=5)
        # flash_led.off()
        camera.stop()
        print('fatta foto: ', filename)
      # sleep(1)
done
