library(maps)
library(ncdf4)
library(RAnEnExtra)
  
nc <- nc_open('~/geolab_storage_V3/data_static/NAM/NCEI/201601.nc')
xs <- ncvar_get(nc, 'Xs') - 360
ys <- ncvar_get(nc, 'Ys')
nc_close(nc)

usa_boundary <- map('state', plot = F)
ext <- c(left = floor(min(usa_boundary$x, na.rm = T)),
         right = ceiling(max(usa_boundary$x, na.rm = T)),
         bottom = floor(min(usa_boundary$y, na.rm = T)),
         top = ceiling(max(usa_boundary$y, na.rm = T)))

subset <- subsetCoordinates(xs = xs, ys = ys, poi = ext, file.output = "domain-USA.cfg", num.chunks = 20)
