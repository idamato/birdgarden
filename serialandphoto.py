#!/usr/bin/python

from time import sleep
from picamera2 import Picamera2
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
        filename = "/home/ilfarodargento/software/departures/" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar) + ".jpg"
        # flash_led.on()
        sleep(1)
        # esegue la foto
        camera.switch_mode_and_capture_file(capture_config, filename)
        # flash_led.off()
        camera.stop()
        print('fatta foto: ', filename)
      # sleep(1)
done
