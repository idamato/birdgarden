# birdgarden
Birdgarden 2.0
 
Il progetto Birdgarden 2.0 mira alla realizzazione di una casetta/nido o mangiatoia per gli uccellini, monitorata attraverso una camera ed un microfono nascosti che metterà a disposizione su internet i dati rilevati, l’audio e le foto scattate nei momenti in cui viene occupata.

Occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi.
Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera tramite il cavetto USB, il monitor con adattatore mini HDMI ed il camera module con il cavo apposito
Eseguire le operazioni seguenti:

- eseguire il login con username e password
- eseguire l’aggiornamento di Linux con i comandi:
- sudo apt update && sudo apt upgrade
- sudo apt install -y python3-picamera2
- installare le librerie Python necessarie
- pip install serial picamera2 requests base64
- scaricare il software dal repository GITHUB
- sudo install git
- git clone https://github.com/idamato/birdgarden/
- modificare i permessi ai file scaricati con chmod a+x birdgarden/*.sh birdgarden/*.py
- modificare username e password e identificativo TAG con la CPUID nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto.
- configurare il comando a tempo (crontab -e) aggiungendo in fondo la seguente riga:
- * * * * * /home/ilfarodargento/birdgarden/sendphoto.sh >> /home/ilfarodargento/cron.log 2>&1
- esegure il test del focus della fotocamera sulla vostra installazione con lo script test-camera-focus.py
- collegare anche il dispositivo micro:bit caricandovi il codice serial_data_logger.py tramite il sito makecode.microbit.org
- creare le due directory che conterranno le foto scattate e quelle spedite
- mkdir departures sent
    





           
