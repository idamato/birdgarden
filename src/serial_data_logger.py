def on_button_pressed_a():
    global trig0
    trig0 = 1
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_logo_pressed():
    global trig0
    serial.write_line("0,0,0,0,0")
    basic.show_icon(IconNames.NO)
    basic.pause(1000)
    serial.write_line("0,0,0,0,0")
    trig0 = 0
input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)

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
basic.show_icon(IconNames.HEART)
basic.pause(2000)

def on_forever():
    global sonar2, trig0
    sonar2 = sonar.ping(DigitalPin.P0, DigitalPin.P1, PingUnit.CENTIMETERS)
    if trig0 == 1 or sonar2 > 1 and sonar2 < 13:
        trig0 = 1
        basic.show_number(trig0)
        rileva()
        serial.write_line("" + str(luce) + "," + ("" + str(temperatura)) + "," + ("" + str(audio)) + "," + ("" + str(trig0)) + "," + ("" + str(sonar2)))
        basic.clear_screen()
        trig0 = 0
        basic.pause(2000)
    else:
        basic.pause(500)
basic.forever(on_forever)
