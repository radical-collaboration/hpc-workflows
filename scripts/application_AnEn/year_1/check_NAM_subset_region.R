library(ncdf4)
library(raster)

if (Sys.info()['login'] == 'wuh20') {
  # files come from Exfat-Hu external harddrive
  obs.file.entire <-
    '/Volumes/ExFat-Hu/Data/NAM_processed/Analysis_NAM.nc'
  obs.file.subset <-
    '/Volumes/ExFat-Hu/Data/NAM_processed/small-set/analysis_small-set.nc'
} else {
  stop("This script needs Weiming's extarnal harddrive")
}

obs.nc.entire <- nc_open(obs.file.entire)
obs.nc.subset <- nc_open(obs.file.subset)

time <- 1
dt <- 1

obs.entire <- ncvar_get(
  obs.nc.entire,
  'Data',
  start = c(1, 1, time, dt),
  count = c(1, 262792, 1, 1)
)
obs.subset <- ncvar_get(
  obs.nc.subset,
  'Data',
  start = c(1, 1, time, dt),
  count = c(1, 20000, 1, 1)
)

nc_close(obs.nc.entire)
nc_close(obs.nc.subset)

dim(obs.entire)
dim(obs.subset)

mat.entire <- matrix(obs.entire, nrow = 428, byrow = T)
mat.subset <- matrix(obs.subset, nrow = 100, byrow = T)

stopifnot(identical(mat.entire[1:100, 1:200], mat.subset))

rast.entire <-
  raster(apply(mat.entire, 2, rev))
rast.subset <-
  raster(apply(mat.subset, 2, rev))

plot(rast.entire)
plot(rast.subset)
contour(rast.subset, add = T)
