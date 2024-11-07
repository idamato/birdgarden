def on_button_pressed_a():
    global pin0
    pin0 = 1
input.on_button_pressed(Button.A, on_button_pressed_a)

pin0 = 0
serial.redirect_to_usb()
luce = 0
temperatura = 0
audio = 0
pin0 = 0
sonar2 = 0

def on_forever():
    global luce, temperatura, audio, sonar2, pin0
    luce = input.light_level()
    temperatura = input.temperature()
    audio = input.sound_level()
    sonar2 = sonar.ping(DigitalPin.P12, DigitalPin.P13, PingUnit.CENTIMETERS)
    if sonar2 < 8:
        pin0 = 1
    serial.write_line("" + str(luce) + "," + str(temperatura) + "," + str(audio) + "," + str(pin0) + "," + str(sonar2))
    basic.show_number(pin0)
    if pin0 == 1:
        pin0 = 0
        basic.pause(2000)
    else:
        basic.pause(200)
basic.forever(on_forever)