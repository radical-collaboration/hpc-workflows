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

## Caveats

1. Don't use symbollic link. While specifying input and output directories in `EnTK` pipelines, avoid using symbolic links and prefer to use absolute paths.
2. Avoid long strings in `Task.arguments`. There is a character limit for the length of the command line and its arguments. When the argument list proliferate, try to avoid passing them directly through the command line by writing arguments into a file to read.

