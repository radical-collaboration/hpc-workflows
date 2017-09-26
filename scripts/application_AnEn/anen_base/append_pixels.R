# append_pixels appends the pixels to the list of
# pixels.computed.list. Thus, this function should
# be called on supercomputers.
#
append_pixels <- function(
    pixels, file.pixels.computed) {

    if (file.exists(file.pixels.computed)) {
        load(file.pixels.computed)
        pixels.computed.list <- c(pixels.computed.list,
                                  list(unlist(pixels)))
        save(pixels.computed.list, file = file.pixels.computed)

    } else {
        stop(paste("File not found: ",
                   file.pixels.computed))
    }
}
