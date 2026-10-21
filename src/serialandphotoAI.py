#!/usr/bin/python
from picamera2 import Picamera2
from pathlib import Path
from typing import Any
import serial
import time
import os
import subprocess
import argparse
import numpy as np
from datetime import datetime
import meshtastic
import meshtastic.serial_interface

# Caricare le due seguenti righe solo se disponibile anche il microfono
# from picamera2.encoders import H264Encoder
# from picamera2.outputs import PyavOutput

# from gpiozero import LED
# from gpiozero import MotionSensor

try:
    # Current Picamera2 API.
    from picamera2.devices import IMX500
except ImportError:  # Compatibility fallback for some Picamera2 versions.
    from picamera2.devices.imx500 import IMX500

DEFAULT_MODEL = "/usr/local/birdgarden/model/network.rpk"
DEFAULT_LABELS = "/usr/local/birdgarden/model/labels.txt"
DEFAULT_PHOTO = "/usr/local/birdgarden/departure/photo.tmp"

def load_labels(path: str | Path) -> list[str]:
    """Load class labels, one per line, in the order used during training."""
    labels_path = Path(path).expanduser().resolve()
    if not labels_path.is_file():
        raise FileNotFoundError(
            f"Label file not found: {labels_path}\n"
            "Create labels.txt with one class name per line, in exactly the same "
            "order as class_names.json from the training notebook."
        )

    labels = [
        line.strip()
        for line in labels_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not labels:
        raise ValueError(f"The label file is empty: {labels_path}")
    return labels

def as_probabilities(values: np.ndarray) -> np.ndarray:
    """Normalize model outputs for display.

    If the output already looks like a probability vector (non-negative and
    approximately summing to 1), it is returned as-is. Otherwise, softmax is
    applied. The resulting scores are useful for ranking classes, but should
    not automatically be interpreted as calibrated real-world probabilities.
    """
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    if values.size == 0:
        raise ValueError("The model returned an empty output tensor.")
    if not np.all(np.isfinite(values)):
        raise ValueError("The model output contains NaN or infinite values.")

    total = float(values.sum())
    if np.all(values >= 0) and np.isclose(total, 1.0, atol=0.10):
        return values

    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    denominator = float(np.sum(exp_values))
    if denominator == 0 or not np.isfinite(denominator):
        raise ValueError("Could not normalize the model output scores.")
    return exp_values / denominator

def classify_once(
    model_path: str | Path = DEFAULT_MODEL,
    labels_path: str | Path = DEFAULT_LABELS,
    photo_path: str | Path | None = None,
    timeout: float = 300.0,
    top_k: int = 3,
    verbose: bool = False,
) -> dict[str, Any]:
    """Run one inference using the Raspberry Pi AI Camera and return results.

    Args:
        model_path: Path to the IMX500 ``network.rpk`` file.
        labels_path: Text file with one class name per line, in training order.
        photo_path: Optional path where the camera frame used for the result
            will be saved as an image. Parent directories are created as needed.
        timeout: Maximum number of seconds to wait for valid inference metadata.
        top_k: Number of highest-scoring classes to include in ``top_predictions``.
        verbose: If True, print initialization messages and the prediction.

    Returns:
        A dictionary with this structure::

            {
                "prediction": {"label": "...", "index": 0, "score": 0.98},
                "top_predictions": [
                    {"label": "...", "index": 0, "score": 0.98},
                    ...
                ],
                "model_path": "/.../network.rpk",
                "labels_path": "/.../labels.txt",
                "photo_path": "/.../result.jpg" or None,
            }

        Scores are fractions between 0 and 1. The camera is always stopped and
        closed before the function returns or raises an exception.

    Raises:
        FileNotFoundError: The model or label file does not exist.
        ValueError: Invalid arguments, empty labels, or unexpected output size.
        TimeoutError: No usable inference output arrived before ``timeout``.
        RuntimeError: The number of model output scores differs from the number
            of labels.
    """
    resolved_model = Path(model_path).expanduser().resolve()
    resolved_labels = Path(labels_path).expanduser().resolve()
    resolved_photo = Path(photo_path).expanduser().resolve() if photo_path else None

    if timeout <= 0:
        raise ValueError("timeout must be greater than 0 seconds.")
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")
    if not resolved_model.is_file():
        raise FileNotFoundError(f"RPK model not found: {resolved_model}")

    labels = load_labels(resolved_labels)

    if verbose:
        print(f"Modello: {resolved_model}")
        print(f"Classi ({len(labels)}): {', '.join(labels)}")
        print(
            "Inizializzo la Raspberry Pi AI Camera; il primo caricamento "
            "del modello può richiedere alcuni minuti..."
        )
    # Instantiate IMX500 before Picamera2 so the RPK is associated with the
    # camera before its pipeline starts.
    imx500 = IMX500(str(resolved_model))
    picam2 = Picamera2(imx500.camera_num)
    picam2.stop()
    camera_started = False

    try:
        # No preview window is opened. A short camera stream is still required
        # by the IMX500 to produce inference metadata.
        config = picam2.create_preview_configuration(buffer_count=4)
        picam2.configure(config)
        picam2.start()
        camera_started = True

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            request = picam2.capture_request()
            try:
                metadata = request.get_metadata()
                outputs = imx500.get_outputs(metadata)
                if outputs is None or len(outputs) < 1:
                    continue
                scores = np.asarray(outputs[0]).squeeze().astype(np.float32).reshape(-1)
                if scores.size != len(labels):
                    raise RuntimeError(
                        "The model output has "
                        f"{scores.size} scores, but labels.txt contains {len(labels)} labels. "
                        "Check class_names.json and labels.txt, and ensure this is the intended RPK."
                    )

                probabilities = as_probabilities(scores)
                count = min(top_k, len(labels))
                order = np.argsort(probabilities)[::-1][:count]
                top_predictions = [
                    {
                        "label": labels[int(index)],
                        "index": int(index),
                        "score": float(probabilities[int(index)]),
                    }
                    for index in order
                ]

                if resolved_photo is not None:
                    resolved_photo.parent.mkdir(parents=True, exist_ok=True)
                    request.save("main", str(resolved_photo))
                    if verbose:
                        print(f"Foto salvata: {resolved_photo}")
                result: dict[str, Any] = {
                    "prediction": top_predictions[0],
                    "top_predictions": top_predictions,
                    "model_path": str(resolved_model),
                    "labels_path": str(resolved_labels),
                    "photo_path": str(resolved_photo) if resolved_photo else None,
                }

                if verbose:
                    print_result(result)
                return result
            finally:
                request.release()

        raise TimeoutError(
            f"Nessun output di inferenza valido entro {timeout:.0f} secondi. "
            "Controlla il collegamento della AI Camera, il caricamento del firmware "
            "e il percorso del modello."
        )
    finally:
        if camera_started:
            picam2.stop()
        picam2.close()

def print_result(result: dict[str, Any]) -> None:
    """Print a result dictionary returned by :func:`classify_once`."""
    prediction = result["prediction"]
    print("\nRisultato classificazione:")
    print(
        f"  Predizione: {prediction['label']} "
        f"({prediction['score']:.1%})"
    )
    print("  Top classi:")
    for item in result["top_predictions"]:
        print(f"    {item['label']}: {item['score']:.1%}")

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for standalone use."""
    parser = argparse.ArgumentParser(
        description="Classify one camera frame using the Birdgarden IMX500 model."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Path to network.rpk (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--labels",
        default=DEFAULT_LABELS,
        help="Text file with one class name per line, in training class-index order.",
    )
    parser.add_argument(
        "--photo",
        default=DEFAULT_PHOTO,
        help="Optional path to save the camera frame used for inference, e.g. result.jpg.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Maximum seconds to wait for an inference result (default: 300).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top classes to return and print (default: 3).",
    )
    return parser.parse_args()



# funzione per la gestione della lettura dei dati dalla porta seriale a cui è collegato il micro:bit
porta = '/dev/ttyACM0'
baudrate = 115200

def leggi_dati_seriale(porta, baudrate):
    while True:
        try:
            # Apertura della connessione seriale
            with serial.Serial(porta, baudrate, timeout=1) as ser:
                # print(f"Connesso a {porta} a {baudrate} baud.")
                while True:
                    # Lettura dei dati
                    dati = ser.readline().decode('utf-8').rstrip()
                    if dati:
                        return dati

        except serial.SerialException as e:
            # Gestione errore di connessione
            print(f"Errore di connessione: {e}")
            print("Tentativo di riconnessione tra 5 minuti...")
            sleep(300)  # Attendi 5 minuti e riprova

# ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# la funzione verifica se è arrivato il comando di shutdown
def verifica_halt(array):
    if len(array) == 5 and all(elemento == '0' for elemento in array):
        return True
    return False

# funzione che impartisce il comando di chiusura del sistema
def arresta_sistema():
    try:
        # Esegue il comando di halt
        os.system("sudo shutdown -h now")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

# inizializza la fotocamera
# camera = Picamera2()
# nel caso di utilizzo di un LED infrarossi, l'anodo del LED (gamba lunga) è collegato al GPIO 17
# fra il catodo (gamba corta) e GROUND è necessario collegare una resistenza di almeno 100 ohm
# flash_led = LED(17)
# nel caso di utilizzo di motion sensor
# sensor = MotionSensor(14)

id = 0

# capture_config = camera.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640,480)})

# imposta il modo autofocus nel continuo
# camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# imposta il modo autofocus con alta velocità
# camera.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})

# imposta il focus in modalità manuale a 10cm, il minimo
# camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

# imposta la cattura di tre immagini consecutive
# camera.start_and_capture_files("fastfocus{:d}.jpg", num_files=3, delay=0.5)

# capture_config = camera.create_still_configuration()
# camera.configure(capture_config)

# uncomment this line if you want to record audio and set the appropriate device
# audio_device = "hw:1,0"

print ("Hello this is the start!")

while True:
    # rcv = ser.readline()
    # cmd = rcv.decode('utf-8').rstrip()
    cmd = leggi_dati_seriale(porta, baudrate)
    values = cmd.split(',')
    print(values)
    if len(values) == 5: 
      luce, temperatura, audio, pin0, sonar = [int(value) for value in values]
      print(luce, temperatura, audio, pin0, sonar)
      if verifica_halt(values):
         # Execute the sudo halt command
         print('devo arrestare il sistema')
         arresta_sistema()
      if pin0:
        id += 1
        print('fare foto!')
        # capture_config = camera.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640,480)})
        # capture_config = camera.create_still_configuration()
        #capture_config = camera.create_still_configuration(main={"size": (1920, 1080)})
        #camera.configure(capture_config) 
        #camera.start()
        # salva data/ora corrente in formato %Y%m%d-%H%M%S nella variabile
        valdata = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = "/usr/local/birdgarden/departures/" + str(valdata) + "_" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar)
        filename_ext = "/usr/local/birdgarden/msg/" + str(valdata) + "_" + str(id) + "_" + str(luce) + "_" + str(temperatura) + "_" + str(audio) + "_" + str(sonar)
        # flash_led.on()
        # camera.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
        # attendo un secondo per la messa a fuoco
        #sleep(2)
        # esegue la foto
        # camera.switch_mode_and_capture_file(capture_config, filename + ".jpg")
        #camera.capture_file(filename + ".jpg")
        # in caso di video
        # camera.start_and_record_video(filename + ".mp4", duration=30)
        # in caso di video + audio commentare la riga precedente e usare le seguenti
        # video_config = picam2.create_video_configuration({'size': (1280, 720), 'format': 'YUV420'})
        # camera.configure(video_config)
        # encoder = H264Encoder(bitrate=6_000_000)
        # encoder.audio = True
        # output = PyavOutput(filename + ".mp4")
        # camera.start_recording(encoder, output)
        # time.sleep(30)  # durata registrazione
        # camera.stop_recording()
        # flash_led.off()
        # Esegue una classificazione utilizzando la Raspberry Pi AI Camera
        # Calls the camera once and returns structured results without printing
        # internal status messages. Set verbose=True to display the result too.
        photo_name = filename + ".jpg"
        photo_name_ext = filename_ext + ".txt"
        print('photo_name: ', photo_name)
        result = classify_once(
            model_path="/usr/local/birdgarden/model/network.rpk",
            labels_path="/usr/local/birdgarden/model/labels.txt",
            photo_path=photo_name,
            timeout=300,
            top_k=3,
            verbose=True,
        )

        species = result["prediction"]["label"]
        score = result["prediction"]["score"]  # fraction: 0.0 to 1.0
        #print(f"Specie riconosciuta: {species} ({score:.1%})")

        # Example use in program logic:
        if score >= 0.80:
            print("Risultato con punteggio elevato.")
            testo_messaggio = f"Rilevamento attendibile\nTemp: {temperatura}C Luce: {luce}\n"
            testo_messaggio += f"Rumore: {audio} Distanza: {sonar}cm\n"
        else:
            print("Risultato incerto: potrebbe essere utile acquisire un'altra immagine.")
            testo_messaggio = f"Rilevamento incerto\nTemp: {temperatura}C Luce: {luce}\n"
            testo_messaggio += f"Rumore: {audio} Distanza: {sonar}cm\n"
        # All ranked species and scores are available to the caller:
        for item in result["top_predictions"]:
            #print(item["index"], item["label"], f"{item['score']:.1%}")
            testo_messaggio += f"{item['label']}, {item['score']:.1%}\n"

        #try:
            # Esegue il comando di invio LoRa
        #    os.system("meshtastic --serial /dev/ttyUSB0 --ch-index 2 --sendtext \"Specie riconosciuta: {specie} Punteggio: {punteggio:.1%}\"")
        #except Exception as e:
        #    print(f"Si è verificato un errore con LoRa: {e}")
        #camera.stop()
        # Formattazione del testo del messaggio (limitato in caratteri per LoRa)
        print(f"Invio via LoRa: {testo_messaggio}")
        with open(photo_name_ext, "w", encoding="utf-8") as file:
            file.write(testo_messaggio)
        
        try:
            # Connessione all'Heltec V3 e invio sul canale 'Birdgarden' (es. ch-index 2)
            interface = meshtastic.serial_interface.SerialInterface("/dev/ttyUSB0")
            interface.sendText(testo_messaggio, channelIndex=2)
            time.sleep(3)  # Lascia il tempo per la trasmissione
            interface.close()
            print("Messaggio LoRa inviato con successo!")
        except Exception as e:
            print(f"Si è verificato un errore con LoRa: {e}")
      # sleep(1)
done
