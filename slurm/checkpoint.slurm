#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o chkpt_%j.out
#SBATCH --export=NONE
# run for three minutes
#SBATCH --time=0-00:03:00
# signal process 90 seconds before end
#SBATCH --signal=SIGUSR1@90
# environment created by micromamba env create -n py312 python=3.12

# This is different in that you
# ** don't need micromamba setup by the user **

# specify which environment you want
export CONDA_DEFAULT_ENV=py312
# load the environment
module load activate-env

srun python scripts/signal.py

echo "done."
