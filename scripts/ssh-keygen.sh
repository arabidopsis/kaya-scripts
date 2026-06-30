#!/bin/bash
source ./ssh-functions.sh

mkdir -p keys
mkdir -p keys/public
mkdir -p keys/private

for dir in ${MOUNT}s/s-*
do

	student=$(basename $dir)
    keygen $student

done
