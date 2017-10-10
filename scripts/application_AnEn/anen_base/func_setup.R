# set up basic parameters that would be shared by all processes
initial_config <- function (user = 'Weiming') {
    require(RAnEnExtra)

    prefix_time <- format(Sys.time(), "%Y-%m-%d-%H-%M-%S")

    if (user == 'Weiming') {
        command.exe <- '/home/whu/github/CAnalogsV2/install/bin/canalogs'
        file.forecasts <- "/home/whu/data/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "/home/whu/data/chunk_NAM/Analysis_NAM.nc"
        folder.scripts <- '/home/whu/github/hpc-workflows/scripts/application_AnEn/anen_base/'
        folder.prefix <- paste('/home/whu/experiments/anen_smart/',
                               prefix_time, '/', sep = '')
    } else if (user == 'Vivek') {
        # setup on supermic
        command.exe <- '/work/vivek91/modules/CAnalogsV2/build/canalogs'
        file.forecasts <- "/work/vivek91/chunk_NAM/Forecasts_NAM_sliced.nc"
        file.observations <- "/work/vivek91/chunk_NAM/Analysis_NAM.nc"
        folder.scripts <- ''
        folder.prefix <- paste('/work/vivek91/anen_smart/',
                               prefix_time, '/', sep = '')
    }

    folder.local <- paste('./local_', prefix_time, '/', sep = '')
    dir.create(folder.local, recursive = T)
    
    file.pixels.computed <- paste(folder.local, 'pixels_computed_list.rdata', sep = '')

    verbose <- '2'
    folder.accumulate <- paste(folder.prefix, 'anen_accumulate/', sep = '')
    folder.output <- paste(folder.prefix, 'anen_output/', sep = '')
    folder.raster.anen <- paste(folder.prefix, 'anen_raster/', sep = '')
    folder.raster.obs <- paste(folder.prefix, 'obs_raster/', sep = '')
    folder.triangles <- paste(folder.prefix, 'triangles/', sep = '')

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
    init.iteration <- 1
    threshold.triangle <- 4
    num.pixels.increase <- 10

    debug <- 0
    interpolate.AnEn.rasters <- 1

    # randomly select pixels to compute
    pixels.compute <- sample.int(grids.total,
                                 init.num.pixels.compute)
    pixels.compute <- include.corners(pixels.compute,
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
                             threshold.triangle = threshold.triangle,
                             num.pixels.increase = num.pixels.increase,
                             interpolate.AnEn.rasters = interpolate.AnEn.rasters,
                             debug = debug)

    return(list.init.config)
}
