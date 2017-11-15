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


#file.raster.obs <- '~/Desktop/results_new_evaluation_6/obs_raster/time1_flt1.rdata'
file.raster.obs <- '~/geolab_storage_V2/data/Analogs/NAM_analysis_raster/time1_flt1.rdata'
load(file.raster.obs)
values(rast.obs) <- values(rast.obs) - 273.15


size <- 30
pts.edge <- 5
pts.growth <- 50
iterations <- 50
repetition <- 10

plot.results <- F
save.plot.data <- T
output.error.plot <- T
output.speedup.plot <- T
output.triangle.plot <- F

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
  print(paste('repetition #', it, sep = ''))
  
  rast.base <- raster(nrows = nrow(rast.obs), ncols = ncol(rast.obs),
                      xmn = 0.5, xmx = ncol(rast.obs) + .5,
                      ymn = 0.5, ymx = nrow(rast.obs) + .5)
  
  plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
  pop.spdf.init           <- generate.inital.population( rast.obs, size, pts.edge )
  
  pop.spdf <- pop.spdf.init
  overall.e.tri <- rep(NA, iterations)
  nums.tri.pts <- rep(NA, iterations)
  
  for ( i in 1:iterations) {
    print(paste('adaptive #', i, sep = ''))
    
    if (output.triangle.plot & plot.results) {
      file <- paste('adaptive_it', str_pad(i, 4, pad = '0'),
                    '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      png(file, width = 10, height = 8, res = 100, units = 'in')
      plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
    }
    
    triangles.spdf     <- triangulate(pop.spdf, rast.obs)
    
    if (plot.results) {
      plot(triangles.spdf,add=T,border='black', lwd = 0.5)
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
      plot(sel.spdf,add=T,pch=19, col = 'green', cex = 0.5)
    }
    
    coords = rbind(coordinates(pop.spdf), coordinates(sel.spdf))
    values = rbind(pop.spdf@data, sel.spdf@data)
    rownames(values)=NULL
    rownames(coords)=NULL
    
    pop.spdf = SpatialPointsDataFrame(coords, data = data.frame(values))
    
    if (output.triangle.plot & plot.results) {
      dev.off()
    }
  }
  
  pop.spdf       <- pop.spdf.init
  nums.rnd.pts <- seq(from = size, by = pts.growth, length.out = iterations)
  overall.e.rnd  <- rep(NA, length(nums.rnd.pts))
  
  if (plot.results) {
    plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
    plot(pop.spdf,add=T,pch=19, col = 'green', cex = 0.5)
  }
  
  for ( i in 1:length(nums.rnd.pts)) {
    print(paste('random #', i, sep = ''))
    
    if (output.triangle.plot & plot.results) {
      file <- paste('random_it', str_pad(i, 4, pad = '0'),
                    '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      png(file, width = 10, height = 8, res = 100, units = 'in')
      plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
    }
    
    if (plot.results) {
      triangles.spdf     <- triangulate(pop.spdf, rast.obs)
      plot(triangles.spdf,add=T,border='black', lwd = 0.5)
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
      plot(pop.new.spdf,add=T,pch=19, col = 'green', cex = 0.5)
    } 
    pop.spdf <- spRbind(pop.spdf, pop.new.spdf)
    pop.spdf <- remove.duplicates(pop.spdf)
    
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

#########
# plots #
#########
# ------------------------------------------------------
# A. error plot
combine <- rbind(mat.errors.rnd, mat.errors.tri)
df <- as.data.frame(combine)
method <- c(rep('random method', repetition),
            rep('adaptive method', repetition))
df<-melt(cbind(df, method), id = 'method')
colnames(df) <- c('method', 'pixels', 'RMSE')

if (save.plot.data) {
  save(df, file = 'error_plot.rdata')
}

range <- range(rbind(mat.errors.rnd, mat.errors.tri))
lower <- range[1] - 0.3
upper <- range[2] + 0.3

if (output.error.plot) {
  png('EX_PSU_errors.png', width = 11, height = 8,
      res = 100, units = 'in')
}

x.ticks <- unique(as.numeric(as.character(df$pixels)))
if (length(original.x.ticks) > x.ticks.display.limit) {
  x.ticks <- x.ticks[floor(seq(from = 1, to = length(x.ticks),
                               length.out = x.ticks.display.limit))]
}

p <- ggplot(df, aes(pixels, RMSE, fill=method)) +
  geom_boxplot(outlier.shape = NA) +
  scale_fill_brewer(palette = 'Dark2') +
  scale_x_discrete(name = '# of points computed',
                   breaks = x.ticks) +
  coord_cartesian(ylim=c(lower, upper)) +
  theme(legend.justification=c(1,1),
        legend.position=c(1,1),
        text = element_text(size = 25),
        plot.margin = margin(.5,.8,0,.1, 'cm'))
p

if (output.error.plot) {
  dev.off()
}

# ------------------------------------------------------
# B. speedup plot

# get average of data
num.powers <- 20
RMSE.sample.size <- 40
xticks.to.show <- 5
selected.ticks <- round(seq(from = 1, to = RMSE.sample.size,
                            length.out = xticks.to.show), digits = 0)
selected.ticks <- unique(selected.ticks)
mat.speedup <- matrix(NA, nrow = repetition, ncol = RMSE.sample.size)
for (it in 1:repetition) {
  RMSE.rnd <- mat.errors.rnd[it, ]
  RMSE.tri <- mat.errors.tri[it, ]
  pixels   <- as.numeric(as.character(colnames(mat.errors.rnd)))
  
  powers <- seq(from = -1, to = -10, length.out = num.powers)
  avg.resids <- sapply(powers, function(power, RMSE) {
    RMSE.power <- RMSE^power
    lm <- lm(pixels ~ RMSE.power)
    return(mean(abs(resid(lm))))
  }, RMSE = RMSE.rnd)
  best.power.rnd <- powers[order(avg.resids)[1]]
  RMSE.power <- RMSE.rnd^best.power.rnd
  lm.rnd <- lm(pixels ~ RMSE.power)
  print(paste("The best average residual for random is",
              avg.resids[order(avg.resids)[1]]))
  print(paste("The best power for random is", best.power.rnd))
  
  # find the best power function to fit
  avg.resids <- sapply(powers, function(power, RMSE) {
    RMSE.power <- RMSE^power
    lm <- lm(pixels ~ RMSE.power)
    return(mean(abs(resid(lm))))
  }, RMSE = RMSE.tri)
  best.power.tri <- powers[order(avg.resids)[1]]
  RMSE.power <- RMSE.tri^best.power.tri
  lm.tri <- lm(pixels ~ RMSE.power)
  print(paste("The best average residual for adaptive is",
              avg.resids[order(avg.resids)[1]]))
  print(paste("The best power for adaptive is", best.power.tri))
  
  plot(RMSE.tri, predict(lm.tri), type = 'l')
  points(RMSE.tri, pixels, pch = 19, cex = 0.5)
  lines(RMSE.rnd, predict(lm.rnd), col = 'red')
  points(RMSE.rnd, pixels, pch = 19, cex = 0.5, col = 'red')
  legend("topright", legend = c("triangulation", "random"),
         col = c('black', 'red'), lty = c('solid', 'solid'))
  
  RMSE.samples <- seq(max(c(range(RMSE.tri)[1], range(RMSE.rnd)[1])),
                      min(c(range(RMSE.tri)[2], range(RMSE.rnd)[2])),
                      length.out = RMSE.sample.size)
  pixels.rnd <- predict(lm.rnd, newdata = data.frame(RMSE.power = RMSE.samples^best.power.rnd))
  pixels.tri <- predict(lm.tri, newdata = data.frame(RMSE.power = RMSE.samples^best.power.tri))
  dif <- pixels.rnd-pixels.tri
  speedup <- dif/pixels.rnd
  
  df <- data.frame(RMSE = RMSE.samples, rate = speedup)
  p <- ggplot(data = df, aes(x = RMSE, y = rate, group = 1)) +
    geom_line() +
    ylab('Speedup Rate') +
    theme(legend.justification=c(1,1),
          legend.position=c(1,1),
          text = element_text(size = 20))
  plot(p)
  
  mat.speedup[it, ] <- speedup
}

if (output.speedup.plot) {
  pdf('EX_PSU_speedup.pdf', width = 10, height = 8)
}

df <- data.frame(mat.speedup)
RMSE.samples <- round(RMSE.samples, digits = 2)
colnames(df) <- as.factor(RMSE.samples)
df <- melt(df)
colnames(df) <- c("RMSE", "rate")

# remove outliers
# outliers are data that don't lie within the range
# (Q1 - 1.5IQR, Q3 + 1.5IQR)
#
Q1 <- quantile(df$rate)[2]
Q3 <- quantile(df$rate)[4]
IQR <- Q3 - Q1
bound.lower <- Q1 - 1.5 * IQR
bound.upper <- Q3 + 1.5 * IQR
df <- df[which((df$rate > bound.lower) & (df$rate < bound.upper)),]

p <- ggplot(df, aes(x = RMSE, y = rate)) +
  geom_boxplot(outlier.shape = NA, na.rm = T) +
  ylab('Speedup Rate') +
  scale_x_discrete(breaks = RMSE.samples[selected.ticks]) +
  theme(legend.justification=c(1,1),
        legend.position=c(1,1),
        text = element_text(size = 20),
        plot.margin = unit(c(.3,.5,.5,.3), "cm"))
p

# plot(error.samples, dif, type = 'l')
# plot(error.samples, speedup, type = 'l')

if (output.speedup.plot) {
  dev.off()
}
