# KAYA

This is a WIP!

## Table of Contents

- [Environment Variables](#environment-variables)
- [Setup SSH Keys](#setup-ssh-keys)
- [Copying files to Kaya](copying-files-to-kaya)
- [Running in Parallel](#running-in-parallel)
- [Julia](#julia)
- [Mounting IRDS](#mount-irds)
- [Install R kernel for jupyter](#install-r-kernel-for-jupyter)
- [Modules](#modules)
- [Conda](#conda)

### References:

- UWA HPC: https://docs.hpc.uwa.edu.au/
- HPC monitor: https://monitor.hpc.uwa.edu.au/
- Software Carpentry: https://software-carpentry.org/
  and https://swcarpentry.github.io/
- https://ondemand.hpc.uwa.edu.au/
- Ryan's Kaya setup: [github](https://github.com/cpflueger2016/Kaya-ListerLab-Tutorial)
- [SLURM Gist](https://gist.github.com/ctokheim/bf68b2c4b78e9851b469be3425470699)
- HPC @ CECI about slurm and clusters: [Tutorial](https://support.ceci-hpc.be/doc/_contents/QuickStart/SubmittingJobs/SlurmTutorial.html)
- Research Computing University of Colorado Boulder: https://curc.readthedocs.io/en/latest/index.html
- [tmux tutorial](https://medium.com/@hammad.ai/how-i-learned-tmux-became-a-workflow-ninja-7d33cc796793>)

## Questions

- Does sbatch take a copy of the script passed in?
- Does the slurm script run .bashrc or .bash_profile? (if we have a shebang of: `#!/usr/bin/bash --login`)

## Environment Variables

With `#SBATCH --export=None` set (from [ref](https://slurm.schedmd.com/sbatch.html#OPT_export_3)):

> However, Slurm will then implicitly attempt to load the user's environment
> on the node where the script is being executed, as if `--get-user-env` was specified

> The environment variables are retrieved by running something of
> this sort "`su --login <username> -c /usr/bin/env`" and parsing the output.

### SLURM Environment Variables

```bash

  SLURM_CLUSTER_NAME=(null)
  SLURM_CONF=/var/spool/slurmd/conf-cache/slurm.conf
  SLURM_CPUS_ON_NODE=4
  SLURM_GTIDS=0
  SLURM_JOB_ACCOUNT=training
  SLURM_JOB_CPUS_PER_NODE=4
  SLURM_JOB_END_TIME=1707981410
  SLURM_JOB_GID=11119
  SLURM_JOB_ID=415830
  SLURM_JOBID=415830
  SLURM_JOB_NAME=me
  SLURM_JOB_NODELIST=n046
  SLURM_JOB_NUM_NODES=1
  SLURM_JOB_PARTITION=test
  SLURM_JOB_QOS=normal
  SLURM_JOB_START_TIME=1707980510
  SLURM_JOB_UID=11119
  SLURM_JOB_USER=training54
  SLURM_LOCALID=0
  SLURM_MEM_PER_CPU=1000
  SLURM_NNODES=1
  SLURM_NODE_ALIASES=(null)
  SLURM_NODEID=0
  SLURM_NODELIST=n046
  SLURM_NPROCS=4
  SLURM_NTASKS=4
  SLURM_PRIO_PROCESS=0
  SLURM_PROCID=0 # [0,..., ntasks -1]
  SLURM_SCRIPT_CONTEXT=prolog_task
  SLURM_SUBMIT_DIR=/home/training/training54
  SLURM_SUBMIT_HOST=kaya1.hpc.uwa.edu.au
  SLURM_TASK_PID=939893
  SLURM_TASKS_PER_NODE=4
  SLURM_TOPOLOGY_ADDR=n046
  SLURM_TOPOLOGY_ADDR_PATTERN=node
  SLURM_WORKING_CLUSTER=(null):kaya-m:6817:9984:109
```

## Setup SSH Keys

Use a ssh key to login to kaya:

Add or create a file `~/.ssh/config` on your local machine and add

```
Host kaya
  Hostname kaya.hpc.uwa.edu.au
  User icastleden
  IdentityFile ~/.ssh/kaya
```

Now run:

```bash
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/kaya
  # This will ask for your *kaya* password
  ssh-copy-id -i ~/.ssh/kaya.pub kaya
  # should now be able to log straight in!
  ssh kaya
```

## Copying files to Kaya

`scp` files to kaya
`rsync` works too

```bash
rsync -av local/directory kaya:
```

## Running in parallel

See [Tutorial at CECI](https://support.ceci-hpc.be/doc/_contents/QuickStart/SubmittingJobs/SlurmTutorial.html#going-parallel)

```bash

  #!/bin/bash
  #
  #SBATCH --ntasks=8
  for file in /path/to/data/*
  do
    # note the backgrounding with '&'
    srun -N1 -n1 -c1 --exact ./myprog $file &
  done
  wait # wait for background jobs to finish
```

_OR_ with gnu parallel (which is on kaya)

```bash

  #!/bin/bash
  #SBATCH --ntasks=8

  parallel -P $SLURM_NTASKS srun -nodes=1 --cpus-per-task=1 -ntasks=1 --exact ./myprog ::: /path/to/data/*
  # *OR*
  find /path/to/data -print0 | xargs -0 -max-args=1 -P $SLURM_NTASKS srun -ntasks=1 --exclusive ./myprog
```

Note that `--exclusive` means don't share allocated nodes with other jobs [ref](https://slurm.schedmd.com/srun.html#OPT_exclusive).

## Julia

Julia is probably the simplest way to get running multiple cpus on kaya using `Distributed`.

### links:

- [Julia manual](https://docs.julialang.org/en/v1/manual/distributed-computing/)
- See [Running Parallel Julia Scripts using the Distributed Package](https://researchcomputing.princeton.edu/support/knowledge-base/julia#distributed)
- Princeton [julia](https://researchcomputing.princeton.edu/support/knowledge-base/julia)

Run with `srun --cpus-per-task=4 --partition=work julia jrun.jl`

```julia

  # file jrun.jl

  using Distributed
  println("version is: $(VERSION)")
  # launch worker processes
  num_cores = parse(Int, ENV["SLURM_CPUS_PER_TASK"])
  addprocs(num_cores)

  println("Number of cores: ", nprocs())
  println("Number of workers: ", nworkers())

  # each worker gets its id, process id and hostname
  # this is a waterfall....
  # for i in workers()
  #     id, pid, host = fetch(@spawnat i (myid(), getpid(), gethostname()))
  #     println(id, " " , pid, " ", host)
  # end
  @everywhere function myfunc(i)
      i + 2
  end

  n = @distributed (+) for i = 1:nworkers()
      println(myid(), " " , getpid(), " ", gethostname())
      myfunc(i)
  end
  println("done ", n)

  # remove the workers
  rmprocs(workers()...)
```

### Julia Repos

see: https://docs.julialang.org/en/v1/manual/environment-variables/

juliaup creates a repo in `~/.julia`. Maybe alter `JULIA_DEPOT_PATH="/group/julia/depot:$JULIA_DEPOT_PATH"`
so that packages get put in `/group/julia/depot`.

## Mount IRDS:

See: https://en.wikipedia.org/wiki/GIO_(software)

You need to run a tmux (`tmux` or `tmux attach`) session then run:

`dbus-run-session -- bash`

This creates a dbus session(?) and runs a bash shell. Now run the script below.
Exiting from the bash shell kills the IRDS mount. To keep the session just detach from
tmux (`Cntrl-B d`).

```bash

  #!/bin/bash
  # ~/mount_irds.sh
  IRDS="drive.irds.uwa.edu.au"
  DOMAIN="uniwa"
  # Harvey Millars
  SHARE="sci-ms-001"

  link=~/irds

  # with:
  # username=00033472
  # password=.....
  source ~/.cifs-credentials

  echo -e "${username}\n${DOMAIN}\n${password}\n" | /usr/bin/gio mount "smb://${IRDS}/${SHARE}" > /dev/null 2>&1

  if [ $? -eq 0 ]; then
      # ${SHARE,,} => lowercase
      MYIRDS="/run/user/$UID/gvfs/smb-share:server=${IRDS,,},share=${SHARE,,}"
      echo "linking to: ${link}"
      rm -f ${link} 2>/dev/null
      ln -s ${MYIRDS} ${link}
  else

      echo  "Something went wrong. Mount failed. Check the mount listing with 'gio mount -l'"
  fi
```

Notes:

- because `irds -> '/run/user/11238/gvfs/smb-share:server=drive.irds.uwa.edu.au,share=sms-b-003'`
  irds links to `/run/user/${UID}` and this is a "local"(?) tmp filesystem we can't
  see any files from kaya.

## Install R kernel for jupyter

```bash
  module load r/4.0.5
  module load Anaconda3
  R
  # > install.packages('IRkernel', repos = "https://cloud.r-project.org")
  # > IRkernel::installspec()
  jupyter lab
```

## Modules

### links:

- Module [Read The Docs](https://modules.readthedocs.io) ([module specific Tcl commands](https://modules.readthedocs.io/en/latest/modulefile.html))
- [Tool Command Language (Tcl) Home Page](https://www.tcl-lang.org/). See if you have tclsh already installed.
- Princeton tutorial [Creating Your Own Environment Modules](https://researchcomputing.princeton.edu/support/knowledge-base/custom-modules)
  and for [julia](https://researchcomputing.princeton.edu/support/knowledge-base/julia)

Module for julia. usage: `module load julia/1.10`.
This is a **tcl** script (https://www.tcl-lang.org/).
Create a file `/group/peb007/modules/julia/1.10` Then
add the line `module use --append /group/peb007/modules` to `~/.bash_profile`
to add it to `MODULEPATH`.

```tcl
  #%Module
  # file: /group/peb007/modules/julia/1.10

  # `module help julia`
  proc ModulesHelp {} {
      puts stderr "put julia 1.10 on PATH for [uname machine]."

  }

  # for module whatis
  module-whatis "Adds julia 1.10 to PATH
  and goes on"

  # julia -e 'print(Sys.BINDIR)'
  set group "/group/peb007"
  prepend-path PATH "${group}/.julia/juliaup/julia-1.10.1+0.x64.linux.gnu/bin"
```

## Conda

We prefer to use micromamba which is a drop-in replacement for
conda and also a simple executable (that is installed in `~/.local/bin/micromamba`)

```bash
  "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
```

You need to set `MAMBA_ROOT_PREFIX` to `/group/peb007/micromamba` which will
place all subsequent environments under `${MAMBA_ROOT_PREFIX}/envs`.

This can be done during the install when the installer asks `Prefix location? [~/micromamba]`

### Create a new environment

```bash
# create a new environment *with* a python
micromamba env create -n my_new_env python=3.12
ls -l $MAMBA_ROOT_PREFIX/envs/my_new_env
micromamba env list
micromamba activate my_new_env
python # should be version 3.12
micromamba deactivate
```

### Activating a conda environment from within slurm

A conda enviroment that work for you or your group is the best way to go.

First create an environment.

```bash

  # load "base" conda environment
  module load Anaconda3/2020.11
  # create an environment somewhere....
  conda create -p /group/peb007/envs/bioinfo -c conda-forge mamba
  # *OR* just a python version
  # conda create -p /group/training/training54/conda_environments/bioinfo python=3.12
  # avoid long names in shell prompt
  conda config --set env_prompt '({name}) '
  # see ~/.condarc

  # activate environment
  conda activate /group/training/training54/conda_environments/bioinfo
  # now add anything you need e.g.:
  conda install blast+
  python -m pip install dataclasses-json
```

**NOTE**: seems like the slurm script does _not_ source `.bashrc`, so we need to initialize
conda some other way.

Run programs dependent scripts from within slurm.

```bash
  #!/bin/bash
  #SBATCH --partition=test
  #SBATCH -n 1
  #SBATCH -o bioinfo_%j.out
  #SBATCH --export=NONE

  module load Anaconda3/2020.11

  echo "running on: $(hostname) : ${SLURM_TASK_PID} with conda=${CONDA_EXE}"

  # ensure that ``conda init`` has effectively been called
  # source $HOME/.bashrc
  source ${CONDA_PREFIX:-$(dirname ${CONDA_EXE})/..}/etc/profile.d/conda.sh

  micromamba activate py312
  echo "activated ${CONDA_PREFIX} with python version: $(python -V) @ $(which python)"
  # run your scripts..
  python mybioinfo.py
  conda deactivate
  echo "done."
```
