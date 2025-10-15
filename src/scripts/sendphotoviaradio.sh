#!/usr/bin/bash -x

# Nome del file di lock
LOCKFILE="/tmp/sendphotoviaradio.lock"

# Funzione per pulire il file di lock
cleanup() {
    rm -f "$LOCKFILE"
}

# Controlla se il file di lock esiste e se il processo è ancora attivo
if [ -e "$LOCKFILE" ]; then
    LOCKPID=$(cat "$LOCKFILE")
    if ps -p "$LOCKPID" > /dev/null 2>&1; then
        echo "Lo script è già in esecuzione con PID: $LOCKPID. Termino."
        exit 1
    else
        echo "Rilevato file di lock obsoleto. Lo rimuovo e procedo."
        rm -f "$LOCKFILE"
    fi
fi

# Crea un file di lock con il PID corrente
echo $$ > "$LOCKFILE"
LOCKPID=$(cat "$LOCKFILE")

WORKDIR=/usr/local/birdgarden
DATA=$(date -u +"%d/%m/%Y-%H:%M:%S")

cd $WORKDIR/sent

for item in $(ls -1); do
  echo "ls -l $item"
  # eseguire il comando convert verificando le coordinate in base alla foto scattata, usare dir di appoggio con nomi LOCKPID
  #convert "$item" -resize 320x256! -pointsize 36 -fill white -annotate +10+40 'CQ IQ0OS' -pointsize 24 -fill red -annotate +10+70 '#MKFR2025' -pointsize 20 -fill navy -annotate +10+100 'Birdgarden 2.0 radio mod' ../templates/AriOstia_logo_mini.png -gravity southeast -composite /tmp/step1.jpg;convert /tmp/step1.jpg ../templates/logo_faro_mini.png -gravity east -composite /tmp/step2.jpg ;convert /tmp/step2.jpg ../templates/logo-birdgarden-mini.png -gravity northeast -composite /tmp/final.jpg
  echo "convert $item -resize 320x256! -pointsize 36 -fill white -annotate +10+40 'CQ IQ0OS' -pointsize 24 -fill white -annotate +10+70 '#MKFR2025  73!' -pointsize 20 -fill white -annotate +10+95 '$DATA' ../templates/AriOstia_logo_mini.png -gravity northeast -composite /tmp/step1.jpg;convert /tmp/step1.jpg ../templates/logo_faro_mini.png -gravity east -composite /tmp/step2.jpg ;convert /tmp/step2.jpg ../templates/logo-birdgarden-mini.png -gravity southeast -composite /tmp/final.jpg">/tmp/step_convert.sh
  bash /tmp/step_convert.sh
  # produrre il file .wav da inviare su audio, usare dir di appoggio con nomi LOCKPID
  python -m pysstv --mode Robot36 --vox /tmp/final.jpg /tmp/final.wav
  # suonare il file .wav
  aplay /tmp/final.wav
  # spostare il file della foto da sent a sentviaradio anche con i jpg modificati ed il wav
  mv $item ../sentviaradio/
  mv /tmp/final.jpg ../sentviaradio/sstv.$item
  mv /tmp/final.wav ../sentviaradio/audio.$item
  rm /tmp/step*
done
# Rimuoviamo il file di lock alla fine dello script
trap cleanup EXIT
