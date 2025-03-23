#!/usr/bin/bash

WORKDIR=/home/ilfarodargento
CPUID=$(cat /proc/cpuinfo | grep Serial | cut -f2 -d":"|awk '{$1=$1};1')
DATA=$(date +"%Y/%m/%d-%H:%M:%S")

cd $WORKDIR/departures

for item in $(ls -1); do
  echo "ls -l $item"
  # esegue la pubblicazione dell'articolo in wordpress
  /usr/bin/python ../birdgarden/wordpress_playground.py $CPUID $DATA $item && mv $item ../sent/
done
