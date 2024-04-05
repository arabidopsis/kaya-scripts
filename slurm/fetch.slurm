#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE

# best way is to run a session and

RUN="<script to run>"

dbus-run-session -- bash -c "/group/peb007/kaya-scripts/bin/mountirds && source ${RUN}"

echo "done"
