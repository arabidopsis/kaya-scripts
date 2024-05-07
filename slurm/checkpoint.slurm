#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o chkpt_%j.out
#SBATCH --export=NONE
#SBATCH --time=0-00:03:00
#SBATCH --signal=SIGUSR1@90
# environment created by micromamba env create -n py312 python=3.12

# This is different in that you
# ** don't need micromamba setup by the user **

# specify which environment you want
export CONDA_DEFAULT_ENV=py312
# load the environment
module load activate-env

python scripts/signal.py

echo "done."
