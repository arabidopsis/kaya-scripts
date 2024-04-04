# KAYA

.. note::

References:

- UWA HPC: https://docs.hpc.uwa.edu.au/
- HPC monitor: https://monitor.hpc.uwa.edu.au/
- Software Carpentry: https://software-carpentry.org/
  and https://swcarpentry.github.io/
- https://ondemand.hpc.uwa.edu.au/
- Ryan's Kaya setup: https://github.com/cpflueger2016/Kaya-ListerLab-Tutorial
- [SLURM Gist](https://gist.github.com/ctokheim/bf68b2c4b78e9851b469be3425470699)
- HPC @ CECI about slurm and clusters: [Tutorial](https://support.ceci-hpc.be/doc/_contents/QuickStart/SubmittingJobs/SlurmTutorial.html)
- Research Computing University of Colorado Boulder: https://curc.readthedocs.io/en/latest/index.html
- Custom Modules: https://researchcomputing.princeton.edu/support/knowledge-base/custom-modules
  and [julia](https://researchcomputing.princeton.edu/support/knowledge-base/julia>)
  and https://modules.readthedocs.io/en/latest/modulefile.html
- [tmux tutorial](https://medium.com/@hammad.ai/how-i-learned-tmux-became-a-workflow-ninja-7d33cc796793>)

## Questions

- Does sbatch take a copy of the script passed in?
- Does the slurm script run .bashrc or .bash_profile? (if we have a shebang of: `#!/usr/bin/bash --login`)
  (A test suggests that `.bashrc` is **not** sourced/run)

Slurm environment variables

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

Use sshkey to login to kaya

```bash

  # cat ~/.ssh/config
  # Host kaya
  #   Hostname kaya.hpc.uwa.edu.au
  #   User training54
  #   # IdentityFile ~/.ssh/kaya

  ssh-keygen -t rsa -b 4096 -f ~/.ssh/kaya
  # This will ask for password
  ssh-copy-id -i ~/.ssh/kaya.pub kaya
  # **uncomment IdentityFile in ~/.ssh/config**
  ssh kaya
```

Things to ask

`scp` files to kaya
`rsync` works too

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

  #!/usr/bin/bash
  #SBATCH --ntasks=8

  parallel -P $SLURM_NTASKS srun -N1 -c1 -n1 --exact ./myprog ::: /path/to/data/*
  # *OR*
  find /path/to/data -print0 | xargs -0 -n1 -P $SLURM_NTASKS srun -n1 --exclusive ./myprog
```

## Julia

Julia is probably the simplest way to get running multiple cpus on kaya using `Distributed`.

.. note::

- https://docs.julialang.org/en/v1/manual/distributed-computing/
- See [Running Parallel Julia Scripts using the Distributed Package](https://researchcomputing.princeton.edu/support/knowledge-base/julia#distributed)

Run with `srun --cpus-per-task=4 --partition=test julia jrun.jl`

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

## Julia Repos

see: https://docs.julialang.org/en/v1/manual/environment-variables/

juliaup creates a repo in ~/.julia. Maybe alter `JULIA_DEPOT_PATH="/home/group/julia/depot:$JULIA_DEPOT_PATH"`
so that packages get put in `/home/group/julia/depot`.

# Mount IRDS:

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

  module load r/4.0.5 Anaconda3
  module load Anaconda3
  R
  # > install.packages('IRkernel', repos = "https://cloud.r-project.org")
  # > IRkernel::installspec()
  jupyter lab
```

## Modules

.. note::

see:

- https://modules.readthedocs.io
- https://www.tcl-lang.org/

Module for julia. usage: `module load julia/1.10`.
This is a **tcl** script (https://www.tcl-lang.org/).
Create a file `~/Modules/modulefiles/julia/1.10` Then
add `module use --append /home/aturing/Modules/modulefiles` to `~/.bash_profile`
to add it to `MODULEPATH`.

```tcl

  #%Module
  # file ~/Modules/modulefiles/julia/1.10
  # from https://researchcomputing.princeton.edu/support/knowledge-base/custom-modules
  # and https://modules.readthedocs.io/en/latest/modulefile.html

  # add `module use --append ~/Modules/modulefiles` to ~/.bash_profile to
  # add path to MODULEPATH
  # get julia: `curl -fsSL https://install.julialang.org | sh`


  # `module help julia`
  proc ModulesHelp {} {
      puts stderr "put julia 1.10 on PATH for [uname machine]."

  }

  module-version 1.10 default

  # for module whatis
  module-whatis "Adds julia 1.10 to PATH
  and goes on"

  # julia -e 'print(Sys.BINDIR)'
  prepend-path PATH "/home/training/training54/.julia/juliaup/julia-1.10.1+0.x64.linux.gnu/bin"
  # *OR*
  prepend-path PATH "[julia -e 'print(Sys.BINDIR)']"
```

## Activating a conda environment from within slurm

A conda enviroment that work for you or your group is the best way to go.

First create an environment.

```bash

  # load "base" conda environment
  module load Anaconda3/2020.11
  # create an environment somewhere....
  conda create -p /group/training/training54/conda_environments/bioinfo -c conda-forge mamba
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

  conda activate /group/training/training54/conda_environments/bioinfo
  echo "activated ${CONDA_PREFIX} with python version: $(python -V) @ $(which python)"
  # run your scripts..
  python mybioinfo.py
  conda deactivate
  echo "done."
```
