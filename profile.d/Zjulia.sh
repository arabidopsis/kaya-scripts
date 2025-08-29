# /etc/profile.d/Zjulia.sh
# need the Z so module use is done last
export PATH=/var/legends/bin:$PATH
export JULIA_DEPOT_PATH=/var/legends/juliaup
export JULIAUP_DEPOT_PATH=$JULIA_DEPOT_PATH
if [ "$(type -t module)" = "function" ]; then
    module use -p /var/legends/modules
fi
