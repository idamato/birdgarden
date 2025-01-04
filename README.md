# birdgarden
Birdgarden 2.0
 
Il progetto Birdgarden 2.0 mira alla realizzazione di una casetta/nido o mangiatoia per gli uccellini, monitorata attraverso una camera ed un microfono nascosti che metterà a disposizione su internet i dati rilevati, l’audio e le foto scattate nei momenti in cui viene occupata.

Occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi.
Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera tramite il cavetto USB, il monitor con adattatore mini HDMI ed il camera module con il cavo apposito
Eseguire le operazioni seguenti:

1. eseguire il login con username e password
2. eseguire l’aggiornamento di Linux con i comandi:
          sudo apt update && sudo apt upgrade
          sudo apt install -y python3-picamera2
4. installare le librerie Python necessarie
           pip install serial picamera2 requests base64
5. scaricare il software dal repository GIT
           git clone https://github.com/idamato/birdgarden/
6. modificare i permessi ai file scaricati con chmod a+x birdgarden/*.sh birdgarden/*.py
7. modificare username e password e identificativo TAG con la CPUID nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto.
8. configurare il comando a tempo (crontab -e) aggiungendo in fondo la seguente riga:
   * * * * * /home/ilfarodargento/birdgarden/sendphoto.sh >> /home/ilfarodargento/cron.log 2>&1
9. esegure il test del focus della fotocamera sulla vostra installazione con lo script test-camera-focus.py
10. collegare anche il dispositivo micro:bit caricandovi il codice serial_data_logger.py tramite il sito makecode.microbit.org
11. creare le due directory che conterranno le foto scattate e quelle spedite
    mkdir departures sent
    





           
