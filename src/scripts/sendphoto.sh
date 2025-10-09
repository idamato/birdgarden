#!/usr/bin/bash

# Nome del file di lock
LOCKFILE="/tmp/sendphoto.lock"

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

WORKDIR=/usr/local/birdgarden
CPUID=$(cat /proc/cpuinfo | grep Serial | cut -f2 -d":"|awk '{$1=$1};1')
#DATA=$(date +"%Y/%m/%d-%H:%M:%S")
DATA=$(date +"%Y%m%d-%H%M%S")
DISK=$(df -h -l --output=size,used / | tail -1)
UPTIME=$(uptime)
SENT=$(ls -1 $WORKDIR/sent | wc -l)
DEPARTURES=$(ls -1 $WORKDIR/departures | wc -l)

cd $WORKDIR/departures
ping -c 3 www.webradiofaro.it
PINGSTATUS=$?

for item in $(ls -1); do
  echo "ls -l $item"
  # esegue un ping per la verifica della linea internet
  if [ $PINGSTATUS -eq 0 ]; then
    # esegue la pubblicazione dell'articolo in wordpress poiché c'è connessione internet
    /usr/bin/python ../birdgarden/wordpress_playground.py $CPUID $DATA $item && mv $item ../sent/
  else
    # linea internet assente o non funzionante
    echo "Ho $DEPARTURES file da spedire ma non trovo connessione con internet"
    # Rimuoviamo il file di lock alla fine dello script
    trap cleanup EXIT
    exit 1
  fi
done
# Invio il monitoraggio
if [ $PINGSTATUS -eq 0 ]; then
  curl -s -X POST "https://www.webradiofaro.it/birdgarden/wp-json/call-logger/v1/call?api_key=dfResYfQnvaPCEaGMnE0FuChwqZttIvGo6LU4ymF" \
  -H "Content-Type: application/json" \
  -d '{"data":"'"$DATA"'","cpuid":"'"$CPUID"'","uptime":"'"$UPTIME"'","disk":"'"$DISK"'","sent":"'"$SENT"'","departures":"'"$DEPARTURES"'"}'
fi
# Rimuoviamo il file di lock alla fine dello script
trap cleanup EXIT
