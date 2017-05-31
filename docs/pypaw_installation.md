# Pypaw installation process against OpenMPI on Titan

### Install conda + start conda env

```
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh
export PATH=miniconda2/bin:$PATH
conda create -n pypaw_env
source activate pypwa_env
```

### Module loads

```
module swap PrgEnv-pgi PrgEnv-gnu
module load cmake
module load boost
module load fftw
module load cudatoolkit
module use --append /lustre/atlas/world-shared/csc230/openmpi/modules
module load openmpi/2017_05_04_539f71d
module unload cray-mpich/7.5.2

module load gcc/4.9.3
module swap cray-libsci cray-libsci/13.2.0
```

 Following instructions from [pypaw repo](https://github.com/wjlei1990/pypaw/blob/master/INSTALL.md)
 
 ### Install obspy, pyflex, pyadjoint, spaceweight, pytomo3d
 
 ### Install mpi4py
 ```
 env MPICC=
 ```

### Install hdf5-parallel


### Install h5py

### Install pyASDF

### Install pypaw



### Script to be run on Titan

```

```
