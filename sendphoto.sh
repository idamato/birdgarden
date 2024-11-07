#!/usr/bin/bash

WORKDIR=/home/ilfarodargento/software/
CPUID=$(cat /proc/cpuinfo | grep Serial | cut -f2 -d":"|awk '{$1=$1};1')
DATA=$(date +"%Y%m%d%H%M%S")

cd $WORKDIR/departures

for item in $(ls -1); do
  echo "ls -l $item"
  scp $item ilfarodargento@pavillone.hopto.org:/home/ilfarodargento/arrivals/$CPUID.$DATA.$item
  mv $item ../sent/
done
