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

## Developing Workflow

For details, please refer to 

- [the official examples](https://radicalentk.readthedocs.io/en/latest/examples.html)
- [the user guide](https://radicalentk.readthedocs.io/en/latest/user_guide.html)
