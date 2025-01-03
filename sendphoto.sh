#!/usr/bin/bash

WORKDIR=/home/ilfarodargento/birdgarden/
CPUID=$(cat /proc/cpuinfo | grep Serial | cut -f2 -d":"|awk '{$1=$1};1')
DATA=$(date +"%Y%m%d%H%M%S")

cd $WORKDIR/departures

for item in $(ls -1); do
  echo "ls -l $item"
  #scp $item ilfarodargento@<serverFQDN>:/home/ilfarodargento/arrivals/$CPUID.$DATA.$item
  ../wordpress_playground.py $CPUID $DATA $item && mv $item ../sent/
done
