# File: func_define_pixels.R
# Author: Weiming Hu
# Created: Sep 2017
#
# Define_pixels has several steps:
# - define and save triangles
# - compute errors over the triangle vertices
# - define pixels for the next iteration
#
define_pixels <- function(
    iteration, folder.raster.obs, prefix.anen.raster, folder.accumulate,
    folder.triangles, pixels.computed, xgrids.total, ygrids.total,
    num.flts, num.pixels.increase, num.times.to.compute, members.size,
    threshold.triangle, tournament.size, num.champions,
    num.error.pixels, num.triangles.from.tournament,
    evaluation.method, verbose) {

    require(raster)
    require(deldir)
    require(spatstat) 
    require(maptools)
    require(RAnEnExtra)
    require(stringr)
    require(ncdf4)
    require(prodlim)

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
    tournament.size <- as.numeric(tournament.size)
    num.champions <- as.numeric(num.champions)
    num.error.pixels <- as.numeric(num.error.pixels)
    num.triangles.from.tournament <- as.numeric(num.triangles.from.tournament)
    evaluation.method <- as.numeric(evaluation.method)
    verbose <- as.numeric(verbose)

    #############################
    # define and save triangles #
    #############################
    print("Define and save triangles")

    # convert pixel to x and y coordinates
    rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                        xmn = 0.5, xmx = xgrids.total+.5,
                        ymn = 0.5, ymx = ygrids.total+.5)
    rast.base.xy <- expand.grid(1:xgrids.total, 1:ygrids.total)
    colnames(rast.base.xy) <- c('x', 'y')
    x.computed <- rast.base.xy[(pixels.computed+1), 'x']
    y.computed <- rast.base.xy[(pixels.computed+1), 'y']
    pts.computed <- SpatialPoints(cbind(x.computed,y.computed))

    # define triangles
    df <- data.frame(x.computed, y.computed)
    W <- owin(xrange = c(1, xgrids.total), yrange = c(1, ygrids.total))
    polys.triangles <- as(delaunay(as.ppp(df, W = W)), "SpatialPolygons")

    # save triangles
    file.triangles <- paste(folder.triangles, 'iteration',
                            iteration, '.rdata', sep = '')
    save(polys.triangles, file = file.triangles)

    if (evaluation.method == 0) {
        print("skip the evaluation")
        return(NA)

    } else if  (evaluation.method == 1) {

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
                    nc_close(nc)
                } else {
                    stop(paste("Can't find AnEn file", file.anen))
                }
                
                # compute the average across all ensemble members
                data.anen <- apply(data.anen, 1, mean, na.rm = T)

                # extract observation values from observation raster at the vertices
                file.raster.obs <- paste(folder.raster.obs, 'time', i,
                                         '_flt', j, '.rdata', sep = '')
                if (file.exists(file.raster.obs)) {
                    load(file.raster.obs)
                    data.obs <- rast.obs[cellFromXY(rast.base, cbind(x.computed,
                                                                     y.computed))]
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
                    control.points.index <- unlist(lapply(control.points, function(i, v) {
                      return(which(v == i))}, v = pixels.computed))
                    errors.triangle[i, j, k] <- mean(errors.vertex[control.points.index], na.rm = T)
                }
            }
        }

        errors.triangle.average <- apply(errors.triangle, 3, mean, na.rm = T)
        triangles.index.to.continue <- which(errors.triangle.average > threshold.triangle)

    } else if (evaluation.method == 2){

        ##############################################
        # compute errors on the interpolated rasters #
        ##############################################
        print("Compute errors over the iterpolated area of the triangle")

        errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                             length(polys.triangles)))
        for (i in 1:num.times.to.compute) {
            for (j in 1:num.flts) {
                print(paste("Processing test day ", i, " flt ", j, sep = ''))

                # read AnEn raster
                file.raster.anen <- paste(prefix.anen.raster, '_time', time,
                                          "_flt", flt, '.rdata', sep = '')
                if (file.exists(file.raster.anen)) {
                    load(file.raster.anen)
                } else {
                    stop(paste("Can't find AnEn raster", file.raster.anen))
                }

                # read observation raster
                file.raster.obs <- paste(folder.raster.obs, 'time', i,
                                         '_flt', j, '.rdata', sep = '')
                if (file.exists(file.raster.obs)) {
                    load(file.raster.obs)
                } else {
                    stop(paste("Can't find observation raster", file.raster.obs))
                }

                # compute errors for each triangle area
                for (k in 1:length(polys.triangles)) {
                    pts.in.triangle <- get.points.in.triangle(polys.triangles[k])
                    pts.in.triangle <- cellFromXY(rast.base, pts.in.triangle)
                    errors.triangle[i, j, k] <- mean(rast.obs[pts.in.triangle] -
                                                     rast.int[pts.in.triangle],
                                                     na.rm = T)
                }
            }
        }

        errors.triangle.average <- apply(errors.triangle, 3, mean, na.rm = T)
        triangles.index.to.continue <- which(errors.triangle.average > threshold.triangle)

    } else if (evaluation.method == 3) {

        ##########################################################
        # compute errors and use the binary tournament selection #
        ##########################################################
        print("Tournament selection is chosen")
        
        points.next.iteration <- list()
        errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                             length(polys.triangles)))
        
        # define random pixels in each triangle
        print("Define random points in each triangle")
        values(rast.base) <- 1
        rnd.points.df <- list()
        triangles.without.inner.points <- vector('numeric')
        for (k in 1:length(polys.triangles)) {
          rast.mask <- mask(crop(rast.base, polys.triangles[k]), polys.triangles[k])
          rnd.point.df <- tryCatch(
            {sampleRandom(rast.mask, num.error.pixels, na.rm = T, sp = T)},
            error = function(e) {
              print(paste('Error:', e$message))
              print("Probabily this is the smallest possible triangle already")
              return(NA)})
          
          if (typeof(rnd.point.df) == 'logical') {
            triangles.without.inner.points <- c(triangles.without.inner.points, k)
          } else {
            rnd.points.df <- c(rnd.points.df, rnd.point.df)
          }
        }
        polys.triangles <- polys.triangles[-triangles.without.inner.points]
        
        print("Compute errors for each triangle")
        for (i in 1:num.times.to.compute) {
            for (j in 1:num.flts) {
                print(paste("Processing test day ", i, " flt", j, sep = ''))

                # read anen accumulated NetCDF file
                file.anen <- paste(folder.accumulate, 'iteration',
                                   iteration, '.nc', sep = '')
                if (file.exists(file.anen)) {
                    nc <- nc_open(file.anen)
                    data.anen <- ncvar_get(nc, 'Data',
                                           start = c(1, i, j, 1),
                                           count = c(length(pixels.computed), 1, 1, members.size))
                    nc_close(nc)
                } else {
                    stop(paste("Can't find AnEn file", file.anen))
                }
                
                # compute the average across all ensemble members
                data.anen <- apply(data.anen, 1, mean, na.rm = T)
                pts.df = SpatialPointsDataFrame(pts.computed,
                                                data = data.frame(data.anen))
                
                # read observation raster
                file.raster.obs <- paste(folder.raster.obs, 'time', i,
                                         '_flt', j, '.rdata', sep = '')
                if (file.exists(file.raster.obs)) {
                    load(file.raster.obs)
                } else {
                    stop(paste("Can't find observation raster", file.raster.obs))
                }
                
                for (k in 1:length(polys.triangles)) {
                  # get coordinates and values for vertices
                  v = !is.na( over(pts.df, polys.triangles[k]))
                  control.points <- coordinates(pts.df)[v, ]
                  control.points.value <- pts.df@data[v, ]
                  
                  # get true and estimated values for random points
                  rnd.point.df <- rnd.points.df[[k]]
                  rnd.point.estimate <- rep(mean(control.points.value,na.rm = T),
                                            num.error.pixels)
                  rnd.point.true <- extract(rast.obs, rnd.point.df)
                  
                  errors.triangle[i, j, k] <- mean(abs(rnd.point.true - rnd.point.estimate),
                                                   na.rm = T)
                }
            }
        }

        errors.triangle.average <- apply(errors.triangle, 3, mean, na.rm = T)
        triangles.index.to.continue <- tournament.selection(errors.triangle.average,
                                                            num.triangles.from.tournament)

    } else {
        stop(paste("Wrong evaluation method #", evaluation.method))
    }

    #################
    # define pixels #
    #################
    print("Define pixels to compute for the next iteration")

    # find out the triangles that have too large errors

    if (verbose > 0) {
        write(paste("******** Evaluation from Iteration ", iteration,
                    " ********", sep = ''), file = 'evaluation_log.txt')
        write(paste("The error threshold is ", threshold.triangle, sep = ''),
              file = 'evaluation_log.txt', append = T)
        write(paste("There are ", length(triangles.index.to.continue),
                    " triangles that need more pixels.", sep = ''),
              file = 'evaluation_log.txt', append = T)
        for (i in 1 : length(errors.triangle.average)) {
	    if (i %in% triangles.index.to.continue) {
                write(paste("The averaged error of triangle #", i, " is ",
                            errors.triangle.average[i], " [selected]", sep = ''),
                      file = 'evaluation_log.txt', append = T)
	    } else {
                write(paste("The averaged error of triangle #", i, " is ",
                            errors.triangle.average[i], sep = ''),
                      file = 'evaluation_log.txt', append = T)
	    }
        }
        write(paste("***********************************************", sep = ''),
              file = 'evaluation_log.txt', append = T)
    }

    # define pixels for the next iteration
    if (evaluation.method == 3) {
      # reuse the pixels for evaluating triangles
      coords.next.iteration <- rnd.points.df[triangles.index.to.continue]
      coords.next.iteration <- lapply(coords.next.iteration, coordinates)
      coords.next.iteration <- do.call(rbind, coords.next.iteration)
      pixels.next.iteration <- xy.to.pixels(coords.next.iteration[, 1],
                                            coords.next.iteration[, 2],
                                            xgrids.total, 0)
      
    } else {
      # generate random pixels in each triangle
      pixels.next.iteration <- vector(mode = 'numeric')
      for (i in triangles.index.to.continue) {
        triangle <- polys.triangles[i]
        pts.selected <- random.points.in.triangle(triangle, num.pixels.increase)
        if (length(pts.selected) > 0) {
          pixels.next.iteration <- c(pixels.next.iteration,
                                     xy.to.pixels(pts.selected[, 1],
                                                  pts.selected[, 2],
                                                  xgrids.total, 0))
        }
        if (NA %in% pixels.next.iteration) {
          stop(paste("NA generated in pixels.next.iteration for triangle", i))
        }
      } 
    }
    
    pixels.next.iteration <- remove.vector.duplicates(c(pixels.computed,
                                                        pixels.next.iteration))
    pixels.next.iteration <- pixels.next.iteration[(length(pixels.computed)+1) :
                                                   length(pixels.next.iteration)]

    print(paste("The amount of the pixels for the next iteration is",
                length(pixels.next.iteration)))

    if (NA %in% pixels.next.iteration) {
        stop("NA found in pixels.next.iteration after removing duplicates")
    }

    print("The pixels for the next iteration are:")
    print(pixels.next.iteration)

    write(pixels.next.iteration, file = 'pixels_next_iteration.txt',
          ncolumns = length(pixels.next.iteration))
    print("Done!")
    return(0)
}
