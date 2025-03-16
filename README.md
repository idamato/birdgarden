# birdgarden
Birdgarden 2.0
Progetto realizzato a cura dei soci di il faro d'argento APS (www.webradiofaro.it)
 
Il progetto Birdgarden 2.0 mira alla realizzazione di una casetta/nido o mangiatoia per gli uccellini, monitorata attraverso una camera ed un microfono nascosti che metterà a disposizione su internet i dati rilevati, l’audio e le foto scattate nei momenti in cui viene occupata. 

Per l'inizializzazione del dispositivo al primo utilizzo sono necessarie alcune attività per le quali è necessario collegare al dispositivo un monitor o TV tramite il cavo HDMI ed una tastiera+mouse tramite il cavo USB aggiuntivo. In alternativa è possibile configurare il sistema raspberry attraverso una connessione seriale, per mezzo di un cavo del tipo USB-to-SERIAL con chip PL2303, facendo attenzione al fatto che sia utilizzabile con la tensione dei 3V dei GPIO del Raspberry.
Per il collegamento attraverso la porta seriale è necessario abilitarne l'accesso nel file config.txt inserendo la seguente riga: enable_uart=1
Nelle versioni più recenti del sistema Raspian OS non esiste un utente preconfigurato con cui eseguire il login tuttavia tramie il software Raspberry Pi Imager è possibile definire le principali configurazioni prima ancora del primo avvio, cosa che in questo progetto abbiamo fatto per voi. Per i sistemi Linux Debian è sufficiente digitare il comando: sudo apt install rpi-imager, mentre per Windows si può scaricare l'installer direttamente dal sito raspberrypi.com
Per il collegamento via seriale abbiamo utilizzato il comando: tio /dev/ttyUSB0, dopo aver verificato che il device ttyUSB0 fosse correttamente associato al cavo USB-to-serial inserito, per mezzo del comando: sudo dmesg, che fornisce le seguenti informazioni:
[ 7849.113480] usb 1-2: new full-speed USB device number 13 using xhci_hcd
[ 7849.240467] usb 1-2: New USB device found, idVendor=067b, idProduct=2303, bcdDevice= 4.00
[ 7849.240514] usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[ 7849.240537] usb 1-2: Product: USB-Serial Controller
[ 7849.240555] usb 1-2: Manufacturer: Prolific Technology Inc.
[ 7849.245418] pl2303 1-2:1.0: pl2303 converter detected
[ 7849.248483] usb 1-2: pl2303 converter now attached to ttyUSB0


Quindi occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi. Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera e maouse tramite il cavetto USB, il monitor con adattatore mini HDMI (in alternativa si utilizzi la connessione seriale) ed il camera module con il cavo apposito.
Eseguire le operazioni seguenti:

- eseguire il login con username e password
- eseguire l’aggiornamento di Linux con i comandi:
- sudo apt update && sudo apt upgrade
- sudo apt install -y python3-picamera2
- sudo apt install -y ffmpeg
- installare le librerie Python necessarie
- pip install serial picamera2 requests base64
- scaricare il software dal repository GITHUB
- sudo install git
- git clone https://github.com/idamato/birdgarden/
- modificare i permessi ai file scaricati con chmod a+x birdgarden/*.sh birdgarden/*.py
- modificare username e password e identificativo TAG con la CPUID nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto.
- creare il link simbolico al file photo.service di avvio del servizio al boot:
 ln -s /etc/systemd/system/photo.service /home/birdgarden/scripts/photo.service
- configurare il comando a tempo (crontab -e) aggiungendo in fondo la seguente riga:
 * * * * * /home/ilfarodargento/birdgarden/sendphoto.sh >> /home/ilfarodargento/logs/cron.log 2>&1
- esegure il test del focus della fotocamera sulla vostra installazione con lo script test-camera-focus.py
- collegare anche il dispositivo micro:bit caricandovi il codice serial_data_logger.py tramite il sito makecode.microbit.org
- creare le due directory che conterranno le foto scattate e quelle spedite e i log
- mkdir departures sent logs





           
