# birdgarden
Birdgarden 2.0

Occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi.
Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera tramite il cavetto USB, il monitor con adattatore mini HDMI ed il camera module con il cavo apposito
Eseguire le operazioni seguenti:

eseguire il login con username e password
eseguire l’aggiornamento di Linux con:
          sudo apt update && sudo apt upgrade
installare le librerie Python necessarie
           pip install serial 
scaricare il software dal repository GIT
           git...
configurare i comandi a tempo (crontab)
