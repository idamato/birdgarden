#!/usr/bin/bash
COUNT=$(ps -ef|grep sendphoto.sh|grep -v grep|wc -l)
if [ $COUNT -gt 2 ]; then
  echo "processo già in esecuzione... esco"
  exit 1
fi

WORKDIR=/home/ilfarodargento
CPUID=$(cat /proc/cpuinfo | grep Serial | cut -f2 -d":"|awk '{$1=$1};1')
#DATA=$(date +"%Y/%m/%d-%H:%M:%S")
DATA=$(date +"%Y%m%d-%H%M%S")

cd $WORKDIR/departures

for item in $(ls -1); do
  echo "ls -l $item"
  # esegue un ping per la verifica della linea internet
  ping -c 3 www.webradiofaro.it
  if [ $? -eq 0 ]; then
    # esegue la pubblicazione dell'articolo in wordpress poiché c'è connessione internet
    /usr/bin/python ../birdgarden/wordpress_playground.py $CPUID $DATA $item && mv $item ../sent/
  else
    # linea internet assente o non funzionante
    echo "non trovo connessione con internet"
    exit 1
  fi
done
