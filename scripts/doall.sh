#!/bin/bash

# git clone https://github.com/arabidopsis/kaya-scripts.git
# cd kaya-scripts/scripts

TARGET=/mnt/s-ws

CODE_DIR=$TARGET/env

sudo mkdir -p $CODE_DIR
sudo chown conny:conny $CODE_DIR

# **also put this in *your* ~/.bashrc file**
# **NOTE** colon at end of JULIA_DEPOT_PATH
export JULIAUP_DEPOT_PATH=${CODE_DIR}/julia
export JULIA_DEPOT_PATH="${JULIAUP_DEPOT_PATH}:"

TOOLSDIR=$JULIAUP_DEPOT_PATH/tools

# install juliaup
# juliaup will put everything (julia executables) in $JULIAUP_DEPOT_PATH/juliaup directory
# but juliaup executable itself will go into ~/.juliaup/bin/
curl -fsSL https://install.julialang.org | sh
source ~/.bashrc

# install your preferred version of julia (into JULIAUP_DEPOT_PATH)
juliaup

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
# install micromamba
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
source ~/.bashrc
# chloe installed into $TOOLSDIR/bin
uv run exe-install.py install --main=chloe_main  https://github.com/ian-small/Chloe.jl.git

# create a conda environment 
SCIENV="${CODE_DIR}/scie4002"

# empty
micromamba env create --prefix=${SCIENV}
micromamba activate ${SCIENV}
micromamba install -c conda-forge -c bioconda -c defaults \
    mafft \
    mashtree \
    iqtree \
    mrbayes \
    bbmap \
    samtools \
    bcftools \
    bedtools \
    getorganelle

# 4.9G total size

# while we are here ensure that we have click installed
python -m pip install click
# create standalone deactivation script scie4002-deactivate.sh
uv run exe-install.py mamba --deactivate --no-path
micromamba deactivate
# extra environment twiddling 
# writes a scie4002-activate.sh file
uv run exe-install.py mamba ${SCIENV}

# possibly **EDIT** scie4002-activate.sh
# fix PATH to your liking i.e. Add `$TOOLSDIR/bin` to PATH
# copy these over
cp scie4002-activate.sh scie4002-deactivate.sh conny.sh bashrc bash_profile ${CODE_DIR}/

# setup ian small's julia "scripts"

# just create a project with FASTX and BioSequences installed
uv run exe-install.py install --package=Scripts FASTX BioSequences
# "executify" the julia scripts
uv run exe-install.py executify Scripts /mnt/s-ws/everyone/tools/*.jl

# now, say, fasta2nex.jl should be just a bash script
# ($TOOLSDIR/bin/fasta2nex.jl)
# that "runs" /mnt/s-ws/everyone/tools/fasta2nex.jl using the correct julia and
# correct JULIA_DEPOT_PATH and with FASTX, BioSequences available

# create .bashrc and .bash_profiles in each students directory
bash ./install-bashrc.sh