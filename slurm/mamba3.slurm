#!/usr/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o bioinfo_%j.out
#SBATCH --export=NONE

# slightly different from mamba.slurm

echo "running on: $(hostname) : ${SLURM_TASK_PID} with mamba=${MAMBA_EXE}"

# command just returns a string of exports that needs to be evaluated viz:

# export PATH='...'
# export CONDA_PREFIX='/group/peb007/micromamba/envs/py312'
# export CONDA_SHLVL='1'
# export CONDA_DEFAULT_ENV='py312'
# export CONDA_PROMPT_MODIFIER='(py312) '

# environment created with (say) `micromamba env create -n py312 python=3.12`

eval "$($MAMBA_EXE shell activate py312 --shell bash)"
echo "activated ${CONDA_PREFIX} with python version: $(python -V) @ $(which python)"
# run your scripts..

# NB: *not* `micromamba deactivate`
${MAMBA_EXE} shell deactivate
echo "done."
