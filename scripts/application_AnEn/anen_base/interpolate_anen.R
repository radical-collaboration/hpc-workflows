# generate interpolated prediction map for
# a single day and flt
#
interpolate_anen <- function(
    day, flt, folder.raster.iteration,
    folder.accumulate, iteration, members.size
    num.pixels.compute, xgrids.total, ygrids.total,
    num.neighbors) {
    require(ncdf4)
    require(raster)
    require(RAnEnExtra)

    if(!dir.exists(folder.raster.iteration)) {
        stop(paste("folder does not exist: ",
                   folder.raster.iteration))
    }

    file.raster.anen <- paste(folder.raster.iteration,
                              'day', day, '_flt', flt,
                              '.rdata', sep = '')
    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)

    if (!file.exists(file.raster.anen)) {
      nc <- nc_open(paste(folder.accumulate, 'accumulate',
                          iteration, '.nc', sep = ''))
      analogs <- ncvar_get(nc, 'Data',
                           start = c(1, day, flt, 1),
                           count = c(num.pixels.compute,
                                     1, 1, members.size))
      nc_close(nc)
      z <- apply(analogs, 1, mean, rm.na=T)
      if (length(pixels.compute) == xgrids.total*ygrids.total) {
        rast.int <- rasterize(cbind(x, y), rast.base, z)
      } else {
        rast.int <- nni(x, y, z, rast.base, n=num.neighbors)
      }
      save(rast.int, file = file.raster.anen)
    }
}
