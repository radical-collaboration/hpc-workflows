# Forward simulations on Titan CPUs using RP

## Requirements (local machine)

* python >= 2.7 (< 3.0)
* python-pip
* python-virtualenv
* git
* gsissh

## Installation

* The instructions in this document are relative to $HOME on Titan, feel free to 
pick your own parent location.

* You will first need to create a virtual environment on Titan. This is to avoid 
conflict between packages required for this example and local system packages. 

Please run the following to do so:

```bash
module load python python_pip python_virtualenv
virtualenv $HOME/myenv
source $HOME/myenv/bin/activate
```

* Note that all package installations and script executions need to be done 
**on Titan**. In other words, the client will be the Titan login node in this 
case.
* You now need to install specific branches of radical.pilot, saga-python, 
radical.utils on Titan. Some of the features required for this work are in the 
development branch and would be released soon. Even if you already have the 
branches please follow the instructions from scratch (or do a 'git pull' before
 installation).


### Radical pilot installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
git checkout fix/titan_aprun
pip install .
```

### Saga-python installation:

```bash
cd $HOME
git clone https://github.com/radical-cybertools/saga-python.git
cd saga-python
git checkout devel
pip install . --upgrade
```

### Radical.utils installation

```bash
cd $HOME
git clone https://github.com/radical-cybertools/radical.utils.git
cd radical.utils
git checkout devel
pip install . --upgrade
```

## Executing the example on Titan


Clone the current repository on Titan and traverse to this folder.
You may have to change the value of the key 'project' in line 193 of config.json 
in the current folder.

Once done, run the following command to execute the script:

```bash
python runme.py ornl.titan_aprun
```

The data is generated at 
```/lustre/atlas/scratch/vivekb/bip149/specfem3d_globe_CPU``` on Titan.


The standard output and error are present in the specific pilot folder in 
```/lustre/atlas/scratch/<username>/<proj_name>/radical.pilot.sandbox``` on 
Titan. Please note the placeholders in the patht to be filled by the user.

You can view them by going into the above directory and doing the following:

```bash
cd `ls -Art | tail -n 1`
cd pilot.0000
```

You will now see two unit.* folders. unit.000000 contains the standard output
and error from the meshfem task and unit.00001 contains the standard output 
and error from the specfem task.

**Important**: Please cleanup the data at the end of the run (after looking into 
them) so that the next run does not fail. You can do that as follows:

```bash
cd /lustre/atlas/scratch/vivekb/bip149/specfem3d_globe_CPU
rm OUTPUT_FILES/ DATABASE_MPI/ -rf   # I will not have permissions to delete them.
```