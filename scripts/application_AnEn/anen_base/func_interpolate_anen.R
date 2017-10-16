# File: func_interpolate_anen.R
# Author: Weiming Hu
# Created: Sep 2017
#
# generate interpolated prediction map for
# a single AnEn file
#
interpolate_anen <- function(
    file.anen, prefix.anen.raster, pixels.computed, times, flts,
    members.size, num.neighbors, xgrids.total, ygrids.total) {
    require(ncdf4)
    require(raster)
    require(RAnEnExtra)

    # convert argument types
    pixels.computed <- as.numeric(unlist(pixels.computed))
    times <- as.numeric(times)
    flts <- as.numeric(flts)
    members.size <- as.numeric(members.size)
    xgrids.total <- as.numeric(xgrids.total)
    ygrids.total <- as.numeric(ygrids.total)
    num.neighbors <- as.numeric(num.neighbors)

    num.pixels.computed <- length(pixels.computed)

    # check dimension
    if (!file.exists(file.anen)) {
        warning(paste("File not found", file.anen))
        return (TRUE)
    }

    nc <- nc_open(file.anen)
    if (length(nc$dim$Members$vals) != members.size) {
        stop(paste("Members dimension is not correct in file", file.anen))
        return (FALSE)
    }
    if (length(nc$dim$Stations$vals) != num.pixels.computed) {
        stop(paste("Stations dimension is not correct in file", file.anen))
        return (FALSE)
    }
    if (length(nc$dim$Time$vals) != times) {
        stop(paste("Time dimension is not correct in file", file.anen))
        return (FALSE)
    }
    if (length(nc$dim$dt$vals) != flts) {
        stop(paste("dt dimension is not correct in file", file.anen))
        return (FALSE)
    }

    nc_close(nc)

    # convert pixel indices to x and y coordinates
    x <- pixels.to.x.by.row(pixels.computed, xgrids.total, 0)
    y <- pixels.to.y.by.row(pixels.computed, xgrids.total, 0)

    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)

    for (time in 1 : times) {
        for (flt in 1 : flts) {
            file.raster.anen <- paste(prefix.anen.raster, '_time', time,
                                      "_flt", flt, '.rdata', sep = '')
            print(paste("Processing time #", time, " flt #", flt, ": ",
                        file.raster.anen, sep = ''))

            if (!file.exists(file.raster.anen)) {
                nc <- nc_open(file.anen)
                analogs <- ncvar_get(nc, 'Data',
                                     start = c(1, time, flt, 1),
                                     count = c(num.pixels.computed,
                                               1, 1, members.size))
                nc_close(nc)

                z <- apply(analogs, 1, mean, rm.na=T)
                if (length(pixels.computed) == xgrids.total*ygrids.total) {
                    rast.int <- rasterize(cbind(x, y), rast.base, z)
                } else {
                    rast.int <- nni(x, y, z, rast.base, n=num.neighbors)
                }
                save(rast.int, file = file.raster.anen)
            } else {
                print(paste("File already exists", file.raster.anen))
            }
        }
    }
}
