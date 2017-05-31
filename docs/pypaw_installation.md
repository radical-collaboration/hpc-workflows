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
 
```
conda install -c obspy obspy

git clone --branch devel https://github.com/wjlei1990/pyflex 
cd pyflex
pip install -v -e . (--user)
cd ..

git clone --branch dev https://github.com/chukren/pyadjoint 
cd pyadjoint
pip install -v -e . (--user)
cd ..

git clone https://github.com/wjlei1990/spaceweight
cd spaceweight
pip install -v -e . (--user)
cd ..

git clone https://github.com/wjlei1990/pytomo3d
cd pytomo3d
pip install -v -e . (--user)
cd ..
```
 
 
 ### Install mpi4py
 ```
 env MPICC= pip install mpi4py
 ```

### Install hdf5-parallel

```
wget http://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.10.1.tar
tar -xvf hdf5-1.10.1.tar 

CC=mpicc ./configure --enable-fortran --enable-parallel --prefix=<path to hdf5 dir> --enable-shared --enable-static
make
make install
```

### Install h5py

````
git clone https://github.com/h5py/h5py
cd h5py
export CC=mpicc
python setup.py configure --mpi
python setup.py configure --hdf5=<path to hdf5 dir>
python setup.py build
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
````


### Script to be run on Titan

```

```
