# AnEn with a spatial metric on a single node
library(ncdf4)

# Define data folders
data.folder <- '~/ExFat-Hu/Data/NCEI/'
forecasts.folder <- paste(data.folder, 'forecasts_yearly/', sep = '')
analysis.folder <- paste(data.folder, 'analysis_yearly/', sep = '')
sim.folder <- 'similarity-nc/'

# Define which test day and flt is used
test.year <- 2018
test.time <- 14
test.flt <- 4

# Define how the granularity of the problem
num.stations <- 262792
chunck.size <- 100

# Calculate start and size for each sub problem
chuncks.start <- seq(0, num.stations, by = chunck.size)
chuncks.size <- c(chuncks.start[-1], num.stations) - chuncks.start

# Define common variables
exec <- 'similarityCalculator'
time.match.mode <- 0
observation.id <- 0
max.par.nan <- 0
max.flt.nan <- 1
verbose <- 2

# Define search years
# search.years <- 2008:2017
search.years <- 2017

for (j in 1:length(search.years)) {
  search.year <- search.years[j]
  cat(paste('Search through the year', search.year, '\n'))
  
  # Define nc files to read data from
  test.forecast.nc <- paste(forecasts.folder, test.year, '.nc', sep = '')
  search.forecast.nc <- paste(forecasts.folder, search.year, '.nc', sep = '')
  search.observation.nc <- paste(analysis.folder, search.year, '.nc', sep = '')
  
  # Define the output similarity nc file
  sim.nc <- paste(sim.folder, 'sim-', search.year, '.nc', sep = '')
  
  # Define how many times exist in the search forecast file
  nc <- nc_open(search.forecast.nc)
  num.search.forecast.times <- length(ncvar_get(nc, 'Times'))
  nc_close(nc)
  
  # Define how many times exist in the search observation file
  nc <- nc_open(search.observation.nc)
  num.search.observation.times <- length(ncvar_get(nc, 'Times'))
  nc_close(nc)
  
  # Genearte similarity files
  for (i in 1:length(chuncks.size)) {
    cat(paste('-- Working on station', chuncks.start[i], '~', chuncks.start[i] + chuncks.size[i] - 1, '\n'))
    command <- paste(exec, '--test-forecasts-nc', test.forecast.nc,
                     '--test-start', paste(0, chuncks.start[i], test.time, test.flt),
                     '--test-count', paste(10, chuncks.size[i], 1, 1),
                     '--search-forecasts-nc', search.forecast.nc,
                     '--search-start', paste(0, chuncks.start[i], 0, test.flt),
                     '--search-count', paste(10, chuncks.size[i], num.search.forecast.times, 1),
                     '--observation-nc', search.observation.nc,
                     '--search-start', paste(0, chuncks.start[i], 0),
                     '--search-count', paste(10, chuncks.size[i], num.search.observation.times),
                     '--similarity-nc', sim.nc, '-v', verbose,
                     '--time-match-mode', time.match.mode,
                     '--observation-id', observation.id,
                     '--max-par-nan', max.par.nan,
                     '--max-flt-nan', max.flt.nan)
  }
}