# File: func_interpolate_anen.R
# Author: Weiming Hu
# Created: Sep 2017
#
# generate interpolated prediction map for
# a single AnEn file
#
interpolate_anen <- function(
    file.anen, prefix.anen.raster, pixels.computed, times, flts,
    members.size, num.neighbors, xgrids.total, ygrids.total,
    interpolation.method) {
    require(ncdf4)
    require(raster)
    require(RAnEnExtra)

    if (interpolation.method == 2) {
        require(gstat)
    }

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

    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)
    rast.base.xy <- expand.grid(1:xgrids.total, 1:ygrids.total)
    colnames(rast.base.xy) <- c('x', 'y')
    x.computed <- rast.base.xy[(pixels.computed+1), 'x']
    y.computed <- rast.base.xy[(pixels.computed+1), 'y']

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

                if (interpolation.method == 1) {
                    # nearest neighbor interpolation
                    if (length(pixels.computed) == xgrids.total*ygrids.total) {
                        rast.int <- rasterize(cbind(x.computed, y.computed),
                                              rast.base, z)
                    } else {
                        rast.int <- nni(x.computed, y.computed, z, rast.base, n=num.neighbors)
                    }

                } else if (interpolation.method == 2) {
                    # inverse distance weighted interpolation
                    if (length(pixels.computed) == xgrids.total*ygrids.total) {
                        rast.int <- rasterize(cbind(x.computed, y.computed),
                                              rast.base, z)
                    } else {
                        data <- data.frame(x = x.computed, y = y.computed, values = z)
                        values(rast.base)[cellFromXY(rast.base, data[, c(1, 2)])] <- z
                        model.idw <- gstat(id = "values", formula = values~1, locations = ~x+y,
                                           data=data, nmax=7, set=list(idp = .5))
                        rast.int <- interpolate(rast.base, model.idw)
                    }
                } else {
                    stop(paste("Wrong interpolation method #", interpolation.method))
                }

                save(rast.int, file = file.raster.anen)
            } else {
                print(paste("File already exists", file.raster.anen))
            }
        }
    }
}


