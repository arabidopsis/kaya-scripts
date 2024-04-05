#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE


# "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
# source ~/.bashrc
# micromamba create -n py312 python=3.12

echo "running on: $(hostname) : ${SLURM_TASK_PID} with mamba=${MAMBA_EXE}"

eval "$(${MAMBA_EXE} shell hook --shell bash)"
# ${MAMBA_ROOT_PREFIX} is the prefix where environments are stored....
micromamba activate py312
echo "activated ${MAMBA_ROOT_PREFIX} with python version: $(python -V) @ $(which python)"
# run your scripts..

micromamba deactivate
echo "done."
