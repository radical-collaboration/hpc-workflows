# set up basic parameters that would be shared by all processes
initial_config <- function () {
    require(RAnEnExtra)

    prefix_time <- format(Sys.time(), "%Y-%m-%d-%H-%M-%S")

    machine = 'supermic'
    if (machine == 'Weiming') {
        command.exe <- '~/github/CAnalogsV2/install/bin/canalogs'
        file.forecasts <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "~/geolab_storage_V2/data/NAM12KM/chunk_NAM/analysis_NAM.nc"
        folder.prefix <- '~/geolab_storage_V2/data/NAM12KM/experiments_smart/'
    } else if (machine == 'supermic') {
        # setup on supermic
        command.exe <- '/home/whu/github/CAnalogsV2/install/bin/canalogs'
        file.forecasts <- "/home/whu/data/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "/home/whu/data/chunk_NAM/Analysis_NAM.nc"
        folder.prefix <- paste('/home/whu/experiments/anen_smart/',
                               prefix_time, '/', sep = '')
    }

    file.pixels.computed <- paste('./pixels_computed_list_', prefix_time, '.rdata', sep = '')

    command.verbose <- '--verbose 0'
    folder.accumulate <- paste(folder.prefix, 'anen_accumulate/', sep = '')
    folder.output <- paste(folder.prefix, 'anen_output/', sep = '')
    folder.raster.anen <- paste(folder.prefix, 'anen_raster/', sep = '')
    folder.raster.obs <- paste(folder.prefix, 'obs_raster/', sep = '')
    folder.tmp <- paste(folder.prefix, 'tmp/', sep = '')

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

    #rast.base <- raster(nrows = ygrids.total, ncols = xgrids.total,
    #                    xmn = 0.5, xmx = xgrids.total+.5,
    #                    ymn = 0.5, ymx = ygrids.total+.5)

    # randomly select pixels to compute
    pixels.compute <- sample.int(grids.total,
                                 init.num.pixels.compute)
    pixels.compute <- include.corners(pixels.compute,
                                      xgrids.total,
                                      ygrids.total, 0)

    list.init.config <- list(command.exe = command.exe,
                             command.verbose = command.verbose,
                             file.forecasts = file.forecasts,
                             file.observations = file.observations,
                             file.pixels.computed = file.pixels.computed,
                             folder.prefix = folder.prefix,
                             folder.accumulate = folder.accumulate,
                             folder.output = folder.output,
                             folder.raster.anen = folder.raster.anen,
                             folder.raster.obs = folder.raster.obs,
                             folder.tmp = folder.tmp,
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
                             iteration = iteration,
                             threshold.triangle = threshold.triangle,
                             num.pixels.increase = num.pixels.increase,
                             debug = debug)

    return(list.init.config)
}
