# generate_observation_rasters complete the following steps
# - generate multiple folders for output
# - generate a rdata file to keep track of the pixels computed
# - generate observation rasters for each test day and flt
#
# This should be run on supercomputers because it generates 
# folders and files on supercomputers
#
generate_observation_rasters <- function(
    test.ID.index, test.ID.start,
    folder.prefix, folder.accumulate, 
    folder.raster.anen, folder.output,
    folder.raster.obs, folder.triangles,
    num.times.to.compute, num.flts,
    file.observations, xgrids.total,
    ygrids.total) {
    require(ncdf4)
    require(raster)

    # some setup work
    # create multiple folders
    #
    for(folder in c(folder.accumulate, folder.output, folder.triangles,
                    folder.raster.anen, folder.raster.obs)) {
        #if (!dir.exists(folder)) {
        # dir.exists function does not exist in older R

        dir.create(folder, recursive = T)
    }

    # convert variable types
    num.times.to.compute <- as.numeric(num.times.to.compute)
    num.flts <- as.numeric(num.flts)
    test.ID.start <- as.numeric(test.ID.start)
    xgrids.total <- as.numeric(xgrids.total)
    ygrids.total <- as.numeric(ygrids.total)

    rast.files <- list.files(folder.raster.obs)
    num.of.files <- length(rast.files)
    grids.total <- xgrids.total*ygrids.total
    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)
    if (num.of.files == num.times.to.compute*num.flts) {
        print(paste("Observation rasters already exist."))
    } else {
        for (j in 1:num.flts) {
            print(paste('Generating observation raster for day ',
                        test.ID.index, ' flt ', j, sep = ''))
            file.raster.obs <- paste(folder.raster.obs, 'day', 
                                     test.ID.index, '_flt', j,
                                     '.rdata', sep = '')
            if(file.exists(file.raster.obs)) {
                print('skip because it already exists')
            } else {
                nc <- nc_open(file.observations)
                obs <- ncvar_get(nc, 'Data',
                                 start = c(1, 1, test.ID.index+test.ID.start, j),
                                 count = c(1, grids.total, 1, 1))
                nc_close(nc)
                coords   <- expand.grid(1:ncol(rast.base),1:nrow(rast.base))
                rast.obs <- rasterize(coords, rast.base, field = obs)

                save(rast.obs, file = file.raster.obs)
            }
        }
    }
}

