#!/usr/bin/bash

# Nome del file di lock
LOCKFILE="/tmp/sendloraping.lock"

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

# Invio il msg di attività sul canale Birdgarden
meshtastic --ch-index 2 --port /dev/ttyUSB0 --sendtext "Alive: $(date)"

# Rimuoviamo il file di lock alla fine dello script
trap cleanup EXIT
