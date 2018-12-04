library(abind)
library(ncdf4)
library(stringr)

# Disable scientific notation
options(scipen = 999)

# Define data folders
data.folder <- '~/ExFat-Hu/Data/NCEI/'
forecasts.folder <- paste(data.folder, 'forecasts_reformat/', sep = '')
sds.folder <- '/home/graduate/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/sds'

verbose <- 3

# Define search years
pattern <- paste("with-wind_(", paste(2016:2017, collapse = "|"), ")", sep = '')
search.files <- list.files(path = forecasts.folder, full.names = T, pattern = pattern)
search.files <- sort(search.files, decreasing = T)

# Read how many times, stations, parameters, and flts exist in each search file
search.files.num.times <- c()
search.files.num.pars <- c()
search.files.num.flts <- c()
search.files.num.stations <- c()
for (i in 1:length(search.files)) {
  nc <- nc_open(search.files[i])
  search.files.num.times <- c(search.files.num.times, length(ncvar_get(nc, 'Times')))
  search.files.num.pars <- c(search.files.num.pars, length(ncvar_get(nc, 'ParameterNames')))
  search.files.num.flts <- c(search.files.num.flts, length(ncvar_get(nc, 'FLTs')))
  search.files.num.stations <- c(search.files.num.stations, length(ncvar_get(nc, 'StationNames')))
  nc_close(nc)
}

# Define the station chunks to compute sds
search.files.stations.start <- seq(0, 428*614, by = 5000)
search.files.stations.count <- c(search.files.stations.start[-1], 428*614) - search.files.stations.start
search.files.in <- paste(search.files, collapse = ' ')

# Check whether the sds folder exists
if (!dir.exists(sds.folder)) {
  stop(paste(sds.folder, 'does not exist!'))
}

# Pre-compute the standard deviation by chunks of stations
for (i in 1:length(search.files.stations.start)) {
  file.out <- paste(sds.folder, '/sds-', 
                    str_pad(i, width = 4, pad = '0'), '.nc', sep = '')
  
  if (file.exists(file.out)) {
    cat(file.out, 'already exists. Skip this file.\n')
    next
  } else {
    cat('Working on station', search.files.stations.start[i], '~', 
        search.files.stations.start[i] + search.files.stations.count[i] - 1, '\n')
    command <- paste(
      'OMP_NUM_THREADS=8 /home/graduate/wuh20/github/AnalogsEnsemble/output/bin/standardDeviationCalculator',
      '-v', verbose, '-i', search.files.in, '-o', file.out,
      '--start', paste(rep(c(0, search.files.stations.start[i], 0, 0), length(search.files)), collapse = ' '),
      '--count', paste(paste(search.files.num.pars, search.files.stations.count[i],
                             search.files.num.times, search.files.num.flts), collapse = ' '))
    system(command)
  }
}

cat("Finished computing standard deviation!\n")

# Combine sds files
cat("Combining standard deviation files ...\n")
sds.files <- list.files(path = sds.folder, pattern = '.txt', full.names = T)
sds.files <- sort(sds.files, decreasing = F)

command <- paste(
  '/home/graduate/wuh20/github/AnalogsEnsemble/output/bin/standardDeviationCalculator',
  '-v', verbose, '-t', 'StandardDeviation', '-i', paste(sds.files, collapse = ' '),
  '-o', sds.folder, '/sds.nc', '-a', '1'
)
system(command)

cat("Finished combining standard deviation files!\n")

# Revert and enable scientific notation
options(scipen = 0)
