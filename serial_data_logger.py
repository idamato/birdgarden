# Scatta la foto

def on_button_pressed_a():
    global trig0
    trig0 = 1
    basic.show_number(trig0)
    basic.pause(200)
    basic.clear_screen()
input.on_button_pressed(Button.A, on_button_pressed_a)

# Invia il segnale di halt al RPi

def on_logo_long_pressed():
    serial.write_line("0,0,0,0,0")
    basic.pause(200)
    serial.write_line("0,0,0,0,0")
input.on_logo_event(TouchButtonEvent.LONG_PRESSED, on_logo_long_pressed)

# Scatta la foto

def on_button_pressed_b():
    global trig0
    trig0 = 2
    basic.show_number(trig0)
    basic.pause(200)
    basic.clear_screen()
input.on_button_pressed(Button.B, on_button_pressed_b)

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
        serial.write_line("" + str(luce) + "," + ("" + str(temperatura)) + "," + ("" + str(audio)) + "," + ("" + str(trig0)) + "," + ("" + str(sonar2)))
        basic.clear_screen()
        trig0 = 0
        basic.pause(500)
    else:
        basic.pause(200)
basic.forever(on_forever)

