#!/bin/bash


# Verificare che l'id sia 1 aka root

# Creazione utente

groupadd -g 192 birdgarden
useradd  -u 192 -g 192 -s /usr/sbin/nologin -G dialout -d /usr/local/birdgarden/ birdgarden

# Creazione /usr/local/birdgarden/

mkdir -p /usr/local/birdgarden/
mkdir -p /var/logs/birdgarden/logs/
mkdir -p /usr/local/birdgarden/departures/
mkdir -p /usr/local/birdgarden/sent/
chmod 755 -R /usr/local/birdgarden/


# Dirty Hack ... we need the birdgarden user
chmod 777 /var/logs/birdgarden/
# copia binari

cp src/*.py /usr/local/birdgarden/
cp -a  src/scripts/ /usr/local/birdgarden/
chmod +x /usr/local/birdgarden/*.py

cp src/logrotate/* /etc/logrotate.d

# Installazione unit systemd  src/systemd/photo.service

cp src/systemd/photo.service /etc/systemd/system

chown birdgarden:birdgarden /usr/local/birdgarden/ -R

systemctl daemon-reload
systemctl start photo.service


apt update -y \
  && apt upgrade -y \
  && apt full-upgrade -y

sudo apt update && \
  sudo apt install -y python3-picamera2\
                      ffmpeg \
                      git \
                      python3-serial

echo 'tmpfs   /tmp/ramdisk    tmpfs  rw,size=30M,nr_inodes=5k,noexec,nodev,nosuid,uid=ubuntu,gid=ubuntu,mode=1700 0 0' >> /etc/fstab
