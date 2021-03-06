# File: func_cut_pixels_along_y.R
# Author: Weiming Hu
# Created: Sep 2017
#
# Call the function from RAnEnExtra
# to cut pixels along y based on the
# predefined cuts
#
cut_pixels_along_y <- function(
   pixels.compute, ycuts, xgrids.total,
   ygrids.total, start = 0) {
    require(RAnEnExtra)

    # convert variable types
    pixels.compute <- as.numeric(unlist(pixels.compute))
    ycuts <- as.numeric(unlist(ycuts))

    xgrids.total <- as.numeric(xgrids.total)
    ygrids.total <- as.numeric(ygrids.total)
    start <- as.numeric(start)

    pixels.cut <- cut.pixels.along.y(pixels.compute, ycuts,
                                     xgrids.total, ygrids.total, 0)
    return(pixels.cut)
}

