# Forward simulations with EnTK

## Requirements (local machine)

* python >= 2.7 (< 3.0)
* python-pip
* python-virtualenv
* git
* gsissh

## Installation

* The instructions in this document are relative to $HOME, feel free to pick your own data locations.

* You will first need to create a virtual environment. This is to avoid conflict between packages required for this example and local system packages. 

```bash
virtualenv $HOME/myenv
source $HOME/myenv/bin/activate
```

* You now need to install specific branches of [radical.pilot](https://github.com/radical-cybertools/radical.pilot) and [radical.ensemblemd](https://github.com/radical-cybertools/radical.ensemblemd). Some of the features required for this work are in the development branch and would be released soon. Even if you already have the branches please follow the instructions from scratch (or do a 'git pull' before installation).


Radical pilot installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
git checkout usecase/vivek
pip install .
```

Ensemble toolkit installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.ensemblemd.git
cd radical.ensemblemd
git checkout fix/kernel_args
pip install .
```

Other depenencies (pypaw, pyadjoint, etc.):

All the dependencies are installed on Stampede. The permissions have been set for public access. Let me know if you hit any access issues. No installation from the user is required for testing this example.


## Executing the example on Stampede 

* You need to have gsissh-access to Stampede. Please see notes here: ```https://github.com/vivek-bala/docs/blob/master/misc/gsissh_setup_stampede_ubuntu_xenial.sh``. These are notes to help in the procedure and not guaranteed to work as the specifics might be system dependent. Happy to help on this.

You can verify passwordless access by running ```gsissh -p 2222 <username>@stampede.tacc.xsede.org``` at the end which should **not** prompt you for a password. 

* Open ```runme.py``` in the same folder as the current file. Add your stampede username and password in **line 286** and execute the following command.


```bash
RADICAL_ENTK_VERBOSE=info python runme.py --resource xsede.stampede
```

Note: The input path and parameter files are located at ```/work/02734/vivek91/modules/simpy/examples/titan_global_inv``` on Stampede. The output is generated at ```/work/02734/vivek91/DATA_RADICAL``` on Stampede.

The standard output and error are present in the specific pilot folder in ```radical.pilot.sandbox``` under the WORK directory on Stampede. You can view them by doing the following:

```bash
cdw
cd radical.pilot.sandbox
cd `ls -Art | tail -n 1`
```

You will see multiple ```unit.*``` folders here that correspond to the various preprocessing tasks.