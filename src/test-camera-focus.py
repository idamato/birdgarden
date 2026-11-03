from picamera2 import Picamera2
from libcamera import controls
import time
picam2 = Picamera2()
picam2.start(show_preview=True)
# imposta autofocus veloce
#picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
#imposta focus manuale 10cm (il minimo)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
time.sleep(1.0)
picam2.start_and_capture_files("fastfocus-test{:d}.jpg", num_files=3, delay=1.0)
picam2.stop_preview()
picam2.stop()
