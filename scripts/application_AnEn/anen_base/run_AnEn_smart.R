# run the AnEn prediction with Delaunay Triangulation and
# error estimation in a recursive style
#
library(RAnEn)
library(RAnEnExtra)
library(raster)
library(deldir)
library(ncdf4)
library(spatstat) 
library(maptools)
library(stringr)


##########
# set up #
##########
# set up basic parameters that would be shared by all processes
command.exe <- '~/github/CAnalogsV2/install/bin/canalogs'
command.verbose <- '--verbose 0'
file.forecasts <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/Forecasts_NAM_sliced.nc"
file.observations <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/analysis_NAM.nc"
folder.prefix <- '~/geolab_storage_V2/data/NAM12KM/experiments_smart/'
folder.accumulate <- paste(folder.prefix, 'anen_accumulate/', sep = '')
folder.output <- paste(folder.prefix, 'anen_output/', sep = '')
folder.raster.anen <- paste(folder.prefix, 'anen_raster/', sep = '')
folder.raster.obs <- paste(folder.prefix, 'obs_raster/', sep = '')
folder.tmp <- paste(folder.prefix, 'tmp/', sep = '')

file.pixels.computed <- paste(folder.prefix, 'pixels_computed_list.rdata', sep = '')
if(!file.exists(file.pixels.computed)) {
  pixels.computed.list <- list()
  save(pixels.computed.list, file = file.pixels.computed)
}

num.flts <- 4
num.times <- 822
num.times.to.compute <- 2
num.parameters <- 13
ygrids.total <- 428
xgrids.total <- 614
grids.total <- xgrids.total*ygrids.total
init.num.pixels.compute <- 100
yinterval <- 15
ycuts <- seq(from = 1, to = ygrids.total, by = yinterval)

quick <- F
cores <- 8
rolling <- 0
observation.ID <- 0
train.ID.start <- 0
train.ID.end <- 699
test.ID.start <- 700
test.ID.end <- test.ID.start + num.times.to.compute - 1
weights <- rep(1, num.parameters)
members.size <- 20

num.neighbors <- 2
iteration <- '0001'
threshold.triangle <- 2
num.pixels.increase <- 10

debug <- FALSE

rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
                    xmn = 0.5, xmx = xgrids.total+.5,
                    ymn = 0.5, ymx = ygrids.total+.5)

for(folder in c(folder.accumulate, folder.output,
                folder.raster.anen, folder.raster.obs)) {
  if (!dir.exists(folder)) {
    dir.create(folder, recursive = T)
  }
}

# generate intial random pixels to compute
pixels.compute <- sample.int(grids.total,
                                init.num.pixels.compute)
pixels.compute <- include.corners(pixels.compute,
                                     xgrids.total,
                                     ygrids.total, 0)

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
rast.files <- list.files(folder.raster.obs)
num.of.files <- length(rast.files)
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
rm(num.of.files, rast.files)


