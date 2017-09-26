# evaluation file for ENTK and AnEn

#######################
# function definition #
#######################
nearest_neighbor_interpolation <- function( x,y,z, rast_base, lonlat=F, n=3 ) {
    # This function use the Nearest neighbour interpolation to project a set of
    # points in x,y,z format to a raster.  It returns the raster with the interpolated
    # values.  The value n is the number of closet points that will be used for the
    # interpolation.
    #
    # Source: http://rspatial.org/analysis/rst/4-interpolation.html
    #
    rast.res  <- rast_base

    # control points.  These are the points on the raster that we want to 
    # interpolate to.  Each of the control point will be assigned a value according to 
    # the nearest x,y point in the input
    #
    cp <- rasterToPoints( rast_base )

    # Distance matrix
    #
    d  <- pointDistance(cp[, 1:2], cbind(x,y), lonlat=lonlat)

    # Get the values of the closest n points
    #
    ngb <- t(apply(d, 1, function(x) order(x)[1:n]))

    pairs  <- cbind(rep(1:nrow(ngb), n), as.vector(ngb))
    values <- z[pairs[,2]]
    pn     <- tapply(values, pairs[,1], mean)

    values(rast.res)  <- as.vector(pn)

    return(rast.res)
}

compute.triangle.errors <- function(control.coords.x, control.coords.y,
                                    rast_obs, rast.pred) {
    # this function evaluate the prediction confidence for a triangle area
    # defined by the control points and Delaunay triangulation. The confidence
    # is measured by the absolute RMSE and the difference betweent the RMSE of
    # the control points of each triangle
    #
    df <- data.frame(x = control.coords.x, y = control.coords.y)

    # need a boundary window
    W <- ripras(df, shape="rectangle") 

    # create point pattern
    # compute Dirichlet triangles
    # convert to SpatialPolygons
    #
    polys <- as(delaunay(as.ppp(df, W=W)), "SpatialPolygons")

    # compute triangle errors
    mat.errors <- matrix(NA, nrows = length(polys), ncol = 2)
    colnames(mat.errors) <- c('RMSE', 'RMSE.diff')
    for (i in 1 : length(polys)) {

        # get coordinates of the control points
        control.coords <- polys[i]@polygons[[1]]@Polygons[[1]]@coords

        # get rid of the last row because it is the same with the first row
        control.coords <- control.coords[1 : (dim(control.coords)[1] - 1), ]

        # get values at the control points
        control.obs <- rast_obs[control.coords[, 1], control.coords[, 2]]
        control.pred <- rast.pred[control.coords[, 1], control.coords[, 2]]

        # compute errors
        mat.errors[i, 'RMSE'] = sqrt( mean( (control.obs - control.pred)^2, na.rm = T) )
        mat.errors[i, 'RMSE.diff'] = mean( abs( control.obs - control.pred), na.rm = T)
    }

    return(mat.errors)
}

evaluate <- function(file_observation, file_AnEn, stations_ID,
                     test_ID_start, test_ID_end, nflts, nrows, ncols,
                     threshold_RMSE = 2, num_neighbors = 3, pixels_growth = 10, verbose = F) {
    # this function will be called by the .py script to evaluate the AnEn results
    # of the current stage
    #
    # This function does the following steps for the current stage
    # - read observations (analysis in this case) as a raster
    # - read AnEn results from the current stage
    # - interpolate the results to a 100 * 100 raster
    # - compute errors for the current AnEn results
    # - determine the pixels to compute the next stage
    #
    print('Install and load libraries')
    #if (!require(sp)) {
    #install.packages('sp', repos='http://cran.us.r-project.org', destdir = '/home/vivek91/')
    #}
    #if (!require(ncdf4)) {
    #install.packages('ncdf4', repos='http://cran.us.r-project.org', destdir = '/home/vivek91/')
    #}
    #if (!require(raster)) {
    #install.packages('Rcpp', repos='http://cran.us.r-project.org', destdir = '/home/vivek91/')
    #install.packages('raster', repos='http://cran.mirrors.hoobly.com', destdir = '/home/vivek91/')
    #}

    library(sp)
    library(ncdf4)
    library(raster)

    print('Libraries loaded')

    rast_base <- raster(nrows = nrows, ncols = ncols, xmn = 0.5, xmx = ncols+.5, ymn = 0.5, ymx = nrows+.5)


    ##################
    # compute errors #
    ##################
    #
    # read observations
    print(paste('Read observations: ', file_observation, sep = ''))
    nc <- nc_open(file_observation)
    obs <- ncvar_get(nc, 'Data')
    nc_close(nc)

    # read AnEn results
    print(paste('Read AnEn results: ', file_AnEn, sep = ''))
    nc <- nc_open(file_AnEn)
    analogs <- ncvar_get(nc, 'Data')
    nc_close(nc)

    # compute the actual coordinates of computed pixels
    x <- (stations_ID %% ncols) + 1
    y <- ceiling(stations_ID / ncols) + 1

    # compute averaged values across all members
    num_computed_pixels <- dim(analogs)[1]
    analogs <- apply(analogs, c(1, 2, 3), mean, na.rm = T)

    # loop through days and flts to compute errors
    print('Compute errors')
    mat_RMSE <- matrix(NA, nrow = test_ID_end - test_ID_start + 1, ncol = nflts)
    rownames(mat_RMSE) <- paste(test_ID_start : test_ID_end)
    colnames(mat_RMSE) <- paste(1 : nflts)
    for (index in 1 : (test_ID_end - test_ID_start + 1)) {
        day = index + test_ID_start - 1
        print(paste('Processing day ', day, ' (', test_ID_start, '~', test_ID_end, ')', sep = ''))
        for (flt in 1 : nflts) {

            # get observations for the day and flt
            coords   <- expand.grid(1 : nrow(rast_base), 1 : ncol(rast_base))
            rast_obs <- rasterize(coords, rast_base, field = obs[, day, flt])

            # interpolate the AnEn prediction for the day and flt
            if (num_computed_pixels < nrows * ncols) {
                rast_int <- nearest_neighbor_interpolation(x, y, analogs[, index, flt], rast_base, n = num_neighbors)
            } else {
                rast_int = rasterize(cbind(x, y), rast_base, analogs[, index, flt])
            }

            # compute error
            mat_RMSE[as.character(day), as.character(flt)] <- sqrt( mean( values( (rast_obs - rast_int)^2), na.rm=T) )
        }
    }


    ###################
    # evaluate errors #
    ###################
    print('Evaluate errors')
    print(paste('threashold.RMSE is ', threshold_RMSE, sep = ''))
    if (mean(mat_RMSE) > threshold_RMSE) {
        # compute more pixels
        stations_ID <- sample.int(nrows * ncols, num_computed_pixels + pixels_growth)

        # make sure that the points at the four corners are included
        if (!(0 %in% stations_ID)) {
            stations_ID[1] <- 0
        }
        if (!(99 %in% stations_ID)) {
            stations_ID[2] <- 99
        }
        if (!(9900 %in% stations_ID)) {
            stations_ID[3] <- 9900
        }
        if (!(9999 %in% stations_ID)) {
            stations_ID[4] <- 9999
        }

        if (verbose) {
            print('Stations index to compute for the next stage:')
            print(stations_ID)
        }

        return(list(stations_ID = stations_ID))

    } else {
        # stop and return an empty list
        return(list())
    }
}
