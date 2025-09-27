#!/usr/bin/bash

ps -ef|grep serialandphoto|grep -v grep
#if [ $? -ne 0 ]; then
#  systemctl start photo.service
#fi
