# define_pixels has several steps:
# - define and save triangles
# - compute errors over the triangle vertices
# - define pixels for the next iteration
#
define_pixels <- function(
    iteration, folder.raster.obs, folder.accumulate, folder.triangles,
    pixels.computed, xgrids.total, ygrids.total, test.ID.start,
    num.flts, num.pixels.increase, num.times.to.compute, members.size,
    threshold.triangle) {

    require(raster)
    require(deldir)
    require(spatstat) 
    require(maptools)
    require(RAnEnExtra)

    # convert argument types
    iteration <- str_pad(as.numeric(iteration), 4, pad = '0')

    xgrids.total <- as.numeric(xgrids.total)
    ygrids.total <- as.numeric(ygrids.total)
    test.ID.start <- as.numeric(test.ID.start)
    num.flts <- as.numeric(num.flts)
    num.times.to.compute <- as.numeric(num.times.to.compute)
    num.pixels.increase <- as.numeric(num.pixels.increase)
    members.size <- as.numeric(members.size)
    threshold.triangle <- as.numeric(threshold.triangle)

    pixels.computed <- as.numeric(unlist(pixels.computed))
    

    #############################
    # define and save triangles #
    #############################
    # convert pixel indices to x and y coordinates
    x <- pixels.to.x.by.row(pixels.computed, xgrids.total, 0)
    y <- pixels.to.y.by.row(pixels.computed, xgrids.total, 0)

    # define triangles
    df <- data.frame(x, y)
    W <- ripras(df, shape = 'rectangle')
    polys.triangles <- as(delaunay(as.ppp(df, W = W)), "SpatialPolygons")

    # save triangles
    file.triangles <- paste(folder.triangles, 'iteration',
                            iteration, '.nc', sep = '')
    save(polys.triangles, file = file.triangles)
 

    #############################################
    # compute errors over the triangle vertices #
    #############################################
    errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                         length(polys.triangles)))
    for (i in 1:num.times.to.compute) {
        for (j in 1:num.flts) {

            # read anen accumulated NetCDF file
            file.anen <- paste(folder.accumulate, 'iteration',
                               iteration, '.nc', sep = '')
            if (file.exists(file.anen)) {
                nc <- nc_open(file.anen)
                data.anen <- ncvar_get(nc, 'Data',
                                       start = c(0, test_ID_start + i - 1, j - 1, 0),
                                       count = c(length(pixels.computed), 1, 1, members.size))
            } else {
                stop(paste("Can't find AnEn file", file.anen))
            }

            # compute the average across all ensemble members
            data.anen <- apply(data.anen, 1, mean, na.rm = T)

            # extract observation values from observation raster at the vertices
            file.raster.obs <- paste(folder.raster.obs, 'day', i,
                                     '_flt', j, '.rdata', sep = '')
            if (file.exists(file.raster.obs)) {
                rast.obs <- raster(file.raster.obs)
                data.obs <- rast.obs[(y-1) + x]
            } else {
                stop(paste("Can't find observation raster", file.raster.obs))
            }

            # compute errors for the vertices
            errors.vertex <- abs(data.obs - data.anen)

            for (k in 1:length(polys.triangles)) {
                control.points <- polys.triangles[k]@polygons[[1]]@Polygons[[1]]@coords
                control.points <- control.points[-1, ]
                control.points <- xy.to.pixels(control.points[, 1], control.points[, 2],
                                               xgrids.total = xgrids.total, start = 0)
                index <- unlist(lapply(control.points,
                                       function (x, l) {return(which(l == x))},
                                       l = pixels.computed))
                
                if (length(index) == length(control.points)) {
                    errors.triangle[i, j, k] <- mean(errors.vertex[index], na.rm = T)
                } else {
                    stop(paste("Some vertex not found in the computed list. ",
                               "The desired vertices are ", control.points, sep = ''))
                }
            }
        }
    }

    errors.triangle.average <- apply(errors.triangle, 3, mean, na.rm = T)


    #################
    # define pixels #
    #################
    # find out the triangles that have too large errors
    triangles.index.to.continue <- which(errors.triangle.average > threshold.triangle)

    # define pixels for the next iteration
    pixels.next.iteration <- vector(mode = 'numeric')
    for (in in triangles.index.to.continue) {
        triangle <- polys.triangles[i]
        pts.selected <- random.points.in.triangle(triangle, num.pixels.increase)
        pixels.next.iteration <- c(pixels.next.iteration,
                                   xy.to.pixels(pts.selected[, 1],
                                                pts.selected[, 2],
                                                xgrids.total, 0))
    }
    pixels.next.iteration <- remove.vector.duplicates(c(pixels.computed,
                                                        pixels.next.iteration))
    pixels.next.iteration <- pixels.next.iteration[length(pixels.computed)+1 :
                                                   length(pixels.next.iteration)]

    write(pixels.next.iteration , file = 'pixels_next_iteration.txt',
          ncolumns = length(pixels.next.iteration))
}
