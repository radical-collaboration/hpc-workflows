# get_list_length gets the length of the list pixels.computed.list.
# This is helpful to acquire the number of iterations, because the
# length of the pixels.computed.list equals the number of iterations
#
get_list_length <- function(file.pixels.computed) {
    if (!file.exists(file.pixels.computed)) {
        stop(paste("File not found", file.pixels.computed))
        return(-1)
    }

    load(file.pixels.computed)
    return(length(pixels.computed.list))
}
