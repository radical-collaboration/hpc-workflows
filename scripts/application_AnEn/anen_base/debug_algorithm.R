# debug algorithm
library(raster)
library(deldir)
library(spatstat)
library(maptools)
library(prodlim)
library(RAnEnExtra)
library(ggplot2)
library(reshape2)


file.raster.obs <- '~/Desktop/results_new_evaluation_6/obs_raster/time1_flt1.rdata'
load(file.raster.obs)


size <- 30
pts.edge <- 5
pts.growth <- 30
iterations <- 10
repetition <- 30

output.plot <- F
save.plot.data <- T


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
for (it in 1:repetition) {
  print(paste('repetition #', it, sep = ''))
  
  rast.base <- raster(nrows = nrow(rast.obs), ncols = ncol(rast.obs),
                      xmn = 0.5, xmx = ncol(rast.obs) + .5,
                      ymn = 0.5, ymx = nrow(rast.obs) + .5)
  #plot(rast.obs)
  pop.spdf.init           <- generate.inital.population( rast.obs, size, pts.edge )
  
  pop.spdf <- pop.spdf.init
  overall.e <- rep(NA, iterations)
  num.points <- rep(NA, iterations)
  
  for ( i in 1:iterations) {
    print(paste('adaptive #', i, sep = ''))
    
    triangles.spdf     <- triangulate(pop.spdf, rast.obs, 'random')
    
    #plot(triangles.spdf,add=T,border=i)
    
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n=2)
    overall.e[i] <- mean(values(rast.int - rast.obs) ^ 2)
    num.points[i] <- length(pop.spdf)
    #print(overall.e[i])
    
    sp = SpatialPoints(triangles.spdf@data[,c('PX','PY')])
    #plot(sp,add=T,pch=19, cex = 0.5)
    e                  <- evaluate( triangles.spdf )
    
    
    #triangles.e.spdf  <- SpatialPolygonsDataFrame(triangles.spdf, data= data.frame(error=e), match.ID = F)
    #spplot(triangles.e.spdf)
    sg                 <- select.greedy(triangles.spdf, abs(e), pts.growth)
    #sg <- tournament.selection(fitness = abs(e)*as.numeric( triangles.spdf@data[,"Area"] ),
    #                            num.samples = pts.growth, tournament.size = 5, num.champions = 1,
    #                            replacement = T)
    # sg <- triangles.spdf[sg, ]
    
    sel.spdf = SpatialPointsDataFrame(sg@data[,c('PX','PY')], data=data.frame(value = sg@data[,c('PTrue')]))
    #plot(sel.spdf,add=T,pch=19,col="red", cex = 0.5)
    
    coords = rbind(coordinates(pop.spdf), coordinates(sel.spdf))
    values = rbind(pop.spdf@data, sel.spdf@data)
    rownames(values)=NULL
    rownames(coords)=NULL
    
    pop.spdf = SpatialPointsDataFrame(coords, data = data.frame(values))
  }
  
  pop.spdf       <- pop.spdf.init
  nums.rnd.pts <- seq(from = size, by = pts.growth, length.out = iterations)
  overall.e.rnd  <- rep(NA, length(nums.rnd.pts))
  
  
  for ( i in 1:length(nums.rnd.pts)) {
    print(paste('random #', i, sep = ''))
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n=2)
    overall.e.rnd[i] <- mean(values(rast.int - rast.obs) ^ 2)
    #print(overall.e.rnd[i])
    
    if (i != length(nums.rnd.pts)) {
      pop.new.spdf = generate.inital.population(rast.obs,
                                                size = (nums.rnd.pts[i+1]-nums.rnd.pts[i]),
                                                pts.edge = 0)
    } 
    pop.spdf     = spRbind(pop.spdf, pop.new.spdf)
  }
  
  
  #plot(nums.rnd.pts, overall.e.rnd, type = 'l', col = 'red',
       #ylim = range(c(overall.e.rnd, overall.e)))
  #lines(num.points, overall.e, lty = 'solid', col = 'blue')
  # lines(num.points, overall.e.greedy, lty = 'solid', col = 'purple')
  # legend('topright', legend = c('random', 'tournament directive', 'greedy directive'),
  # col = c('red', 'blue', 'purple'), lty = 1)
  legend('topright', legend = c('random', 'tournament directive'),
         col = c('red', 'blue'), lty = 1)
  
  errors <- c(errors, list(nums.rnd.pts, overall.e.rnd,
                           num.points, overall.e))
}


mat.errors.rnd <- matrix(nrow = repetition, ncol = 10)
mat.errors.tri <- matrix(nrow= repetition, ncol = 10)
for ( i in 1:repetition ) {
  mat.errors.rnd[i, ] <- unlist(errors[(i-1)*4 + 2])
  mat.errors.tri[i, ] <- unlist(errors[(i-1)*4 + 4])
}
colnames(mat.errors.rnd) <- nums.rnd.pts
colnames(mat.errors.tri) <- nums.rnd.pts

# plots
combine <- rbind(mat.errors.rnd, mat.errors.tri)
df <- as.data.frame(combine)
method <- c(rep('random method', repetition),
            rep('adaptive method', repetition))
df<-melt(cbind(df, method), id = 'method')
colnames(df) <- c('method', 'pixels', 'error')

range <- range(rbind(mat.errors.rnd, mat.errors.tri))
lower <- floor(range[1])
upper <- ceiling(range[2])

if (output.plot) {
  png('EX_PSU_errors.png', width = 10, height = 8,
      res = 100, units = 'in')
}

p <- ggplot(df, aes(pixels, error, fill=method)) +
  geom_boxplot(outlier.shape = NA) +
  scale_fill_brewer(palette = 'Dark2') +
  coord_cartesian(ylim=c(lower, 103)) +
  theme(legend.justification=c(1,1),
        legend.position=c(1,1),
        text = element_text(size = 25))
p

if (output.plot) {
  dev.off()
}
 
if (save.plot.data) {
  save(df, file = 'error_plot.rdata')
}
