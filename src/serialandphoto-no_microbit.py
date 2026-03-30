import RPi.GPIO as GPIO
import time

# -----------------------------
# CONFIGURAZIONE
# -----------------------------
TRIG = 23
ECHO = 24

SOGLIA_CM = 30        # distanza limite
PERIODO_LETTURA = 2   # secondi tra letture

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
time.sleep(2)  # stabilizzazione sensore


def misura_distanza():
    """Restituisce la distanza in cm o None in caso di timeout."""
    # impulso TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # attesa fronte di salita
    start = time.time()
    timeout = start + 0.02
    while GPIO.input(ECHO) == 0:
        start = time.time()
        if start > timeout:
            return None

    # attesa fronte di discesa
    stop = time.time()
    timeout = stop + 0.02
    while GPIO.input(ECHO) == 1:
        stop = time.time()
        if stop > timeout:
            return None

    durata = stop - start
    distanza = (durata * 34300) / 2
    return distanza


def loop_principale():
    """Loop principale a basso consumo CPU."""
    try:
        while True:
            dist = misura_distanza()

            if dist is not None and dist < SOGLIA_CM:
                print(f"Ostacolo a {dist:.1f} cm")
              
                '''Inserire qui il codice principale'''

            time.sleep(PERIODO_LETTURA)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    loop_principale()
