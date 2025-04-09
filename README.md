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

Quindi occorre scaricare ed installare Raspberry Pi OS sulla scheda SSD utilizzando il software Raspberry Pi Imager, completando la configurazione iniziale dell’utente e del wi-fi. Inserire successivamente la scheda SSD nel Raspberry Pi Zero 2W, collegarvi una tastiera e maouse tramite il cavetto USB, il monitor con adattatore mini HDMI (in alternativa si utilizzi la connessione seriale) ed il camera module con il cavo apposito. Tenete a mente che durante il primo avvio il sistema opera delle configurazioni automatiche ed esegue anche un riavvio automatico, quindi impiega necessariamente più tempo a partire rispetto ad una normale procedura di avvio, come potranno essere quelle successive. Se tutto è andato a buon fine avrete a video il desktop del sistema Raspian OS (derivato da Linux Debian) e potrete aprire una finestra terminale per proseguire con le attività di configurazione descritte nel seguito.

Eseguire le operazioni seguenti:

- eseguire il login con username e password impostati (l'importante è che la home directory si chiami /home/ilfarodargento)
- eseguire l’aggiornamento di Linux con i comandi:
- sudo apt update && sudo apt upgrade (occorre rispondere con Y confermando l'attività - questo task può durare anche 30 minuti)
- se le librerie python-picamera2 non sono installate potete usare il comando: sudo apt install -y python3-picamera2
- se le librerie per il video non sono installate potete usare il comando: sudo apt install -y ffmpeg
- installare le librerie Python necessarie
- la maggior parte delle librerie python3 sono installate, occorre ancora il comando seguente per la libreria seriale: sudo apt install python3-serial
- scaricare il software dal repository GITHUB
- sudo install git
- git clone https://github.com/idamato/birdgarden/
- modificare i permessi ai file scaricati con chmod a+x birdgarden/\*.sh birdgarden/\*.py birdgarden/photo.service
- modificare username e password e identificativo TAG con la CPUID nel file wordpress_playground.py secondo le indicazioni ricevute al momento dell'adesione al progetto. (Viene creato un account all'interno del portale Birdgarden 2.0 con le credenziali per la pubblicazione delle foto/video dal dispositivo)
- creare il link simbolico al file photo.service di avvio del servizio al boot:
  sudo cp /home/ilfarodargento/birdgarden/photo.service /lib/systemd/system/photo.service ;
  sudo systemctl enable photo.service ; 
  sudo systemctl start photo.service (comando per l'avvio manuale) ;
  sudo journalctl --unit=photo.service (per verificare il log delle esecuzioni precedenti)
- configurare il comando a tempo (crontab -e) aggiungendo in fondo la seguente riga:
  30 * * * * /home/ilfarodargento/birdgarden/sendphoto.sh >> /home/ilfarodargento/logs/cron.log 2>&1
- dalla /home/ilfarodargento creare le directory per i log e per le foto da spedire e spedite con: mkdir logs departures sent
- esegure il test del focus della fotocamera sulla vostra installazione eseguendo il comando: python3 test-camera-focus.py, tenete presente che se state utilizzando il terminale senza grafica dovrete prima modificare lo script impostando la preview a False.
- collegare anche il dispositivo micro:bit caricandovi il codice serial_data_logger.py tramite il sito makecode.microbit.org

Se si desidera modificare la configurazione del WiFi si può procedere nel modo seguente:
- eseguire il comando: sudo nmtui, ed abilitare la rete wifi di interesse

Ci sono inoltre una serie di aspetti di configurazione che sono stati curati all'interno del portale https://www.webradiofaro.it/birdgarden/ che utilizza Wordpress.
In particolare deve essere creato un utente/ruolo specifico associato al dispositivo in modo che nello stesso portale possano concorrere le pubblicazioni di tutti i dispositivi.
Oltre all'utente deve essere anche creata una chiave applicativa legata all'applicazione Birdgarden e con essa si avranno le credenziali da inserire nello scirpt Python per l'invio dati.

           
