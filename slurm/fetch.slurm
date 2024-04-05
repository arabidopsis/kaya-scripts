#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE

# Because we have no sudo access....

# mountirds uses the gnome gio executables which need a
# running "session" i.e. a user -- usually -- needs to be
# logged in. If we log out of Kaya we will kill our user session
# Luckily we can create a "session" with `dbus-run-session` 
# while we are logged out and this script is running somewhere.

RUN="<script to run that needs access to IRDS files>"

dbus-run-session -- bash -c "/group/peb007/kaya-scripts/bin/mountirds && source ${RUN}"

echo "done"
