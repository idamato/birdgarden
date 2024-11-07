#!/usr/bin/python

from time import sleep
from picamera2 import Picamera2
import serial

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
camera = Picamera2()
id = 0

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
        sleep(2)
        capture_config = camera.create_still_configuration()
        filename = "/home/ilfarodargento/software/departures/" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar) + ".jpg"
        camera.switch_mode_and_capture_file(capture_config, filename)
        print('fatta foto: ', filename)
      # sleep(1)
done
