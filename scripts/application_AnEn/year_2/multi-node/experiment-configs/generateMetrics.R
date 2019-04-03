# This script combines analog and similarity files and generate metrics

library(ncdf4)
library(RAnEn)
library(stringr)

# Define some folders
analog.folder <- '/glade/u/home/wuh20/flash/sliced/analogs'
similarity.folder <- '/glade/u/home/wuh20/flash/sliced/sims'
rds.folder <- '/glade/u/home/wuh20/flash/sliced/rds'
forecast.folder <- '~/scratch/data/AnEn/forecasts'
observation.folder <- '~/scratch/data/AnEn/observations'

analog.files  <- list.files(path = analog.folder, pattern = '.nc', full.names = T)
similarity.files <- list.files(path = similarity.folder, pattern = '.nc', full.names = T)
stopifnot(length(analog.files) == length(similarity.files))

for (i in 1:length(analog.files)) {
    # Get the day id based on the file name. Add 1 because R
    # starts counting from 1 but the file name starts at 0.
    #
    day.id <- as.numeric(gsub(".*/day-(\\d{5})\\.nc", '\\1', analog.files[i])) + 1
    result.file <- paste(rds.folder, '/', str_pad(day.id, 5, pad = 0), '.nc', sep = '')

    if (file.exists(result.file)) {
        print(paste(result.file, 'exists. Skip this generation.'))
        next
    } else {
        # Create a place holder file
        print(paste("Create a placeholder RDS file", result.file))
        saveRDS(result.file, file = result.file)
    }

    print(paste('Reading', analog.files[1]))
    nc <- nc_open(analog.files[1])
    flts <- ncvar_get(nc, 'FLTs')
    xs <- ncvar_get(nc, 'Xs')
    ys <- ncvar_get(nc, 'Ys')
    analogs <- ncvar_get(nc, 'Analogs')
    test.time <- ncvar_get(nc, 'Times')
    member.times <- ncvar_get(nc, 'MemberTimes')
    nc_close(nc)

    # Define the test time for which analogs, observations, forecasts are generated
    stopifnot(length(test.time) == 1)
    test.time <- test.time[1]
    test.year.month <- format(as.POSIXct(test.time, origin = '1970-01-01', tz = 'UTC'), format = '%Y%m')

    # Determine the corresponding forecast file
    forecast.file <- paste(forecast.folder, '/', test.year.month, '.nc', sep = '')
    stopifnot(file.exists(forecast.file))
    print(paste('Forecast file for', test.time, 'is', forecast.file))

    # Read forecasts
    nc <- nc_open(forecast.file)
    forecast.times <- ncvar_get(nc, 'Times')
    num.pars <- nc$dim$num_parameters$len
    num.stations <- nc$dim$num_stations$len
    num.flts <- nc$dim$num_flts$len

    # Figure out the index of current test time in this forecast file
    i.time <- which(forecast.times == test.time)
    stopifnot(length(i.time) == 1)

    forecasts <- ncvar_get(nc, 'Data', start = c(1, 1, i.time, 1),
                           count = c(num.pars, num.stations, 1, num.flts))

    nc_close(nc)

    # Reading observation data is a little bit complicated.
    # First identify the observation times and files needed.
    #
    times.needed <- test.time + flts
    times.needed <- as.POSIXct(times.needed, origin = '1970-01-01', tz = 'UTC')
    files.needed <-  paste(observation.folder, '/', format(times.needed, format = '%Y%m'), '.nc', sep = '')
    stopifnot(length(times.needed) == length(files.needed))

    # Then loop through times and files to read each set of observations
    observation.list <- list()
    observation.times.found <- c()

    for (i.time.needed in 1:length(times.needed)) {
        nc <- nc_open(files.needed[i.time.needed])
        observation.times <- ncvar_get(nc, 'Times')

        num.pars <- nc$dim$num_parameters$len
        num.stations <- nc$dim$num_stations$len

        # Figure out the index of current test time in this file
        i.time <- which(observation.times == times.needed[i.time.needed])

        if (length(i.time) != 1) {
            print(paste("Warning: Observations cannot be found for", times.needed[i.time.needed]))
        } else {
            print(paste("Reading observations for", times.needed[i.time.needed], 'from', files.needed[i.time.needed]))
            observation.list <- c(observation.list, list(ncvar_get(nc, 'Data', start = c(1, 1, i.time), count  = c(num.pars, num.stations, 1))))
            observation.times.found <- c(observation.times.found, times.needed[i.time.needed])
        }

        nc_close(nc)
    }

    # Reorganizing observations
    print("Reorganizing AnEn, forecasts, and observations ...")
    observations <- array(NA, dim = c(num.pars, num.stations, length(observation.list)))
    for (j in 1:dim(observations)[3]) {
        observations[, , j] <- observation.list[[j]]
    }
    rm(observation.list)

    observations.aligned <- alignObservations(observations, observation.times.found, test.time, flts, silent = T, show.progress = F)

    anen <- analogs[, , , 1, drop = F]
    dim(anen) <- c(262792, 1, 53, 50)

    obs <- observations.aligned[16, , , , drop = F]
    dim(obs) <- dim(obs)[-1]

    fcsts <- forecasts[16, , , drop = F]
    dim(fcsts) <- c(262792, 1, 53, 1)

    ret <- list(AnEn = NULL, NAM = NULL)

    print("Verifying AnEn RMSE ...")
    ret$AnEn$RMSE <- verifyRMSE(anen, obs)
    print("Verifying AnEn MAE ...")
    ret$AnEn$MAE <- verifyMAE(anen, obs)
    print("Verifying AnEn Bias ...")
    ret$AnEn$Bias <- verifyBias(anen, obs)
    print("Verifying AnEn Correlation ...")
    ret$AnEn$Cor <- verifyCorrelation(anen, obs)
    print("Verifying AnEn Spread ...")
    ret$AnEn$Spread <- verifySpread(anen)
    print("Verifying AnEn Spread Skill ...")
    ret$AnEn$SpreadSkill <- verifySpreadSkill(anen, obs)
    print("Verifying AnEn CRPS ...")
    ret$AnEn$CRPS <- verifyCRPS(anen, obs)
    print("Verifying AnEn Rank histogram ...")
    ret$AnEn$RH <- verifyRanHist(anen, obs, show.progress = T)
    print("Verifying NAM RMSE ...")
    ret$NAM$RMSE <- verifyRMSE(fcsts, obs)
    print("Verifying NAM MAE ...")
    ret$NAM$MAE <- verifyMAE(fcsts, obs)
    print("Verifying NAM Bias ...")
    ret$NAM$Bias <- verifyBias(fcsts, obs)
    print("Verifying NAM Correlation ...")
    ret$NAM$Cor <- verifyCorrelation(fcsts, obs)

    ret$test.time <- test.time
    ret$flts <- flts
    ret$xs <- xs
    ret$ys <- ys

    saveRDS(ret, file = result.file)
    print(paste("Successfully generated RDS file", result.file))
    break
}

