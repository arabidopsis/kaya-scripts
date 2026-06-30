#!/bin/bash
source ./ssh-functions.sh

rm -rf ${KEYS}
mkdir -p ${KEYS}
mkdir -p ${KEYS}/public
mkdir -p ${KEYS}/private

for dir in ${MOUNT}/s-*
do

	student=$(basename $dir)
    keygen $student

done
