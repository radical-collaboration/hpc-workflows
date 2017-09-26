# call the function from RAnEnExtra
# to cut pixels along y based on the
# predefined cuts
#
cut_pixels_along_y <- function(
   pixels.compute, ycuts, xgrids.total,
   ygrids.total, start = 0) {
    require(RAnEnExtra)

    pixels.cut <- cut.pixels.along.y(pixels.compute, ycuts,
                                     xgrids.total, ygrids.total, 0)
    return(pixels.cut)
}

