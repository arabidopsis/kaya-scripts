#!/usr/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE
# environment created by micromamba env create -n py312 python=3.12
# ** don't need micromamba setup by the user **
export CONDA_DEFAULT_ENV=py312
module load mamba

echo "activated ${CONDA_PREFIX}"
echo "with python version: $(python -V) @ $(which python)"
# run your scripts..

module unload mamba
echo "done."
