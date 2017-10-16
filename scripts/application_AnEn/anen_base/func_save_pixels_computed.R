# File: func_save_pixels_computed.R
# Author: Weiming Hu
# Created: Sep 2017
#
# save_pixels_computed saves the pixels to a list of
# pixels.computed.list. This function is called locally.
#
save_pixels_computed <- function(
    pixels, file.pixels.computed) {

    if (file.exists(file.pixels.computed)) {
        load(file.pixels.computed)
        pixels.computed.list <- c(pixels.computed.list,
                                  list(unlist(pixels)))
    } else {
        pixels.computed.list <- list(unlist(pixels))
    }

    save(pixels.computed.list, file = file.pixels.computed)
}
