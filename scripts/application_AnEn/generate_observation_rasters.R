###############################
# prepare observation rasters #
###############################
# this can be viewed as a preprocessing stage
#
# this stage reads data from the observations file and
# convert the data for each test day and flt to a raster
#
# this stage will save time from file I/O during
# the evaluation stage
#
generate_observation_rasters <- function(
    folder.raster.obs, num.times.to.compute,
    num.flts, file.observations, test.ID.start,
    xgrids.total, ygrids.total) {
    require(ncdf4)

    rast.files <- list.files(folder.raster.obs)
    num.of.files <- length(rast.files)
    grids.total <- xgrids.total*ygrids.total
    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)
    if (num.of.files == num.times.to.compute*num.flts) {
        print(paste("Observation rasters already exist."))
    } else {
        for (i in 1:num.times.to.compute) {
            for (j in 1:num.flts) {
                print(paste('Generating observation raster for day ', i,
                            ' flt ', j, sep = ''))
                file.raster.obs <- paste(folder.raster.obs, 'day', i,
                                         '_flt', j, '.rdata', sep = '')
                if(file.exists(file.raster.obs)) {
                    print('skip because it already exists')
                } else {
                    nc <- nc_open(file.observations)
                    obs <- ncvar_get(nc, 'Data', start = c(1, 1, i+test.ID.start, j),
                                     count = c(1, grids.total, 1, 1))
                    nc_close(nc)
                    coords   <- expand.grid(1:ncol(rast.base),1:nrow(rast.base))
                    rast.obs <- rasterize(coords, rast.base, field = obs)

                    save(rast.obs, file = file.raster.obs)
                }
            }
        }
    }
}

