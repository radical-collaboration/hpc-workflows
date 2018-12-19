# Select analogs based on the spatial metric
library(maps)
library(ncdf4)
library(abind)
library(raster)
library(fields)
library(stringr)
library(parallel)
library(OpenImageR)
library(RColorBrewer)

# These are the definitions from the 05 script for the time of prediction
cols <- colorRampPalette(brewer.pal(8, 'OrRd'))(100)
crs.latlon <- CRS("+proj=longlat +datum=WGS84")
test.year <- 2018
test.month <- 5
test.time <- 14
test.flt <- 4
nrow <- 428
ncol <- 614

bypass.visualization <- F
plot.to.file <- T

# Read all similarity metric and time information
sim.folder <- '~/github/hpc-workflows/scripts/application_AnEn/year_2/sim'
sim.files <- list.files(path = sim.folder, pattern = '*.nc', full.names = T)
sim.files <- sort(sim.files, decreasing = T)

sims.rdata <- paste(sim.folder, '/sims.RData', sep = '')
sims.time.rdata <- paste(sim.folder, '/sims-times.RData', sep = '')

# Read similarity matrices
if (file.exists(sims.rdata)) {
  cat('Load similarity matrices from the RData file.\n')
  load(sims.rdata)
  
} else {
  cat("Reading similarity file", sim.files[1], 'as a template ... \n')
  nc <- nc_open(sim.files[1])
  sims <- ncvar_get(nc, 'SimilarityMatrices')
  nc_close(nc)
  
  for (i in 2:length(sim.files)) {
    sim.file <- sim.files[i]
    cat("Reading similarity file", sim.file, '\n')
    nc <- nc_open(sim.file)
    sims <- abind(sims, ncvar_get(nc, 'SimilarityMatrices'), along = 2)
    nc_close(nc)
  }
  
  cat('Export similarity matrices to an RData file.\n')
  save(sims, file = sims.rdata)
}

# Read time information
if (file.exists(sims.time.rdata)) {
  load(sims.time.rdata)
  search.forecast.times <- as.POSIXct(
    search.forecast.times, origin = '1970-01-01', tz = 'UTC')
} else {
  stop("Can't find time information for similarity matrices!")
}

# Read location information
nc <- nc_open(sim.files[1])
xs <- ncvar_get(nc, 'Xs') - 360
ys <- ncvar_get(nc, 'Ys')
nc_close(nc)

# Define a raster template
#
df <- data.frame(x = xs, y = ys)
ext <- extent(df)
rast.template <- raster(ext, nrow = nrow, ncol = ncol, crs = crs.latlon)

# Define the stacked raster file
sims.stack.file <- paste(sim.folder, '/sims-stack.tif', sep = '')

if (file.exists(sims.stack.file)) {
  cat('Reading raster stack file ...\n')
  sims.stack <- stack(sims.stack.file)
  
} else {
  cat('Generating raster stack file ...\n')
  # Rasterize the simialrity metric for each day using parallelization
  res <- mclapply(1:dim(sims)[2], function(i, df, rast.template, sims) {
    require(raster)
    return(rasterize(df, rast.template, sims[1, i, ], fun = mean))
  }, df = df, rast.template = rast.template, sims = sims, mc.cores = detectCores())
  
  # Stack rasters in the returned list
  sims.stack <- stack(res)
  
  # Write the stack into a file
  writeRaster(sims.stack, filename = sims.stack.file)
}

#if (!bypass.visualization) {
if (F) {
  # This chunk of script first lets you select a region to analyze;
  # then plot the trendline of the mean similarity metric of this region.
  #
  # Select a region
  plot(sims.stack[[1]], col = cols); map(add = T)
  ext <- drawExtent()
  
  # Extract values for this region
  values <- extract(sims.stack, ext)
  
  # plot the trend line for values in this region
  at <- seq(1, length(search.forecast.times), by = 10)
  plot(colMeans(values, na.rm = T), type = 'l', xaxt = 'n', 
       xlab = 'Date', ylab = 'Similarity Metric')
  axis(1, at = at, labels = search.forecast.times[at])
}

# Because the original search.forecast.times and sims are in the following order
# 201712 1, 2, 3, ..., 31
# 201711 1, 2, 3, ..., 30
# ...
#
# I need to reorder them to the following order
# 201712, 31, 30, ..., 1
# 201711, 30, 29, ..., 1
# ...
#
decreasing.order <- order(search.forecast.times, decreasing=T)
search.forecast.times = search.forecast.times[decreasing.order]
sims <- sims[ , decreasing.order, , drop = F]

# Select analogs based on a spatial metric
#
# Define the products that we will be generating by the end of the selection
product.sims <- sims[1, 1, ]
product.end.i <- rep(1, dim(sims)[3])

# Define the grid points that are left to continue the searching
grids.left <- 1:length(product.sims)

# Define the kernel
kernel <- matrix(c(1, 1, 1, 1, 10, 1, 1, 1, 1), nrow = 3, ncol = 3) / 18

# Define max iteration
max.i <- 99999999999999

