# birdgarden
Birdgarden 2.0

Il progetto Birdgarden 2.0 mira alla realizzazione di una casetta/nido o mangiatoia per gli uccellini, monitorata attraverso una camera ed un microfono nascosti che metterà a disposizione su internet i dati rilevati, l’audio e le foto scattate nei momenti in cui viene occupata.

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
5. modificare username e password e identificativo TAG con la CPUID nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto.
6. configurare il comando a tempo (crontab -e)

           
