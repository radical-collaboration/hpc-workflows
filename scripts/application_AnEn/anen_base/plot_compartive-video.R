# debug algorithm
library(raster)
library(deldir)
library(spatstat)
library(maptools)
library(RAnEnExtra)
library(ggplot2)
library(reshape2)
library(RColorBrewer)
library(stringr)

addalpha <- function(colors, alpha=1.0) {
  r <- col2rgb(colors, alpha=T)
  # Apply alpha
  r[4,] <- alpha*255
  r <- r/255.0
  return(rgb(r[1,], r[2,], r[3,], r[4,]))
}


#file.raster.obs <- '~/Desktop/results_new_evaluation_6/obs_raster/time1_flt1.rdata'
file.raster.obs <- '~/geolab_storage_V2/data/Analogs/NAM_analysis_raster/time1_flt1.rdata'
load(file.raster.obs)
values(rast.obs) <- values(rast.obs) - 273.15


size <- 30
pts.edge <- 5
pts.growth <- 20
iterations <- 30
repetition <- 1

plot.results <- T
save.plot.data <- F
output.error.plot <- F
output.speedup.plot <- F
output.triangle.plot <- T

point.col <- 'red'
point.size <- .3

transparent.plot <- T
# gradient.col <- c('#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c',
#                   '#fc4e2a', '#e31a1c', '#bd0026', '#800026')

gradient.col <- brewer.pal(11, 'Spectral')[11:1]
alpha <- .6

triangle.col <- 'black'
triangle.width <- .3

x.ticks.display.limit <- 10



generate.inital.population = function( raster, size=100, pts.edge=5 ) {
  
  # Generate an initial random population
  #
  pop = sampleRandom(raster, size - pts.edge*4,xy=T)
  
  xs = xFromCol(raster)
  xs.edge = c( xs[1], xs[length(xs)], sample(xs, pts.edge))
  
  ys = yFromRow(raster)
  ys.edge = c( ys[1], ys[length(ys)], sample(ys, pts.edge))
  
  top    = expand.grid(xs.edge,ys.edge[1])
  bottom = expand.grid(xs.edge,ys.edge[2])
  left   = expand.grid(xs.edge[1],ys.edge)
  right  = expand.grid(xs.edge[2],ys.edge)
  
  boundary.sp   = SpatialPoints( rbind(top, bottom, left, right) )
  boundary.val  = extract( raster, boundary.sp )
  
  # bind everthing together and remove the duplicates
  pop      = unique( rbind( pop, cbind(coordinates(boundary.sp), boundary.val) ) )
  pop.spdf = SpatialPointsDataFrame(pop[,1:2],data=data.frame(value=pop[,3]) )
  
  
  return( pop.spdf )
}


triangulate = function( pts.spdf, raster, mode = "center" ) {
  
  
  # Triangulate the points
  coords       <-  coordinates(pts.spdf)
  df           <- data.frame(coordinates(pts.spdf))
  W            <- owin(xrange = range(xFromCol(raster)), yrange = range(yFromRow(raster)) )
  triangles.sp <- as(delaunay(as.ppp(df, W = W)), "SpatialPolygons")
  
  edges <- matrix(NA, nrow=length(triangles.sp),ncol=9)
  
  for (k in 1:length(triangles.sp)) {
    
    valid         <- !is.na( over( pts.spdf, triangles.sp[k] ) )
    edges[k,1:3]  <- pts.spdf@data[valid,]
    
    # Generate a random point for this triangle
    if ( mode == "center") {
      rnd.sp        <- coordinates(triangles.sp[k,])
    } else {
      rnd.sp        <- spsample(triangles.sp[k],1,type="random",iter=10)
    }
    
    
    edges[k,4]    <- extract(raster, rnd.sp) # This should be the AnEn
    edges[k,5:6]  <- rowColFromCell(raster, cellFromXY(raster, rnd.sp))
    edges[k,7:8]  <- coordinates(rnd.sp)
    edges[k,9]    <- area( triangles.sp[k] )
  }
  
  df = data.frame(edges)
  colnames(df) = c("V1","V2","V3","PTrue","PRow","PCol","PX","PY","Area")
  
  triangles.spdf = SpatialPolygonsDataFrame(triangles.sp, data = df, match.ID = F)
  
  return(triangles.spdf)
}


