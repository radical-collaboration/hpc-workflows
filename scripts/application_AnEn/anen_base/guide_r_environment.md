# R Installation Guide

This document guides you to set up the R environment for the ENTK AnEn use case on supercomputers.

### Local

A good installation guide for installing R and other packages [How To Set Up R on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-r-on-ubuntu-14-04)

HDF5, NetCDF installation guide [install_netcdf4.sh](https://gist.github.com/perrette/cd815d03830b53e24c82)

### SuperMIC

First, load modules.

```
module purge
module load gcc
module loag r
```

The R packages you need to install before running the `master.py` are the following:

1. devtools
2. raster
3. ncdf4
4. maptools
5. deldir
6. RANN
7. splancs
8. prodlim
9. spatstat
10. RAnEnExtra
11. gstat (optional, for interpolation method #2)

To install 1 ~ 9 packages, you can do the following in the R session:

```
install.packages("[name of the package]")
```

And then install `RAnEnExtra` which is from Github:

```
install_github("Weiming-Hu/RAnEnExtra")
```

For the package `gstat`, if you fail at the first time, and you are receiving the error message
```
gstat not avaiable for R version (#.#)
```
Try another CRAN mirror. It might work.

At last, because the latest `spatstat` package requires the latest R version, we need to install the
older version of `spatstat`.

```
# we are install v 1.30
wget https://cran.r-project.org/src/contrib/Archive/spatstat/spatstat_1.30-0.tar.gz

R CMD INSTALL spatstat_1.30-0.tar.gz
```