# Define line width for contours
lwd <- 0.2

for (i in 1:length(search.forecast.times)) {
  cat('Processing similarity matrices at time',
      as.character(search.forecast.times[i]), '\n')

  # Transpose the matrix for a better visualization
  sims.mat <- t(matrix(data = sims[1, i, ], nrow = nrow, byrow = T))
  processed <- convolution(sims.mat, kernel, mode = "same")
  continue <- processed > 5
  
  # Calculate the intersect of grids that stop the searching
  # and that are left in the pool
  #
  grids.stop <- intersect(grids.left, which(!continue))
  
  # Assign the similarity values on the grid points that 
  # do not need to continue searching
  #
  product.sims[grids.stop] <- sims[1, i, grids.stop]
  product.end.i[grids.stop] <- i
  
  cat('The leftover grid point count changes from', length(grids.left))
  grids.left <- setdiff(grids.left, grids.stop)
  cat(' to', length(grids.left), '\n')
  
  if (i >= max.i) {
    cat("Max i reached.\n")
    break
  }
  
  if (length(grids.left) == 0) {
    cat("No leftover grids.\n")
    break
  }
  
  if (!bypass.visualization) {
    product.sims.mat <- t(matrix(
      data = product.sims, nrow = nrow, byrow = T))
    product.end.i.mat <- t(matrix(
      data = product.end.i, nrow = nrow, byrow = T))
    
    if (plot.to.file)
      png(paste(sim.folder, '/optimized-sim/optimized-sim-i-',
                str_pad(i, width = 5, pad = '0'), '.png', sep = ''),
          width = 12, height = 6, res = 400, units = 'in')
    
    par(mfrow = c(1, 2), oma = c(1, 1, 1, 3))
    
    # image.plot(product.sims.mat, col = cols)
    # contour(product.sims.mat, add = T, col = 'grey', lwd = lwd)
    # title(paste('Similarity Metric Product Until',
    #             as.character(search.forecast.times[i])))
    # 
    # image.plot(product.end.i.mat, col = cols)
    # title('Search Amount')
    
    rast.tmp <- rasterize(
      df, rast.template, log(product.sims.mat, base = 10), fun = mean)
    plot(rast.tmp, col = cols, main = 
           paste('Similarity Metric (log10) Product Until',
                 as.character(search.forecast.times[i])))
    map(add = T, col = 'grey')
    contour(rast.tmp, add = T, col = 'white', lwd = lwd)
    mtext(paste('Min:', round(min(product.sims.mat, na.rm = T), 4),
                ' Mean:', round(mean(product.sims.mat, na.rm = T), 4)))
    
    rast.tmp <- rasterize(df, rast.template, product.end.i, fun = mean)
    if (i == 1) {
      plot(rast.tmp, col = 'white', main = 'Amount of Search Data')
    } else {
      plot(rast.tmp, col = cols, main = 'Amount of Search Data')
    }
    map(add = T, col = 'grey')
    
    if (plot.to.file) dev.off()
  }
}

if (length(grids.left) != 0) {
  product.sims[grids.left] <- sims[1, i, grids.left]
  product.end.i[grids.left] <- i
}

if (!bypass.visualization) {
  if (plot.to.file)
    png(paste(sim.folder, '/optimized-sim/optimized-sim-i-',
              str_pad(i, width = 5, pad = '0'), '.png', sep = ''),
        width = 12, height = 6, res = 400, units = 'in')
  
  product.sims.mat <- t(matrix(
    data = product.sims, nrow = nrow, byrow = T))
  product.end.i.mat <- t(matrix(
    data = product.end.i, nrow = nrow, byrow = T))
  
  par(mfrow = c(1, 2), oma = c(1, 1, 1, 2))
  
  # image.plot(product.sims.mat, col = cols)
  # contour(product.sims.mat, add = T, col = 'grey', lwd = lwd)
  # title(paste('Similarity Metric Product Until',
  #             as.character(search.forecast.times[i])))
  # 
  # image.plot(product.end.i.mat, col = cols)
  # title('Search Amount')
  
  rast.tmp <- rasterize(
    df, rast.template, log(product.sims.mat, base = 10), fun = mean)
  plot(rast.tmp, col = cols, main = 
         paste('Similarity Metric (log10) Product Until',
               as.character(search.forecast.times[i])))
  map(add = T, col = 'grey')
  contour(rast.tmp, add = T, col = 'white', lwd = lwd)
  mtext(paste('Min:', round(min(product.sims.mat, na.rm = T), 4),
              ' Mean:', round(mean(product.sims.mat, na.rm = T), 4)))
    
  
  rast.tmp <- rasterize(df, rast.template, product.end.i, fun = mean)
  plot(rast.tmp, col = cols, main = 'Amount of Search Data')
  map(add = T, col = 'grey')
  
  if (plot.to.file) dev.off()
}


# You can use ffmpeg to combine pictures to a video
# ffmpeg -r 8 -i optimized-sim-i-%05d.png -c:v libx264 -pix_fmt yuv420p out.mp4
