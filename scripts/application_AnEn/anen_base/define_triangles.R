# define triangles and output to a file
#
define_triangles <- function(
    pixels.compute, xgrids.total,
    folder.raster.anen, iteration) {
    require(deldir)
    require(spatstat) 
    require(maptools)
    require(RAnEnExtra)

    # convert and prepare pixel coordinates
    x <- pixels.to.x.by.row(pixels.compute, xgrids.total, 0)
    y <- pixels.to.y.by.row(pixels.compute, xgrids.total, 0)

    # define triangles
    df <- data.frame(x, y)
    W <- ripras(df, shape="rectangle")
    polys.triangle <- as(delaunay(as.ppp(df, W=W)), "SpatialPolygons")

    folder.raster.iteration <- paste(folder.raster.anen, 'iteration',
                                     iteration, '/', sep = '')
    save(polys.triangle, file = paste(folder.raster.iteration,
                                      'triangulations.rdata', sep = ''))
}
