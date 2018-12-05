# AnEn with a spatial metric on a single node
library(raster)
library(ncdf4)
library(stringr)
library(RColorBrewer)
library(stringr)
library(maps)

# Define data folders
data.folder <- '~/ExFat-Hu/Data/NCEI/'
forecasts.folder <- paste(data.folder, 'forecasts_reformat/', sep = '')
analysis.folder <- paste(data.folder, 'analysis_collapsed/', sep = '')
sim.folder <- '/home/graduate/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/sim/'

sds.nc <- '/home/graduate/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/sds/sds.nc'

# Define which test day and flt is used
test.year <- 2018
test.month <- 5
test.time <- 14
test.flt <- 4

# Define how the granularity of the problem
num.stations <- 262792
chunk.size <- 262792 + 1

# Calculate start and size for each sub problem
chunks.start <- seq(0, num.stations, by = chunk.size)
chunks.size <- c(chunks.start[-1], num.stations) - chunks.start

# Define common variables
exec <- '/home/graduate/wuh20/github/AnalogsEnsemble/output/bin/similarityCalculator'
cols <- colorRampPalette(brewer.pal(8, 'OrRd'))(100)
time.match.mode <- 1
observation.id <- 0
max.par.nan <- 0
max.flt.nan <- 1
verbose <- 3
nrow <- 428
ncol <- 614

# Wether we should plot into filse
plot.to.file <- F
plot.folder <- sim.folder

# Create a template raster for visualization
nc <- nc_open('/home/graduate/wuh20/ExFat-Hu/Data/NCEI/analysis_collapsed/200810.nc')
stations.x <- ncvar_get(nc, 'Xs') - 360
stations.y <- ncvar_get(nc, 'Ys')
nc_close(nc)
crs.latlon <- CRS("+proj=longlat +datum=WGS84")
df <- data.frame(x = stations.x, y = stations.y)
ext <- extent(df)
rast.template <- raster(ext, nrow = nrow, ncol = ncol, crs = crs.latlon)

# Define search years
pattern <- paste("with-wind_(", paste(2016:2017, collapse = "|"), ")", sep = '')
# pattern <- paste("with-wind_(", paste(2008:2017, collapse = "|"), ")", sep = '')
search.files <- list.files(path = forecasts.folder, full.names = T, pattern = pattern)
search.files <- sort(search.files, decreasing = T)

# Check whether the similarity folder exists
if (!dir.exists(sim.folder)) {
  stop(paste(sim.folder, "does not exists."))
}

# Generate similarity metric for each search forecasts
search.forecast.times <- c()
sims.time.rdata <- paste(sim.folder, 'times.RData', sep = '')
for (j in 1:length(search.files)) {
  search.file <- search.files[j]
  search.time <- gsub("^.*//with-wind_(\\d{6})\\.nc$", "\\1", search.file)
  cat(paste('Search in the file', search.file, '\n'))
  
  # Define nc files to read data from
  test.forecast.nc <- paste(forecasts.folder, 'with-wind_', test.year,
                            str_pad(test.month, 2, pad = '0'), '.nc', sep = '')
  search.forecast.nc <- search.file
  
  search.observation.nc <- paste(analysis.folder, search.time, '.nc', sep = '')
  if (!file.exists(search.observation.nc)) {
    # If observation file for this search forecast does not exist,
    # skip the generation of this search time
    #
    cat(search.observation.nc, "does not exist. Skip the search file.\n")
    next
  }
  
  # Define how many times exist in the search forecast file
  nc <- nc_open(search.forecast.nc)
  search.forecast.times <- c(search.forecast.times, ncvar_get(nc, 'Times'))
  num.search.forecast.times <- length(search.forecast.times)
  nc_close(nc)
  
  # Define how many times exist in the search observation file
  nc <- nc_open(search.observation.nc)
  num.search.observation.times <- length(ncvar_get(nc, 'Times'))
  nc_close(nc)
  
  # Genearte similarity files
  for (i in 1:length(chunks.size)) {
    cat(paste('-- Working on station', chunks.start[i], '~', chunks.start[i] + chunks.size[i] - 1, '\n'))

    # Define the output similarity nc file
    sim.nc <- paste(sim.folder, 'sim-', search.time, '-',
                    str_pad(chunks.start[i], width = 7, pad = '0'),
                    '.nc', sep = '')
  
    if (file.exists(sim.nc)) {
      cat(sim.nc, 'already exists. Skip this file.\n')
      next
    }

    command <- paste(exec, '--test-forecast-nc', test.forecast.nc,
                     '--test-start', paste(0, chunks.start[i], test.time, test.flt),
                     '--test-count', paste(12, chunks.size[i], 1, 1),
                     '--search-forecast-nc', search.forecast.nc,
                     '--search-start', paste(0, chunks.start[i], 0, test.flt),
                     '--search-count', paste(12, chunks.size[i], num.search.forecast.times, 1),
                     '--observation-nc', search.observation.nc,
                     '--obs-start', paste(0, chunks.start[i], 0),
                     '--obs-count', paste(10, chunks.size[i], num.search.observation.times),
                     '--similarity-nc', sim.nc, '-v', verbose,
                     '--sds-nc', sds.nc,
                     '--sds-start', paste(0, chunks.start[i], test.flt),
                     '--sds-count', paste(12, chunks.size[i], 1),
                     '--time-match-mode', time.match.mode,
                     '--observation-id', observation.id,
                     '--max-par-nan', max.par.nan,
                     '--max-flt-nan', max.flt.nan)
    system(command)
  }
  
  if (!file.exists(sim.nc)) {
    stop(paste(sim.nc, "is not generated correctly."))
  }
  
  # Analyze the simularity file
  nc <- nc_open(sim.nc)
  sim.mat <- ncvar_get(nc, 'SimilarityMatrices')
  nc_close(nc)
  
  # Extract the lowest distance for each grid point
  sim.best.ori <- apply(sim.mat[1, , ], 2, min, na.rm = T)
  sim.best <- log(sim.best.ori, base = 10)
  
  if (F) {
    # Reshape the data and plot it
    rast.sim.best <- rasterize(df, rast.template, sim.best, fun=mean)
    plot.name <- paste("Best similarity metric map by searching", search.time)
    
    if (plot.to.file) {
      # Plot to a file
      cat(paste("Generate plot file for", search.time, "\n"))
      
      file.to.plot <- paste(plot.folder, search.time, '.pdf', sep = '')
      if (file.exists(file.to.plot)) {
        next
      }
      
      pdf(file.to.plot, width = 12, height = 6)
    }
    
    par(mfrow = c(1, 2), mar = c(4, 2, 4, 4))
    hist(sim.best, xlab = 'Metric value (log10)')
    plot(rast.sim.best, col = cols, main = plot.name)
    map(add = T)
    mtext(paste("Max metric:", round(max(sim.best.ori), 3),
                "; Min metric:", round(min(sim.best.ori), 3)))
    
    if (plot.to.file) {
      dev.off()
      # If you are using Ubuntu, you can use pdfunite to combine pdf files
      # pdfunite *.pdf combined.pdf
    }
  }
}

if (!file.exists(sims.time.rdata)) {
  cat("Export search times to an RData file", sims.time.rdata, '\n')
  save(search.forecast.times, file = sims.time.rdata)
}
