##########
# set up #
##########
# set up basic parameters that would be shared by all processes
command.exe <- '~/github/CAnalogsV2/install/bin/canalogs'
command.verbose <- '--verbose 0'
file.forecasts <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/Forecasts_NAM_sliced.nc"
file.observations <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/analysis_NAM.nc"
folder.prefix <- '~/geolab_storage_V2/data/NAM12KM/experiments_smart/'
folder.accumulate <- paste(folder.prefix, 'anen_accumulate/', sep = '')
folder.output <- paste(folder.prefix, 'anen_output/', sep = '')
folder.raster.anen <- paste(folder.prefix, 'anen_raster/', sep = '')
folder.raster.obs <- paste(folder.prefix, 'obs_raster/', sep = '')
folder.tmp <- paste(folder.prefix, 'tmp/', sep = '')

file.pixels.computed <- paste(folder.prefix, 'pixels_computed_list.rdata', sep = '')
if(!file.exists(file.pixels.computed)) {
  pixels.computed.list <- list()
  save(pixels.computed.list, file = file.pixels.computed)
}

num.flts <- 4
num.times <- 822
num.times.to.compute <- 2
num.parameters <- 13
ygrids.total <- 428
xgrids.total <- 614
grids.total <- xgrids.total*ygrids.total
init.num.pixels.compute <- 100
yinterval <- 15
ycuts <- seq(from = 1, to = ygrids.total, by = yinterval)

quick <- F
cores <- 8
rolling <- 0
observation.ID <- 0
train.ID.start <- 0
train.ID.end <- 699
test.ID.start <- 700
test.ID.end <- test.ID.start + num.times.to.compute - 1
weights <- rep(1, num.parameters)
members.size <- 20

num.neighbors <- 2
iteration <- '0001'
threshold.triangle <- 2
num.pixels.increase <- 10

debug <- FALSE

rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                    xmn = 0.5, xmx = xgrids.total+.5,
                    ymn = 0.5, ymx = ygrids.total+.5)

for(folder in c(folder.accumulate, folder.output,
                folder.raster.anen, folder.raster.obs)) {
  if (!dir.exists(folder)) {
    dir.create(folder, recursive = T)
  }
}


