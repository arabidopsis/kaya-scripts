#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE

# export JULIAUP_DEPOT_PATH=/group/peb007/.julia
# curl -fsSL https://install.julialang.org | sh
# specify custom install and place juliaup in /group/peb007/.juliaup
# mv ~/.julia /group/peb007
# export PATH=/group/peb007/.juliaup/bin${PATH:+:${PATH}}
module load julia/1.10.2
echo "running on: $(hostname) : ${SLURM_TASK_PID} julia=$(julia -e 'print(Sys.BINDIR)')"

# expecting /group/peb007/.julia
echo "depot=$JULIA_DEPOT_PATH"

julia -e 'println("version is: $(VERSION)")'

# module unload julia/1.10.0
echo "done."
