# debug define pixels in loops
library(RAnEnExtra)
library(stringr)
iteration <- 1
folder.raster.obs <- '~/Desktop/testloop/obs_raster/'
prefix.anen.raster <- ''
folder.triangles <- '~/Desktop/testloop/triangles/'

load('~/Desktop/testloop/pixels_computed_list.rdata')
pixels.computed <- as.numeric(unlist(pixels.computed.list[[1]]))

source('func_setup.R')
initial.settings <- initial_config('Weiming', 1)
xgrids.total <- initial.settings$xgrids.total
ygrids.total <- initial.settings$ygrids.total
num.flts <- 1
num.pixels.increase <- initial.settings$num.pixels.increase
num.times.to.compute <- 1
members.size <- initial.settings$members.size
threshold.triangle <- initial.settings$threshold.triangle
tournament.size <- initial.settings$tournament.size
num.champions <- initial.settings$num.champions
num.error.pixels <- initial.settings$num.error.pixels
num.triangles.from.tournament <- 20
evaluation.method <- 3
interpolation.method <- 1
verbose <- initial.settings$verbose

source('perfect.R')
load('~/Desktop/testloop/obs_raster/time1_flt1.rdata')
plot(rast.obs)
for (i in 1:5) {
  # get data anen arr
  arr.data.anen <- array(NA, dim = c(2, 4, length(pixels.computed)))
  x <- pixels.to.x.by.row(pixels.computed, ncol(rast.obs), 0)
  y <- pixels.to.y.by.row(pixels.computed, ncol(rast.obs), 0)
  points(x, y, pch = 16, col = i, cex = 0.6)
  for (i in 1:2) {
    for (j in 1:4) {
      load(paste(folder.raster.obs, 'time', i, '_flt', j, '.rdata', sep = ''))
      arr.data.anen[i, j, ] <- rast.obs[cellFromXY(rast.obs, cbind(x, y))]
    }
  }
  
  pixels.next <- define_pixels (
    iteration, folder.raster.obs, prefix.anen.raster, arr.data.anen,
    folder.triangles, pixels.computed, xgrids.total, ygrids.total,
    num.flts, num.pixels.increase, num.times.to.compute, members.size,
    threshold.triangle, tournament.size, num.champions,
    num.error.pixels, num.triangles.from.tournament,
    evaluation.method, interpolation.method, verbose)
  
  load(paste(folder.triangles, 'iteration', str_pad(as.numeric(iteration), 4, pad = '0'),
             '.rdata', sep = ''))
  plot(polys.triangles, add = T, border = i, cex = 0.4)
  pixels.computed <- c(pixels.computed, pixels.next)
}