#############
# main loop #
#############
while (length(pixels.compute) != 0) {
  
  #################
  # compute stage #
  #################
  # assign random pixels to sub-regions
  pixels.cut <- cut.pixels.along.y(pixels.compute, ycuts,
                                   xgrids.total, ygrids.total, 0)
  output.cut.files <- c()
  
  # create tmp folder for the AnEn files for subregions
  if(!dir.exists(folder.tmp)) {
    dir.create(folder.tmp, recursive = T)
  }
  
  # compute AnEn for sub-regions
  for(i in 1:length(pixels.cut)) {
    if (length(pixels.cut[[i]]) == 0) {
      print(paste('no pixels lie within subregion #', i, sep = ''))
      next
    }
    print(paste('computing the AnEn for subregion #', i,
                ' out of ', length(pixels.cut), sep = ''))
    
    output.file <- paste(folder.tmp, 'analogs_cut_', i, '.nc', sep = '')
    output.cut.files <- c(output.cut.files, output.file)
    
    command.netcdf <- '-N'
    command.forecasts <- paste('--forecast-nc', file.forecasts)
    command.observations <- paste('--observation-nc', file.observations)
    command.test <- paste('--test-ID-start', test.ID.start,
                          '--test-ID-end', test.ID.end)
    command.train <- paste('--train-ID-start', train.ID.start,
                           '--train-ID-end', train.ID.end)
    command.observation.ID <- paste('--observation-ID', observation.ID)
    command.members <- paste('--members-size', members.size)
    command.weights <- paste('--weights', paste(weights, collapse = ' '))
    command.rolling <- paste('--rolling', rolling)
    command.quick <- paste('--quick', as.numeric(quick))
    command.cores <- paste('--cores', cores)
    command.output <- paste('-p -o', output.file)
    
    # the relative index is needed
    subregion.start.station <- (ycuts[i]-ycuts[1])*xgrids.total
    command.stations <- paste('--stations-ID',
                              paste(pixels.cut[[i]] - subregion.start.station,
                                    collapse = ' '))
    start.forecasts <- c(0, subregion.start.station, 0, 0)
    start.observations <- c(0, subregion.start.station, 0, 0)
    if (i == length(ycuts)) {
      count.forecasts <- c(num.parameters,
                           grids.total-subregion.start.station,
                           num.times, num.flts)
      count.observations <- c(1,
                              grids.total-subregion.start.station,
                              num.times, num.flts)
    } else {
      count.forecasts <- c(num.parameters,
                           yinterval*xgrids.total,
                           num.times, num.flts)
      count.observations <- c(1,
                              yinterval*xgrids.total,
                              num.times, num.flts)
    }
    command.start.forecasts <- paste('--start-forecasts',
                                     paste(start.forecasts, collapse = ' '))
    command.count.forecasts <- paste('--count-forecasts',
                                     paste(count.forecasts, collapse = ' '))
    command.start.observations <- paste('--start-observations',
                                        paste(start.observations, collapse = ' '))
    command.count.observations <- paste('--count-observations',
                                        paste(count.observations, collapse = ' '))
    command.final <- paste(command.exe, command.netcdf, command.forecasts,
                           command.observations, command.stations, command.test,
                           command.train, command.observation.ID, command.members,
                           command.weights, command.rolling, command.quick,
                           command.cores, command.output, command.verbose,
                           command.start.forecasts, command.count.forecasts,
                           command.start.observations, command.count.observations)
    if (debug) {
      print(command.final)
    } else {
      system(command.final)
    }
  }
  
  # combine subregion output
  command.combine <- '-C'
  command.from <- paste('--files-from', paste(output.cut.files, collapse = ' '))
  command.new <- paste('--file-new ', folder.output,
                       'iteration', iteration, '.nc', sep = '')
  command.final <- paste(command.exe, command.combine, command.new, command.from)
  if (debug) {
    print(command.final)
  } else {
    system(command.final)
  }
  
  # save computed pixels
  load(file.pixels.computed)
  pixels.computed.list <- c(pixels.computed.list,
                            list(unlist(pixels.cut)))
  save(pixels.computed.list, file = file.pixels.computed)
  rm(pixels.computed.list)
  
  # delete folder tmp
  unlink(folder.tmp, recursive = T)
  
  # accumulate AnEn from previous iterations
  files.accumulate <- list.files(folder.output, full.names = T)
  command.from <- paste('--files-from', paste(files.accumulate, collapse = ' '))
  command.new <- paste('--file-new ', folder.accumulate,
                       'accumulate', iteration, '.nc', sep = '')
  command.final <- paste(command.exe, command.combine, command.new, command.from)
  if (debug) {
    print(command.final)
  } else {
    system(command.final)
  }
  
  # accumulate the pixels as well
  pixels.compute <- c()
  load(file.pixels.computed)
  pixels.compute <- unlist(pixels.computed.list[1:as.numeric(iteration)])
  rm(pixels.computed.list)
  
  
  ##################
  # evaluate stage #
  ##################
  folder.raster.iteration <- paste(folder.raster.anen, 'iteration',
                                   iteration, '/', sep = '')
  if (dir.exists(folder.raster.iteration)) {
    unlink(folder.raster.iteration, recursive = T)
  }
  dir.create(folder.raster.iteration, recursive = T)
  
  # convert and prepare pixel coordinates
  x <- pixels.to.x.by.row(pixels.compute, xgrids.total, 0)
  y <- pixels.to.y.by.row(pixels.compute, xgrids.total, 0)
  
  # define triangles
  df <- data.frame(x, y)
  W <- ripras(df, shape="rectangle")
  polys.triangle <- as(delaunay(as.ppp(df, W=W)), "SpatialPolygons")
  save(polys.triangle, file = paste(folder.raster.iteration,
                                    'triangulations.rdata', sep = ''))
  
  # compute error matrix
  errors.rast <- matrix(NA, nrow = num.times.to.compute, ncol = num.flts)
  errors.triangle <- array(NA, dim = c(num.times.to.compute, num.flts,
                                       length(polys.triangle)))
  for (i in 1:num.times.to.compute) {
    for (j in 1:num.flts) {
      
      # read the AnEn
      print(paste("For time #", i, ' at flt #', j,
                  ' interpolating predictions', sep = ''))
      file.raster.anen <- paste(folder.raster.iteration, 'day', i,
                                '_flt', j, '.rdata', sep = '')
      if (file.exists(file.raster.anen)) {
        load(file.raster.anen)
      } else {
        nc <- nc_open(paste(folder.accumulate, 'accumulate',
                            iteration, '.nc', sep = ''))
        analogs <- ncvar_get(nc, 'Data', start = c(1, i, j, 1),
                             count = c(length(pixels.compute),
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
      
      # read observations
      load(paste(folder.raster.obs, 'day', i, '_flt', j,
                 '.rdata', sep = ''))
      
      # compute raster error
      print(paste("For time #", i, ' at flt #', j,
                  ' computing errors.rast', sep = ''))
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
  triangles.index.to.continue <- which(
    errors.triangle.average > threshold.triangle)
  
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
  pixels.next.iteration <- remove.vector.duplicates(
    c(pixels.compute, pixels.next.iteration))
  pixels.compute <- pixels.next.iteration[(length(pixels.compute)+1) :
                                            length(pixels.next.iteration)]
  iteration <- str_pad(as.numeric(iteration)+1, 4, pad = '0')
  
  if (iteration == '0010') {
    break
  }
}
