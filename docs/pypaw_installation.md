# Pypaw installation process against OpenMPI on Titan

### Install conda + start conda env

```
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh
export PATH=miniconda2/bin:$PATH
conda create -n pypaw
source activate pypwa
```

### Module loads

```
module load PE-intel/14.0.4
module load openmpi
module load hdf5-parallel/1.8.11_shared
module load mxml git vim szip
```

 Following instructions from [pypaw repo](https://github.com/wjlei1990/pypaw/blob/master/INSTALL.md)
 
 ### Install obspy, pyflex, pyadjoint, spaceweight, pytomo3d
 
```
conda install -c obspy obspy

git clone --branch devel https://github.com/wjlei1990/pyflex 
cd pyflex
pip install -v -e .
cd ..
```
```
git clone --branch dev https://github.com/chukren/pyadjoint 
cd pyadjoint
```

Had to edit line 74 from setup.py: ```"obspy>=1.0.0", "flake8==2.5.1", "pytest", "nose", "numpy", "scipy"``` to ```"obspy>=1.0.0", "flake8>=2.5.1", "pytest", "nose", "numpy", "scipy"```

```
pip install -v -e .
cd ..

git clone https://github.com/wjlei1990/spaceweight
cd spaceweight
pip install -v -e .
cd ..

git clone https://github.com/wjlei1990/pytomo3d
cd pytomo3d
pip install -v -e .
cd ..
```
 
### Install mpi4py
 
 ```
 env MPICC=mpicc pip install mpi4py==1.3.1
 ```

### Install h5py

```
git clone https://github.com/h5py/h5py
cd h5py
export CC=mpicc
python setup.py configure --mpi
python setup.py configure --hdf5=/sw/rhea/hdf5-parallel/1.8.11_shared/rehl6.6_intel14.0.4
python setup.py build
```

Had to comment line 62 from h5py/__init__.py

```
python setup.py install
```

### Install pyASDF

```
git clone https://github.com/wjlei1990/pyasdf
cd pyasdf
pip install -v -e .
cd ..
```

### Install pypaw

```
git clone https://github.com/wjlei1990/pypaw
cd pypaw
pip install -v -e .
cd ..
```


### Script to be run on Rhea

```
#!/bin/bash
# Begin PBS directives
#PBS -A BIP149
#PBS -N test
#PBS -j oe
#PBS -l walltime=00:30:00,nodes=1
#    End PBS directives and begin shell commands
export PATH=/lustre/atlas/scratch/vivekb/bip149/anaconda/bin:$PATH
source activate pypaw
#export PMI_NO_FORK=True

module load PE-intel/14.0.4
module load openmpi
module load mxml git vim szip
module load hdf5-parallel/1.8.11_shared

mpirun -np 16 pypaw-process_asdf -f /lustre/atlas/scratch/vivekb/bip149/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_17_40.path.json -p /lustre/atlas/scratch/vivekb/bip149/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.17_40.param.yml

```
