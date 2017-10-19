# debug script for func_define_pixels.R
# for convenient local debugging
#

# developer's setup
iteration <- 2
folder.root <- '/Volumes/ExFat-Hu/Experiments/results_random_1_out_of_4/'
prefix.anen.raster <- '~/Desktop/test'

# auto setup
source('func_setup.R')
initial.settings <- initial_config()
verbose <- initial.settings$verbose
num.flts <- initial.settings$num.flts
xgrids.total <- initial.settings$xgrids.total
ygrids.total <- initial.settings$ygrids.total
members.size <- initial.settings$members.size
num.champions <- initial.settings$num.champions
tournament.size <- initial.settings$tournament.size
num.error.pixels <- initial.settings$num.error.pixels
evaluation.method <- initial.settings$evaluation.method
threshold.triangle <- initial.settings$threshold.triangle
num.pixels.increase <- initial.settings$num.pixels.increase
num.times.to.compute <- initial.settings$num.times.to.compute
num.triangles.from.tournament <- initial.settings$num.triangles.from.tournament
folder.triangles <- paste(folder.root, 'triangles/')
folder.raster.obs <- paste(folder.root, 'obs_raster/', sep = '')
folder.accumulate <- paste(folder.root, 'anen_accumulate/', sep = '')
file.pixels.computed <- paste(folder.root, 'pixels_computed_list.rdata', sep = '')

load(file.pixels.computed)
pixels.computed <- unlist(pixels.computed.list[1:iteration])

# source functions
source('func_define_pixels.R')

# clean up files
files.to.remove <- list.files(pattern = 'pixels_next_iteration.txt', full.names = T)
file.remove(files.to.remove)
