# read_pixels_computed read the pixels_computed_list
# rdata file and return the accumulated list of the
# pixels that have been computed. This function is
# called locally.
#
read_pixels_computed <- function(
    file.pixels.computed, iteration) {

    if (file.exists(file.pixels.computed)) {
        load(file.pixels.computed)

        if (as.numeric(iteration) <= length(pixels.computed.list)) {
            res <- unlist(pixels.computed.list[1 : as.numeric(iteration)])
        } else {
            stop(paste("Given iteration index [" , as.numeric(iteration),
                       "] is larger than the number of sublists [",
                       length(pixels.computed.list), "] in the file ",
                       file.pixels.computed, sep = ''))
        }
    } else {
        stop(paste("Can't find file", file.pixels.computed))
    }

    return(res)
}
