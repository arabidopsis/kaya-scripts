#!/bin/bash
mkdir -p keys
mkdir -p  keys/public
mkdir -p keys/private
for dir in /mnt/s-ws/s-*
do

	student=$(basename $dir)
    ssh-keygen -t rsa -b 4096 -q -N '' -f keys/s-${student}-key
    mv keys/s-${student}-key keys/private
    mv keys/s-${student}-key.pub keys/public

done
