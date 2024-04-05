#!/usr/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE

# best way is to run a session and 

# dbus-run-session -- bash -c "~/mountirds.sh && source ${RUN}"
# dbus-run-session -- ~/readirds.sh
sleep 30
echo "dbus=$DBUS_SESSION_BUS_ADDRESS"
~/readirds.sh
echo "done"
