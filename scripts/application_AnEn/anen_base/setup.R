# set up file for ENTK and AnEN
#
# this file configures the initial arguments for the AnEn executable
# the function will be called from the master.py script
#
initial_config <- function (verbose = F) {
    current_stage <- 1
    init.num.pixels <- 100
    nrows <- 100
    ncols <- 100

    file.forecast <- '/home/whu/data/Temperature_NAM/Forecasts_NAM_C.nc'
    file.observation <- '/home/whu/data/Temperature_NAM/Analysis_NAM_R.nc'

    num.flts <- 4
    num.times <- 822
    num.parameters <- 13
    num.stations.per.chunk <- 10000
    num.stations <- 262790

    test.ID.start <- 700
    test.ID.end <- 701
    train.ID.start <- 0
    train.ID.end <- 699
    members.size <- 20
    rolling <- -2
    cores <- 16

    output.prefix <- paste('/work/whu/', current_stage, '_', sep = '')
    output.AnEn <- paste(output.prefix, 'anen.nc', sep = '')
    #output.computed.pixels <- paste(output.prefix, 'computed_pixels.rdata', sep = '')
    #stations.ID <- sample.int(nrows * ncols, init.num.pixels)

    # make sure that the points at the four corners are included
    #if (!(0 %in% stations.ID)) {
    #    stations.ID[1] <- 0
    #}
    #if (!(99 %in% stations.ID)) {
    #    stations.ID[2] <- 99
    #}
    #if (!(9900 %in% stations.ID)) {
    #    stations.ID[3] <- 9900
    #}
    #if (!(9999 %in% stations.ID)) {
    #    stations.ID[4] <- 9999
    #}

    # save the index numbers of computed pixels
    #save(stations.ID, file = output.computed.pixels)

    list.init.config <- list(file.forecast = file.forecast,                             
                             file.observation = file.observation,
                             output.AnEn = output.AnEn,
                             #stations.ID = stations.ID,
                             test.ID.start = test.ID.start,
                             test.ID.end = test.ID.end,
                             train.ID.start = train.ID.start,
                             train.ID.end = train.ID.end,
                             rolling = rolling,
                             members.size = members.size,
                             cores = cores,
                             num.flts = num.flts,
                             num.times = num.times,
                             num.parameters = num.parameters,
                             num.stations.per.chunk = num.stations.per.chunk,
                             num.stations = num.stations,
                             nrows = nrows,
                             ncols = ncols)

    if (verbose) {
        print(list.init.config)
    }
  
    return(list.init.config)
}
