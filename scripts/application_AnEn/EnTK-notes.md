# My Guide to RADICAL EnTK

## Installation

The official guide for EnTK installation is [here](https://radicalentk.readthedocs.io/en/latest/install.html).

Below are the steps.

```
# Create an virtual environment using python version 3.X
virtualenv $HOME/venv -p python3

# Activate the python in the virtual environment
source $HOME/venv/source/bin/activate

# Install EnTK
pip install radical.entk

# Check installation
radical-stack
```

If you want to quit the current virtual environment, use the command `deactivate`.

## Workflow Development

For details, please refer to 

- [the official examples](https://radicalentk.readthedocs.io/en/latest/examples.html)
- [the user guide](https://radicalentk.readthedocs.io/en/latest/user_guide.html)

## Runtime

After pilots have been submitted, the job can be monitored on the supercomputer. In the following case, the job is queued.

```
$ squeue -u `whoami`
  JOBID   PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
5341930      normal pilot.00 tg839717 PD       0:00      1 (Priority)
```

When all pipelines have been submitted, you can go `$WORK` to find `radical.pilot.sandbox` folder. All logs files can be found over there.

## Caveats

1. Don't use symbolic link. While specifying input and output directories in `EnTK` pipelines, avoid using symbolic links and prefer to use absolute paths.
2. Avoid long strings in `Task.arguments`. There is a character limit for the length of the command line and its arguments. When the argument list proliferate, try to avoid passing them directly through the command line by writing arguments into a file to read.


## Questions

1. How many tasks are there in a stage? I tried to use `len(p.taksks)` but it only returns 1?
2. What's the proper use of the task attribute `link_input_data`?
