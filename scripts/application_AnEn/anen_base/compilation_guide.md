# compile on Comet

```
# set up environment
module purge
module load cmake/3.8.2
module load gnu/4.9.2
module load netcdf/4.3.2
module list

# compile
git clone https://github.com/Weiming-Hu/CAnalogsV2.git
cd CAnalogs
mkdir build
cd build
CC=gcc CXX=g++ cmake -DNETCDF_LIBRARIES=$NETCDFHOME/lib/libnetcdf.so -DNETCDF_INCLUDE_DIR=$NETCDFHOME/include/ ..
make -j 16

# test
./canalogs
```

# compile on Stampede

*This is tested on Stampede 2.*

```
# set up environment
module purge
module load gcc/7.1.0
module load netcdf/4.3.3.1
module list

# compile
# I failed with HTTPS
# so I'm using SSH here
#
git clone git@github.com:Weiming-Hu/CAnalogsV2.git
cd CAnalogs
mkdir build
cd build
CC=gcc CXX=g++ cmake -DNETCDF_INCLUDE_DIR=$TACC_NETCDF_INC -DNETCDF_LIBRARIES=$TACC_NETCDF_LIB/libnetcdf.so ..
make -j 16

# test
./canalogs
```


# compile on SuperMic

```
# set up environment
module purge
module load gcc/4.9.0
module load netcdf/4.2.1.1/INTEL-140-MVAPICH2-2.0
module load cmake/2.8.12/INTEL-14.0.2
module list

# compile
# same problem here
# using SSH
#
git clone git@github.com:Weiming-Hu/CAnalogsV2.git
cd CAnalogs
mkdir build
cd build
CC=gcc CXX=g++ cmake -DNETCDF_INCLUDE_DIR=/usr/local/packages/netcdf/4.2.1.1/INTEL-140-MVAPICH2-2.0/include/ -DNETCDF_LIBRARIES=/usr/local/packages/netcdf/4.2.1.1/INTEL-140-MVAPICH2-2.0/lib/libnetcdf.so ..
make -j 16

# test
./canalogs
```
