# birdgarden
Birdgarden 2.0

Occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi.
Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera tramite il cavetto USB, il monitor con adattatore mini HDMI ed il camera module con il cavo apposito
Eseguire le operazioni seguenti:

1. eseguire il login con username e password
2. eseguire l’aggiornamento di Linux con:
          sudo apt update && sudo apt upgrade
3. installare le librerie Python necessarie
           pip install serial picamera2 requests base64
4. scaricare il software dal repository GIT
           git clone https://github.com/idamato/birdgarden/
5. modificare username e password nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto.
6. configurare i comandi a tempo (crontab)
           
