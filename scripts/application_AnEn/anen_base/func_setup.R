# File: func_setup.R
# Author: Weiming Hu
#         Vivek Balasubramanian
# Created: Sep 2017
#
# This script sets up the basic parameters for running EnTK and AnEn
initial_config <- function (user = 'Weiming', debug = 0) {
    require(RAnEnExtra)

    prefix_time <- format(Sys.time(), "%Y-%m-%d-%H-%M-%S")


    ################################
    # parameters specific to users #
    ################################
    if (user == 'Weiming') {
        docker.port <- 32773
        command.exe <- '/home/whu/github/CAnalogsV2/install/bin/canalogs'
        file.forecasts <- "/home/whu/data/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "/home/whu/data/chunk_NAM/Analysis_NAM.nc"
        folder.scripts <- '/home/whu/github/hpc-workflows/scripts/application_AnEn/anen_base/'
        folder.prefix <- paste('/home/whu/experiments/anen_smart/',        
                               prefix_time, '/', sep = '')
        
    } else if (user == 'Vivek') {
        docker.port <- 32773
        command.exe <- '/work/vivek91/modules/CAnalogsV2/build/canalogs'
        file.forecasts <- "/work/vivek91/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "/work/vivek91/chunk_NAM/Analysis_NAM.nc"
        folder.scripts <- '/home/vivek91/repos/hpc-workflows/scripts/application_AnEn/anen_base/'
        folder.prefix <- paste('/work/vivek91/anen_smart/',
                               prefix_time, '/', sep = '')
    }


    #####################
    # folders and files #
    #####################
    if (debug) {
      folder.local <- paste('./debug_local_', prefix_time, '/', sep = '')
    } else {
      folder.local <- paste('./local_', prefix_time, '/', sep = '')
    }
    
    file.pixels.computed <- paste(folder.local, 'pixels_computed_list.rdata', sep = '')
    folder.accumulate <- paste(folder.prefix, 'anen_accumulate/', sep = '')
    folder.output <- paste(folder.prefix, 'anen_output/', sep = '')
    folder.raster.anen <- paste(folder.prefix, 'anen_raster/', sep = '')
    folder.raster.obs <- paste(folder.prefix, 'obs_raster/', sep = '')
    folder.triangles <- paste(folder.prefix, 'triangles/', sep = '')
    dir.create(folder.local, recursive = T)


    ###################
    # AnEn parameters #
    ###################
    # AnEn data information
    num.flts <- 4
    num.times <- 822
    num.times.to.compute <- 2
    num.parameters <- 13

    # domain information
    ygrids.total <- 428
    xgrids.total <- 614
    grids.total <- xgrids.total*ygrids.total

    # how many random points to start with
    init.num.pixels.compute <- 100

    # how many extra points should be selected on edges
    num.edge.points <- 5

    # parameters for defining the subregions
    yinterval <- 15
    ycuts <- seq(from = 1, to = ygrids.total, by = yinterval)

    # AnEn computation parameters
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


    ##############################
    # adaptive analog parameters #
    ##############################
    verbose <- 2
    init.iteration <- 1
    max.iterations <- 7

    # number of neighbors to find for final interpolation
    num.neighbors <- 2

    # error threshold for evaluating triangles
    threshold.triangle <- 3

    # number of random pixels to select in each triangle
    num.pixels.increase <- 1

    # whether to generate interpolation map from AnEn results
    interpolate.AnEn.rasters <- 1

    # whether to download the interpolation map
    # TODO: it does not actually download the maps for now
    #
    download.AnEn.rasters <- 0

    # choose one evaluation method from the below
    # 0 ---- skip evaluation (useful for cases with predefined pixels)
    # 1 ---- evaluate on the vertices
    # 2 ---- evaluate on the interpolated maps
    # 3 ---- evaluate using tournament
    #
    evaluation.method <- 3

    # parameters for evaluation method #3
    # number of individuals in each tournament
    tournament.size <- 5

    # number of champions from each tournament
    num.champions <- 1

    # number of pixels to select while evaluating the
    # fittness for each triangle
    #
    num.error.pixels <- 2

    # sample size for tournament selection
    num.triangles.from.tournament <- 200

    # predefine the number of pixels to compute for each iteration
    # this is only for convenient use for experiments
    #
    predefine.num.pixels <- 0
    #num.pixels.iteration <- c(100, 63, 153, 398, 923, 1973, 3552, 5356)
    #num.pixels.iteration <- c(100, 100, 100, 98, 96, 97, 88, 88)
    #num.pixels.iteration <- c(100, 169, 387, 373, 358)
    num.pixels.iteration <- c(100, 400, 400, 400, 400, 400, 400, 400, 400, 400)
    if (predefine.num.pixels == 1) {
        max.iterations = length(num.pixels.iteration)
    }


    # randomly select pixels to compute
    pixels.compute <- sample(0:(grids.total-1), 
                             init.num.pixels.compute)
    pixels.compute <- include.corners(pixels.compute,
                                      xgrids.total,
                                      ygrids.total, 0)
    pixels.compute <- include.boundaries(pixels.compute,
                                         num.edge.points,
                                         xgrids.total,
                                         ygrids.total, 0)

    list.init.config <- list(command.exe = command.exe,
                             verbose = verbose,
                             file.forecasts = file.forecasts,
                             file.observations = file.observations,
                             file.pixels.computed = file.pixels.computed,
                             folder.prefix = folder.prefix,
                             folder.scripts = folder.scripts,
                             folder.local = folder.local,
                             folder.accumulate = folder.accumulate,
                             folder.output = folder.output,
                             folder.raster.anen = folder.raster.anen,
                             folder.raster.obs = folder.raster.obs,
                             folder.triangles = folder.triangles,
                             num.flts = num.flts,
                             num.times = num.times,
                             num.times.to.compute = num.times.to.compute,
                             num.parameters = num.parameters,
                             ygrids.total = ygrids.total,
                             xgrids.total = xgrids.total,
                             grids.total = grids.total,
                             init.num.pixels.compute = init.num.pixels.compute,
                             pixels.compute = pixels.compute,
                             yinterval = yinterval,
                             ycuts = ycuts,
                             quick = quick,
                             cores = cores,
                             rolling = rolling,
                             observation.ID = observation.ID,
                             train.ID.start = train.ID.start,
                             train.ID.end = train.ID.end,
                             test.ID.start = test.ID.start,
                             test.ID.end = test.ID.end,
                             weights = weights,
                             members.size = members.size,
                             num.neighbors = num.neighbors,
                             init.iteration = init.iteration,
                             max.iterations = max.iterations,
                             threshold.triangle = threshold.triangle,
                             predefine.num.pixels = predefine.num.pixels,
                             num.pixels.iteration = num.pixels.iteration,
                             num.pixels.increase = num.pixels.increase,
                             interpolate.AnEn.rasters = interpolate.AnEn.rasters,
                             download.AnEn.rasters = download.AnEn.rasters,
                             evaluation.method = evaluation.method,
                             tournament.size = tournament.size,
                             num.champions = num.champions,
                             num.error.pixels = num.error.pixels,
                             num.triangles.from.tournament = num.triangles.from.tournament,
                             docker.port = docker.port,
                             debug = debug)

    return(list.init.config)
}
