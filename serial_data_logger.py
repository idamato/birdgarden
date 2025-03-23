def scriviseriale():
    serial.write_line("" + str(luce) + "," + ("" + str(temperatura)) + "," + ("" + str(audio)) + "," + ("" + str(trig0)) + "," + ("" + str(sonar2)))
# Invia il segnale di halt al RPi (soluzione per spegnerlo)

def on_logo_long_pressed():
    serial.write_line("0,0,0,0,0")
    basic.pause(200)
    serial.write_line("0,0,0,0,0")
input.on_logo_event(TouchButtonEvent.LONG_PRESSED, on_logo_long_pressed)

def rileva():
    global luce, temperatura, audio
    luce = input.light_level()
    temperatura = input.temperature()
    audio = input.sound_level()
sonar2 = 0
audio = 0
temperatura = 0
luce = 0
trig0 = 0
serial.redirect_to_usb()
trig0 = 0

def on_forever():
    global sonar2, trig0
    sonar2 = sonar.ping(DigitalPin.P0, DigitalPin.P1, PingUnit.CENTIMETERS)
    if sonar2 < 20:
        trig0 = 1
        basic.show_number(trig0)
        rileva()
        scriviseriale()
        basic.clear_screen()
        trig0 = 0
        basic.pause(10000)
    else:
        basic.pause(500)
basic.forever(on_forever)