evaluate = function( triangles.spdf, na.rm=T ) {
  
  e <- NULL
  
  for ( k in 1:length(triangles.spdf) ) {
    Vavg  <- mean( as.numeric( triangles.spdf@data[k,c('V1','V2','V3')] ), na.rm = na.rm )
    Ptrue <- as.numeric( triangles.spdf@data[k, 'PTrue'])
    e[k]  <- (Vavg - Ptrue)
  }
  
  return(e)
}


sort.mat = function( mat, n, decreasing = F) {
  o = order(mat[,n], decreasing=decreasing)
  return( mat[o,])  
}


select.greedy <- function(triangles.spdf, e, n=100) {
  if ( n >= length(e) || n <= 0 ) {return(triangles.spdf)}
  
  e <- e * triangles.spdf@data[, "Area"]
  
  mat   = cbind(e, 1:length(e))
  
  sm   <- sort.mat(mat, 1, T)
  ret  <- sm[1:n,2]
  
  
  return(triangles.spdf[ret,])
}



select.area <- function(triangles.spdf, e, n=100) {
  if ( n >= length(e) || n <= 0 ) {return(triangles.spdf)}
  
  areas = as.numeric( triangles.spdf@data[,"Area"] )
  mat   = cbind(areas, 1:length(areas))
  
  sm   <- sort.mat(mat, 1, T)
  ret  <- sm[1:n,2]
  
  return(triangles.spdf[ret,])
}

