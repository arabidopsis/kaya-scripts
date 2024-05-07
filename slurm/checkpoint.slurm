#!/bin/bash
#SBATCH --partition=work
#SBATCH -n 1
#SBATCH -o chkpt_%j.out
#SBATCH --export=NONE
# run for 1 1/2 minutes
#SBATCH --time=0-00:01:30
# signal process 10 seconds before end
#SBATCH --signal=SIGUSR1@10
# environment created by micromamba env create -n py312 python=3.12

# This is different in that you
# ** don't need micromamba setup by the user **

# specify which environment you want
export CONDA_DEFAULT_ENV=py312
# load the environment
module load activate-env
# pip install click
srun $(which python) scripts/sigtest.py --auto-requeue

# with auto_requeue seem to get this in the output:
# srun: Job step aborted: Waiting up to 32 seconds for job step to finish.
# slurmstepd: error: *** JOB 443741 ON n031 CANCELLED AT 2024-05-07T11:28:20 DUE TO JOB REQUEUE ***
# and no "done" in the output either...
# But otherwise it seems to work
echo "done."
