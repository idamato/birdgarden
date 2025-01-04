def on_button_pressed_a():
    global pin0
    pin0 = 1
input.on_button_pressed(Button.A, on_button_pressed_a)

audio = 0
temperatura = 0
luce = 0
sonar2 = 0
pin0 = 0
serial.redirect_to_usb()
pin0 = 0

def on_forever():
    global sonar2, pin0, luce, temperatura, audio
    sonar2 = sonar.ping(DigitalPin.P12, DigitalPin.P13, PingUnit.CENTIMETERS)
    if sonar2 < 12:
        pin0 = 1
        basic.show_number(pin0)
        luce = input.light_level()
        temperatura = input.temperature()
        audio = input.sound_level()
        serial.write_line("" + str(luce) + "," + ("" + str(temperatura)) + "," + ("" + str(audio)) + "," + ("" + str(pin0)) + "," + ("" + str(sonar2)))
        basic.clear_screen()
        pin0 = 0
        basic.pause(500)
    else:
        basic.pause(200)
basic.forever(on_forever)
