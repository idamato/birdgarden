#!/bin/bash


# Verificare che l'id sia 1 aka root

# Creazione utente

groupadd -g 192 birdgarden
useradd  -u 192 -g 192 -s /usr/sbin/nologin -G dialout,video -d /usr/local/birdgarden/ birdgarden

# Creazione /usr/local/birdgarden/

mkdir -p /usr/local/birdgarden/
mkdir -p /var/log/birdgarden/
mkdir -p /usr/local/birdgarden/departures/
mkdir -p /usr/local/birdgarden/sent/
mkdir -p /usr/local/birdgarden/sentviaradio/

chmod 755 -R /usr/local/birdgarden/

crontab -u birdgarden src/crontabs/sendphoto

# Dirty Hack ... we need the birdgarden user
chmod 777 /var/log/birdgarden/
# copia binari

cp src/*.py /usr/local/birdgarden/
cp -a  src/scripts/ /usr/local/birdgarden/
chmod +x /usr/local/birdgarden/*.py /usr/local/birdgarden/scripts/*.sh

cp src/logrotate/* /etc/logrotate.d

# Installazione unit systemd  src/systemd/photo.service

cp src/systemd/photo.service /etc/systemd/system

chown birdgarden:birdgarden /usr/local/birdgarden/ -R

systemctl daemon-reload
systemctl enable photo.service
systemctl start photo.service

apt update -y \
  && apt upgrade -y \
  && apt full-upgrade -y
