# debug script for func_define_pixels.R
# for convenient local debugging
#
library(stringr)
library(RAnEnExtra)

# developer's setup
iteration <- 1
clean.debug.files <- F
plot.extra.points <- F
read.next.iteration.pixels <- F
call.func.define.pixels <- F
folder.triangles <- paste('~/Desktop/test/', sep = '')
folder.root <- '~/Desktop/test/'

# auto setup
source('func_setup.R')
initial.settings <- initial_config('Weiming', 1)
verbose <- initial.settings$verbose
num.flts <- initial.settings$num.flts
xgrids.total <- initial.settings$xgrids.total
ygrids.total <- initial.settings$ygrids.total
members.size <- initial.settings$members.size
num.champions <- initial.settings$num.champions
tournament.size <- initial.settings$tournament.size
num.error.pixels <- initial.settings$num.error.pixels

evaluation.method <- initial.settings$evaluation.method
evaluation.method <- 3

threshold.triangle <- initial.settings$threshold.triangle
num.pixels.increase <- initial.settings$num.pixels.increase
num.times.to.compute <- initial.settings$num.times.to.compute
num.triangles.from.tournament <- initial.settings$num.triangles.from.tournament
folder.raster.obs <- paste(folder.root, 'obs_raster/', sep = '')
folder.accumulate <- paste(folder.root, 'anen_accumulate/', sep = '')
file.pixels.computed <- paste(folder.root, 'pixels_computed_list.rdata', sep = '')
prefix.anen.raster <- paste(initial.settings$folder.raster.anen, 'iteration',
                            str_pad(as.numeric(iteration), 4, pad = '0'), sep = '')

load(file.pixels.computed)
pixels.computed <- unlist(pixels.computed.list[1:iteration])

if (!dir.exists(folder.triangles)) {
  dir.create(folder.triangles, recursive = T)
}

# source functions
if (call.func.define.pixels) {
  source('func_define_pixels.R')
  res <- define_pixels (
    iteration, folder.raster.obs, prefix.anen.raster, folder.accumulate,
    folder.triangles, pixels.computed, xgrids.total, ygrids.total,
    num.flts, num.pixels.increase, num.times.to.compute, members.size,
    threshold.triangle, tournament.size, num.champions,
    num.error.pixels, num.triangles.from.tournament,
    evaluation.method, verbose)
}

# read pixels for next iteration
if (read.next.iteration.pixels) {
  if (file.exists('pixels_next_iteration.txt')) {
    next.iteration.pixels <- readLines('pixels_next_iteration.txt')
    next.iteration.pixels <- strsplit(next.iteration.pixels, split = ' ')
    next.iteration.pixels <- as.numeric(unlist(next.iteration.pixels))
  } else {
    stop('pixels_next_iteration.txt is not found.')
  }
  
  if (plot.extra.points) {
    file.triangle <- list.files(folder.triangles, full.names = T,
                                str_pad(as.numeric(iteration), 4, pad = '0'))
    load(file.triangle)
    plot(polys.triangles)
    x <- pixels.to.x.by.row(next.iteration.pixels, xgrids.total, 0)
    y <- pixels.to.y.by.row(next.iteration.pixels, xgrids.total, 0)
    points(x, y, pch = 16, cex = 0.5, col = 'red')
  }
}

# clean up files
if (clean.debug.files) {
  files.to.remove <- vector('character')
  target.files <- c('evaluation_log.txt',
                         'pixels_next_iteration.txt')
  for (name in target.files) {
    files.to.remove <- c(files.to.remove,
                         list.files(pattern = name, full.names = T))
  }
  
  folders.to.remove <- vector('character')
  target.folders <- c('debug_local_*')
  for (name in target.folders) {
    folders.to.remove <- c(folders.to.remove,
                           list.files(pattern = name, full.names = T))
  }
  unlink(folders.to.remove)
}