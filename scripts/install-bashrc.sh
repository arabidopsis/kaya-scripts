#!/bin/bash
MOUNT=/mnt/s-ws
# ensure each student has a home directory
# owned by them and with .bashrc/.bash_profile files
for dir in ${MOUNT}/s-*
do
	st=$(basename $dir)
	echo "$st: installing bashrc"
	chown $st:$st $dir
	cp ${MOUNT}/env/bashrc "$dir/.bashrc"
	chown $st:$st "$dir/.bashrc"
	cp ${MOUNT}/env/bash_profile "$dir/.bash_profile"
	chown $st:$st "$dir/.bash_profile"
done
