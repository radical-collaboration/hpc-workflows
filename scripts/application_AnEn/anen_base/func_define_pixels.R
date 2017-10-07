# define_pixels has several steps:
# - define and save triangles
# - compute errors over the triangle vertices
# - define pixels for the next iteration
#
define_pixels <- function(
    iteration, folder.raster.obs, folder.accumulate, folder.triangles,
    pixels.computed, xgrids.total, ygrids.total,
    num.flts, num.pixels.increase, num.times.to.compute, members.size,
    threshold.triangle, verbose) {

    require(raster)
    require(deldir)
    require(spatstat) 
    require(maptools)
    require(RAnEnExtra)
    require(stringr)
    require(ncdf4)

    # convert argument types
    iteration <- str_pad(as.numeric(iteration), 4, pad = '0')
    pixels.computed <- as.numeric(unlist(pixels.computed))

    xgrids.total <- as.numeric(xgrids.total)
    ygrids.total <- as.numeric(ygrids.total)
    num.flts <- as.numeric(num.flts)
    num.times.to.compute <- as.numeric(num.times.to.compute)
    num.pixels.increase <- as.numeric(num.pixels.increase)
    members.size <- as.numeric(members.size)
    threshold.triangle <- as.numeric(threshold.triangle)
    verbose <- as.numeric(verbose)


    #############################
    # define and save triangles #
    #############################
    print("Define and save triangles")

    # convert pixel indices to x and y coordinates
    x <- pixels.to.x.by.row(pixels.computed, xgrids.total, 0)
    y <- pixels.to.y.by.row(pixels.computed, xgrids.total, 0)

    # define triangles
    df <- data.frame(x, y)
    #W <- ripras(df, shape = 'rectangle')
    W <- owin(xrange = c(1, xgrids.total), yrange = c(1, ygrids.total))
    polys.triangles <- as(delaunay(as.ppp(df, W = W)), "SpatialPolygons")

    # save triangles
    file.triangles <- paste(folder.triangles, 'iteration',
                            iteration, '.nc', sep = '')
    save(polys.triangles, file = file.triangles)
 

    #############################################
    # compute errors over the triangle vertices #
    #############################################
    print("Compute errors over the triangle vertices")

    errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                         length(polys.triangles)))
    for (i in 1:num.times.to.compute) {
        for (j in 1:num.flts) {
            print(paste("Processing test day ", i, " flt ", j, sep = ''))

            # read anen accumulated NetCDF file
            file.anen <- paste(folder.accumulate, 'iteration',
                               iteration, '.nc', sep = '')
            if (file.exists(file.anen)) {
                nc <- nc_open(file.anen)
                data.anen <- ncvar_get(nc, 'Data',
                                       start = c(1, i, j, 1),
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
                load(file.raster.obs)
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
    print("Define pixels to compute for the next iteration")

    # find out the triangles that have too large errors
    triangles.index.to.continue <- which(errors.triangle.average > threshold.triangle)

    if (verbose > 0) {
        print(paste("******** Evaluation from Iteration ", iteration,
                    " ********", sep = ''))
        print(paste("The error threshold is ", threshold.triangle, sep = ''))
        print(paste("There are ", length(triangles.index.to.continue),
                    " triangles that need more pixels.", sep = ''))
        for (i in 1 : length(errors.triangle.average)) {
            print(paste("The averaged error of vertices #", i, " is ",
                        errors.triangle.average[i], sep = ''))
        }
        print(paste("***********************************************",
                    sep = ''))
    }

    # define pixels for the next iteration
    pixels.next.iteration <- vector(mode = 'numeric')
    for (i in triangles.index.to.continue) {
        triangle <- polys.triangles[i]
        pts.selected <- random.points.in.triangle(triangle, num.pixels.increase)
        pixels.next.iteration <- c(pixels.next.iteration,
                                   xy.to.pixels(pts.selected[, 1],
                                                pts.selected[, 2],
                                                xgrids.total, 0))
    }
    pixels.next.iteration <- remove.vector.duplicates(c(pixels.computed,
                                                        pixels.next.iteration))
    pixels.next.iteration <- pixels.next.iteration[(length(pixels.computed)+1) :
                                                   length(pixels.next.iteration)]

    print(paste("The amount of the pixels for the next iteration is",
                length(pixels.next.iteration)))

    write(pixels.next.iteration, file = 'pixels_next_iteration.txt',
          ncolumns = length(pixels.next.iteration))
    print("Done!")
}