errors <- list()
mat.errors.rnd <- matrix(nrow = repetition, ncol = iterations)
mat.errors.tri <- matrix(nrow= repetition, ncol = iterations)
for (it in 1:repetition) {
  i = 1
  print(paste('repetition #', it, sep = ''))
  
  
  rast.base <- raster(nrows = nrow(rast.obs), ncols = ncol(rast.obs),
                      xmn = 0.5, xmx = ncol(rast.obs) + .5,
                      ymn = 0.5, ymx = nrow(rast.obs) + .5)
  
  if (transparent.plot) {
    plot(rast.obs, col = addalpha(col = gradient.col, alpha), legend = F)
  } else {
    plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
  }
  
  pop.spdf.init           <- generate.inital.population( rast.obs, size, pts.edge )
  
  pop.spdf <- pop.spdf.init
  overall.e.tri <- rep(NA, iterations)
  nums.tri.pts <- rep(NA, iterations)
  save.image('temp_adaptive.rdata')
  
  
  pop.spdf       <- pop.spdf.init
  nums.rnd.pts <- seq(from = size, by = pts.growth, length.out = iterations)
  overall.e.rnd  <- rep(NA, length(nums.rnd.pts))
  
  if (plot.results) {
    
    if (transparent.plot) {
      plot(rast.obs, col = addalpha(col = gradient.col, alpha))
    } else {
      plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
    }
    
    plot(pop.spdf,add=T,pch=19, col = point.col, cex = point.size)
  }
  save.image('temp_random.rdata')
  
  
  
  
  for ( i in 1:iterations) {
    load('temp_adaptive.rdata')
    print(paste('adaptive #', i, sep = ''))
    
    if (output.triangle.plot & plot.results) {
      file <- paste('adaptive_it', str_pad(i, 4, pad = '0'),
                    '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      png(file, width = 12, height = 5, res = 200, units = 'in')
      par(mfrow = c(1, 2), mar = c(0,1,2,4))
      if (transparent.plot) {
        plot(rast.obs, main = 'Adaptive Method',
             col = addalpha(col = gradient.col, alpha), legend = F, box = F, xaxt = 'n', yaxt = 'n')
      } else {
        plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
      }
    }
    
    triangles.spdf     <- triangulate(pop.spdf, rast.obs)
    
    if (plot.results) {
      plot(triangles.spdf,add=T,border=triangle.col, lwd = triangle.width)
    }
    
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n=2)
    overall.e.tri[i] <- sqrt(mean(values(rast.int - rast.obs) ^ 2))
    nums.tri.pts[i] <- length(pop.spdf)
    print(overall.e.tri[i])
    
    sp = SpatialPoints(triangles.spdf@data[,c('PX','PY')])
    # if (plot.results) {
    #   plot(sp,add=T,pch=19, cex = 0.5, col = 'red')
    # }
    e                  <- evaluate( triangles.spdf )
    
    
    #triangles.e.spdf  <- SpatialPolygonsDataFrame(triangles.spdf, data= data.frame(error=e), match.ID = F)
    #spplot(triangles.e.spdf)
    sg                 <- select.greedy(triangles.spdf, abs(e), pts.growth)
    #sg <- tournament.selection(fitness = abs(e)*as.numeric( triangles.spdf@data[,"Area"] ),
    #                            num.samples = pts.growth, tournament.size = 5, num.champions = 1,
    #                            replacement = T)
    # sg <- triangles.spdf[sg, ]
    
    sel.spdf = SpatialPointsDataFrame(sg@data[,c('PX','PY')], data=data.frame(value = sg@data[,c('PTrue')]))
    if (plot.results) {
      plot(sel.spdf,add=T,pch=19, col = point.col, cex = point.size)
    }
    
    coords = rbind(coordinates(pop.spdf), coordinates(sel.spdf))
    values = rbind(pop.spdf@data, sel.spdf@data)
    rownames(values)=NULL
    rownames(coords)=NULL
    
    pop.spdf = SpatialPointsDataFrame(coords, data = data.frame(values))
    
    #if (output.triangle.plot & plot.results) {
    #  dev.off()
    #}
    
    i = i + 1
    save.image('temp_adaptive.rdata')
    load('temp_random.rdata')
    
    print(paste('random #', i, sep = ''))
    
    if (output.triangle.plot & plot.results) {
      file <- paste('random_it', str_pad(i, 4, pad = '0'),
                    '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      #png(file, width = 10, height = 8, res = 100, units = 'in')
      
      if (transparent.plot) {
        plot(rast.obs,  main = 'Random Method', col = addalpha(col = gradient.col, alpha), xaxt = 'n', yaxt = 'n')
      } else {
        plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
      }
      
    }
    
    if (plot.results) {
      triangles.spdf     <- triangulate(pop.spdf, rast.obs)
      plot(triangles.spdf,add=T,border=triangle.col, lwd = triangle.width)
    }
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n=2)
    overall.e.rnd[i] <- sqrt(mean(values(rast.int - rast.obs) ^ 2))
    if (plot.results) {
      print(overall.e.rnd[i])
    }
    
    if (i != length(nums.rnd.pts)) {
      pop.new.spdf = generate.inital.population(rast.obs,
                                                size = (nums.rnd.pts[i+1]-nums.rnd.pts[i]),
                                                pts.edge = 0)
      plot(pop.new.spdf,add=T,pch=19, col = point.col, cex = point.size)
    } 
    pop.spdf <- spRbind(pop.spdf, pop.new.spdf)
    pop.spdf <- remove.duplicates(pop.spdf)
    
    i = i + 1
    save.image('temp_random.rdata')
    if (output.triangle.plot & plot.results) {
      dev.off()
    }
  }
  
  
  # plot(nums.rnd.pts, overall.e.rnd, type = 'l', col = 'red',
  # ylim = range(c(overall.e.rnd, overall.e.tri)))
  # lines(nums.tri.pts, overall.e.tri, lty = 'solid', col = 'blue')
  # lines(nums.tri.pts, overall.e.greedy, lty = 'solid', col = 'purple')
  # legend('topright', legend = c('random', 'tournament directive', 'greedy directive'),
  # col = c('red', 'blue', 'purple'), lty = 1)
  # legend('topright', legend = c('random', 'tournament directive'),
  #        col = c('red', 'blue'), lty = 1)
  
  
  mat.errors.rnd[it, ] <- overall.e.rnd
  mat.errors.tri[it, ] <- overall.e.tri
}

colnames(mat.errors.rnd) <- nums.rnd.pts
colnames(mat.errors.tri) <- nums.rnd.pts

