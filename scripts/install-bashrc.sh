#!/bin/bash
for dir in /mnt/s-ws/s-*
do
	st=$(basename $dir)
	echo "$st: installing"
	cp /mnt/s-ws/env/bashrc "$dir/.bashrc"
	chown $st:$st "$dir/.bashrc"
	cp /mnt/s-ws/env/bash_profile "$dir/.bash_profile"
	chown $st:$st "$dir/.bash_profile"
done
