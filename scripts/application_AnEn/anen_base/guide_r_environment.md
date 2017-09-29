# R Environment Guide

This document guides you to set up the R environment for the ENTK AnEn use case on supercomputers.

The setup might be different depending on the platforms.

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
8. RAnEnExtra
9. spatstat

To install 1 ~ 7 packages, you can do the following in the R session:

```
install.packages("[name of the package]")
```

And then install `RAnEnExtra` which is from Github:

```
install_github("Weiming-Hu/RAnEnExtra")
```

At last, because the latest `spatstat` package requires the latest R version, we need to install the
older version of `spatstat`.

```
# we are install v 1.30
wget https://cran.r-project.org/src/contrib/Archive/spatstat/spatstat_1.30-0.tar.gz

R CMD INSTALL spatstat_1.30-0.tar.gz
```
