# get the accumulated pixels up until the
# current iteration
#
get_accumulated_pixels <- function (
    file.pixels.computed, iteration) {

  pixels.compute <- c()
  load(file.pixels.computed)
  pixels.compute <- unlist(pixels.computed.list[1:as.numeric(iteration)])
  reutn(pixels.compute)
}
