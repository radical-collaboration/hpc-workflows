# return a list with pixels for the next iteration
#
define_pixels_for_next_iteration <- function(
    num.times.to.compute, num.flts, pixels.compute,
    folder.raster.anen, iteration, folder.raster.obs,
    threshold.triangle) {
    require(raster)
    require(RAnEnExtra)

    file.triangles <- paste(folder.raster.iteration,
                            'triangulations.rdata', sep = '')
    if (file.exists(file.triangles)) {
        load(file.triangles)
    } else {
        stop("Triangulation file not found:",
             file.triangles)
    }

    errors.rast <- matrix(NA, nrow = num.times.to.compute, ncol = num.flts)
    errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                         length(polys.triangle)))

    folder.raster.iteration <- paste(folder.raster.anen, 'iteration',
                                     iteration, '/', sep = '')
    for (i in 1:num.times.to.compute) {
        for (j in 1:num.flts) {

            # read anen raster
            file.raster.anen <- paste(folder.raster.iteration, 'day', i,
                                      '_flt', j, '.rdata', sep = '')
            if (file.exists(file.raster.anen)) {
                load(file.raster.anen)
            } else {
                stop(paste("AnEn raster not found:",
                           file.raster.anen))
            }

            # read observations
            file.raster.obs <- paste(folder.raster.obs, 'day',
                                     i, '_flt', j, '.rdata', sep = '')
            if(file.exists(file.raster.obs)) {
                load(file.raster.obs)
            } else {
                stop(paste("Observation raster not found:",
                           file.raster.obs))
            }

            # compute raster error
            errors.rast[i, j] <- sd(values(rast.obs - rast.int))

            # compute triangulation error
            for (k in 1:length(polys.triangle)) {
                error.tmp <- 0
                control.points <- polys.triangle[k]@polygons[[1]]@Polygons[[1]]@coords
                control.points <- control.points[1:3,]
                for (m in 1:3) {
                    # raster is            (nrow, ncol)
                    # which corresponds to (y, x)
                    #
                    error.tmp <- error.tmp + abs(rast.obs[control.points[m,2],
                                                 control.points[m,1]] -
                                                     rast.int[control.points[m,2],
                                                              control.points[m,1]])
                }
                errors.triangle[i, j, k] <- mean(error.tmp, na.rm = T)
            }
        }
    }
    errors.rast.average <- mean(mean(errors.rast))
    errors.triangle.average <- apply(errors.triangle, 3, mean, na.rm = T)
    triangles.index.to.continue <- which(errors.triangle.average > threshold.triangle)

    # define pixels for the next iteration
    pixels.next.iteration <- vector(mode = 'numeric')
    for (i in triangles.index.to.continue) {
        triangle <- polys.triangle[i]
        pts.selected <- random.points.in.triangle(triangle, num.pixels.increase)
        pixels.next.iteration <- c(pixels.next.iteration,
                                   xy.to.pixels(pts.selected[, 1],
                                                pts.selected[, 2],
                                                xgrids.total, 0))
    }
    pixels.next.iteration <- remove.vector.duplicates(c(pixels.compute,
                                                        pixels.next.iteration))
    pixels.compute <- pixels.next.iteration[(length(pixels.compute)+1) :
                                            length(pixels.next.iteration)]
    return(pixels.compute)
}
