# debug algorithm
library(raster)
library(deldir)
library(spatstat)
library(maptools)
library(RAnEnExtra)
library(RAnEn)
library(ggplot2)
library(reshape2)
library(RColorBrewer)
library(stringr)
library(ncdf4)

#--------------------- Function Definitions ---------------------#
{
  legend.col <- function(col, lev) {
    # add color scale
    opar <- par
    n <- length(col)
    bx <- par("usr")
    
    box.cx <- c(bx[2] + (bx[2] - bx[1]) / 1000,
                bx[2] + (bx[2] - bx[1]) / 1000 + (bx[2] - bx[1]) / 50)
    box.cy <- c(bx[3], bx[3])
    box.sy <- (bx[4] - bx[3]) / n
    
    xx <- rep(box.cx, each = 2)
    
    par(xpd = TRUE)
    for (i in 1:n) {
      yy <- c(
        box.cy[1] + (box.sy * (i - 1)),
        box.cy[1] + (box.sy * (i)),
        box.cy[1] + (box.sy * (i)),
        box.cy[1] + (box.sy * (i - 1))
      )
      polygon(xx, yy, col = col[i], border = col[i])
      
    }
    par(new = TRUE)
    plot(
      0,
      0,
      type = "n",
      ylim = c(min(lev), max(lev)),
      yaxt = "n",
      ylab = "",
      xaxt = "n",
      xlab = "",
      frame.plot = FALSE
    )
    axis(
      side = 4,
      las = 2,
      tick = FALSE,
      line = .25
    )
    par <- opar
  }
  
  addalpha <- function(colors, alpha = 1.0) {
    # apply transparency (alpha) to colors
    #
    r <- col2rgb(colors, alpha = T)
    
    # apply alpha
    r[4, ] <- alpha * 255
    r <- r / 255.0
    
    return(rgb(r[1, ], r[2, ], r[3, ], r[4, ]))
  }
  
  compute.AnEn.on.vertices <-
    function(selected.points, fcts.subset, obs.subset,
             test.ID.start, test.ID.end,
             train.ID.start, train.ID.end,
             members.size, rolling, quick,
             cores, verbose) {
      # compute AnEn for selected points
      #
      dim(obs.subset) = c(1, dim(obs.subset))
      analogs <- rcpp_compute_analogs(
        forecasts = fcts.subset,
        observations = obs.subset,
        weights = rep(1, dim(fcts.subset)[1]),
        stations_ID = selected.points,
        test_ID_start = test.ID.start,
        test_ID_end = test.ID.end,
        train_ID_start = train.ID.start,
        train_ID_end = train.ID.end,
        members_size = members.size,
        observation_ID = 1,
        rolling = rolling,
        quick = quick,
        cores = cores,
        verbose = verbose
      )
      
      # assumption: only one test day
      # assumption: only take the first forecast lead time
      res <- apply(analogs[, , , , 1], c(1, 2), mean)[, 1]
      
      return(res)
    }
  
  generate.inital.population <-
    function(raster, size = 100, pts.edge = 5) {
    # Generate an initial random population
    # the values of the selected points are taken from
    # the raster file
    #
    pop = sampleRandom(raster, size - pts.edge * 4, xy = T)
    
    xs = xFromCol(raster)
    xs.edge = c(xs[1], xs[length(xs)], sample(xs, pts.edge))
    
    ys = yFromRow(raster)
    ys.edge = c(ys[1], ys[length(ys)], sample(ys, pts.edge))
    
    top    = expand.grid(xs.edge, ys.edge[1])
    bottom = expand.grid(xs.edge, ys.edge[2])
    left   = expand.grid(xs.edge[1], ys.edge)
    right  = expand.grid(xs.edge[2], ys.edge)
    
    boundary.sp   = SpatialPoints(rbind(top, bottom, left, right))
    boundary.val  = extract(raster, boundary.sp)
    
    # bind everthing together and remove the duplicates
    pop      = unique(rbind(pop, cbind(
      coordinates(boundary.sp), boundary.val
    )))
    pop.spdf = SpatialPointsDataFrame(
      pop[, 1:2], data = data.frame(value = pop[, 3]))
    
    return(pop.spdf)
  }
  
  triangulate <- function(pts.spdf, raster, mode = "center") {
    # Triangulate the points
    coords       <-  coordinates(pts.spdf)
    df           <- data.frame(coordinates(pts.spdf))
    W            <-
      owin(xrange = range(xFromCol(raster)),
           yrange = range(yFromRow(raster)))
    triangles.sp <-
      as(delaunay(as.ppp(df, W = W)), "SpatialPolygons")
    
    edges <- matrix(NA, nrow = length(triangles.sp), ncol = 9)
    
    for (k in 1:length(triangles.sp)) {
      valid         <- !is.na(over(pts.spdf, triangles.sp[k]))
      edges[k, 1:3]  <- pts.spdf@data[valid,]
      
      # Generate a point for this triangle
      if (mode == "center") {
        rnd.sp <- coordinates(triangles.sp[k,])
      } else {
        rnd.sp <- spsample(triangles.sp[k], 1, type = "random", iter = 10)
      }
      
      edges[k, 4] <- extract(raster, rnd.sp)
      edges[k, 5:6] <- rowColFromCell(raster, cellFromXY(raster, rnd.sp))
      edges[k, 7:8] <- coordinates(rnd.sp)
      edges[k, 9] <- area(triangles.sp[k])
    }
    
    df = data.frame(edges)
    colnames(df) = c("V1", "V2", "V3", "PTrue", "PRow", "PCol", "PX", "PY", "Area")
    triangles.spdf = SpatialPolygonsDataFrame(triangles.sp, data = df, match.ID = F)
    
    return(triangles.spdf)
  }
  
  evaluate <- function(triangles.spdf, na.rm = T) {
    # Evalute triangle errors on the center
    # The predicted value for the center is the average of the valeus of the vertices
    #
    e <- NULL
    
    for (k in 1:length(triangles.spdf)) {
      Vavg  <- mean(as.numeric(
        triangles.spdf@data[k, c('V1', 'V2', 'V3')]), na.rm = na.rm)
      Ptrue <- as.numeric(triangles.spdf@data[k, 'PTrue'])
      e[k]  <- (Vavg - Ptrue)
    }
    
    return(e)
  }
  
  sort.mat <- function(mat, n, decreasing = F) {
    o = order(mat[, n], decreasing = decreasing)
    return(mat[o,])
  }
  
  select.greedy <- function(triangles.spdf, e, n = 100) {
    if (n >= length(e) || n <= 0) {
      return(triangles.spdf)
    }
    
    e <- e * triangles.spdf@data[, "Area"]
    
    mat <- cbind(e, 1:length(e))
    
    sm <- sort.mat(mat, 1, T)
    ret <- sm[1:n, 2]
    
    return(triangles.spdf[ret,])
  }
}
#----------------- End of Function Definitions -----------------#

#----------------------- Parameter Setup -----------------------#
# AnEn parameters
test.ID.start <- 100
test.ID.end <- 100
train.ID.start <- 1
train.ID.end <- 95
members.size <- 10
rolling <- -1
quick <- TRUE
cores <- 4
verbose <- 1

# initial number of points
size <- 30

pts.edge <- 5
pts.growth <- 20

# max iterations of adaptive/random methods
iterations <- 13

# times of repetition of the entire algorithm
# it is used to generate distribution information
repetition <- 1

# visualization
alpha <- .6
col.new.points <- 'green'
x.ticks.display.limit <- 10
gradient.col.raster <- brewer.pal(11, 'Spectral')[11:1]
gradient.col.tri.error <- colorRampPalette(c("grey", "red"))

compute.AnEn <- T
transparent.plot <- T

plot.extra.figures <- F
plot.iteration.results <- T
plot.repetition.figures <- T

save.plot.data <- F
output.error.plot <- F
output.speedup.plot <- F
output.triangle.plot <- F
output.triangle.error.plot <- T

# read the observation data as a raster
if (Sys.info()['login'] == 'wuh20') {
  # files come from Exfat-Hu external harddrive locally
  obs.file.subset <-
    '/Volumes/ExFat-Hu/Data/NAM_processed/small-set/analysis_small-set.nc'
  fcts.file.subset <-
    '/Volumes/ExFat-Hu/Data/NAM_processed/small-set/forecasts_small-set.nc'
} else {
  # files come from Geolab storage V2
  obs.file.subset <-
    '~/geolab_storage_V2/data/Analogs/NAM_subset/analysis_small-set.nc'
  fcts.file.subset <-
    '~/geolab_storage_V2/data/Analogs/NAM_subset/forecasts_small-set.nc'
}

obs.nc.subset <- nc_open(obs.file.subset)
fcts.nc.subset <- nc_open(fcts.file.subset)

obs.subset <- ncvar_get(obs.nc.subset, 'Data') - 273.15
fcts.subset <-
  ncvar_get(fcts.nc.subset, 'Data')[, , , c(1, 3, 5, 7)]

nc_close(obs.nc.subset)
nc_close(fcts.nc.subset)

rast.obs <- raster(
    nrows = 100, ncols = 200,
    xmn = 0.5, xmx = 200 + .5,
    ymn = 0.5, ymx = 100 + .5,
    vals = apply(matrix(
      obs.subset[, test.ID.start, 1], nrow = 100, byrow = T
    ), 2, rev)
  )

errors <- list()
mat.errors.rnd <- matrix(nrow = repetition, ncol = iterations)
mat.errors.tri <- matrix(nrow = repetition, ncol = iterations)
#-------------------- End of Parameter Setup --------------------#

#------------------------ Main Algorithm ------------------------#
for (it in 1:repetition) {
  print(paste('repetition #', it, sep = ''))
  
  rast.base <- raster(
      nrows = nrow(rast.obs), ncols = ncol(rast.obs),
      xmn = 0.5, xmx = ncol(rast.obs) + .5,
      ymn = 0.5, ymx = nrow(rast.obs) + .5,
      resolution = res(rast.obs)
    )
  
  # create initial point population and save it
  # so we can reuse it for initialization for the random method
  # to ensure same initialization for random/adaptive
  pop.spdf.init <-
    generate.inital.population(rast.obs, size, pts.edge)
  if (compute.AnEn) {
    # compute AnEn on the selected points and replace the
    # original values with the AnEn predictions
    #
    selected.points <- xy.to.pixels(
      x = pop.spdf.init@coords[, 1],
      y = pop.spdf.init@coords[, 2],
      xgrids.total = 200,
      start = 1
    )
    pop.spdf.init@data[, 1] <- compute.AnEn.on.vertices(
        selected.points, fcts.subset, obs.subset,
        test.ID.start, test.ID.end,
        train.ID.start, train.ID.end,
        members.size, rolling, quick,
        cores, verbose)
  }
  
  ###################
  # adaptive method #
  ###################
  overall.e.tri <- rep(NA, iterations)
  nums.tri.pts <- rep(NA, iterations)
  pop.spdf <- pop.spdf.init
  
  if (plot.iteration.results) {
    if (transparent.plot) {
      plot(rast.obs, col = addalpha(col = gradient.col.raster, alpha))
    } else {
      plot(rast.obs, col = gradient.col.raster)
    }
    
    plot(pop.spdf, add = T, pch = 19, cex = 0.5,
         col = col.new.points)
  }
  
  for (i in 1:iterations) {
    print(paste('adaptive #', i, sep = ''))
    
    if (output.triangle.plot & plot.iteration.results) {
      file <- paste('adaptive_it', str_pad(i, 4, pad = '0'),
        '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      png(file, width = 10, height = 8, res = 100, units = 'in')
      
      if (transparent.plot) {
        plot(rast.obs, col = addalpha(col = gradient.col, alpha))
      } else {
        plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
      }
    }
    
    triangles.spdf <- triangulate(pop.spdf, rast.obs)
    
    if (plot.iteration.results) {
      plot(triangles.spdf, add = T, border = 'black', lwd = 0.5)
    }
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n = 2)
    
    overall.e.tri[i] <- sqrt(mean(values(rast.int - rast.obs) ^ 2))
    nums.tri.pts[i] <- length(pop.spdf)
    print(overall.e.tri[i])
    
    e <- evaluate(triangles.spdf)
    
    if (output.triangle.error.plot) {
      print("output triangle error plot")
      pdf(file = paste('figures/tri-error_adaptive_repetition_',
                       it, '_iteration_', i, '.pdf', sep = ''),
          width = 17, height = 10)
      triangles.e.spdf  <- SpatialPolygonsDataFrame(
        triangles.spdf, data = data.frame(error = abs(e)), match.ID = F)
      plot(triangles.e.spdf, col = gradient.col.tri.error(length(e)))
      legend.col(gradient.col.tri.error(length(e)), abs(e))
      dev.off()
    }
    
    sg <- select.greedy(triangles.spdf, abs(e), pts.growth)
    #sg <- tournament.selection(fitness = abs(e)*as.numeric( triangles.spdf@data[,"Area"] ),
    #                            num.samples = pts.growth, tournament.size = 5, num.champions = 1,
    #                            replacement = T)
    # sg <- triangles.spdf[sg, ]
    
    sel.spdf = SpatialPointsDataFrame(
      sg@data[, c('PX', 'PY')],
      data = data.frame(value = sg@data[, c('PTrue')]))
    if (plot.iteration.results) {
      plot(sel.spdf, add = T, pch = 19,
           col = col.new.points, cex = 0.5)
    }
    
    coords = rbind(coordinates(pop.spdf), coordinates(sel.spdf))
    values = rbind(pop.spdf@data, sel.spdf@data)
    rownames(values) = NULL
    rownames(coords) = NULL
    
    pop.spdf = SpatialPointsDataFrame(coords, data = data.frame(values))
    
    if (compute.AnEn) {
      selected.points <- xy.to.pixels(
        x = pop.spdf@coords[, 1],
        y = pop.spdf@coords[, 2],
        xgrids.total = 200,
        start = 1
      )
      pop.spdf@data[, 1] <- compute.AnEn.on.vertices(
          selected.points, fcts.subset, obs.subset,
          test.ID.start, test.ID.end,
          train.ID.start, train.ID.end,
          members.size, rolling, quick,
          cores, verbose)
    }
    
    if (output.triangle.plot & plot.iteration.results) {
      dev.off()
    }
  }
  
  #################
  # random method #
  #################
  pop.spdf       <- pop.spdf.init
  overall.e.rnd  <- rep(NA, length(nums.rnd.pts))
  nums.rnd.pts <-
    seq(from = size,
        by = pts.growth,
        length.out = iterations)
  
  if (plot.iteration.results) {
    if (transparent.plot) {
      plot(rast.obs, col = addalpha(col = gradient.col.raster, alpha))
    } else {
      plot(rast.obs, col = gradient.col.raster)
    }
    
    plot(pop.spdf, add = T, pch = 19, cex = 0.5,
         col = col.new.points)
  }
  
  for (i in 1:length(nums.rnd.pts)) {
    print(paste('random #', i, sep = ''))
    
    if (output.triangle.plot & plot.iteration.results) {
      file <- paste('random_it', str_pad(i, 4, pad = '0'),
        '_rep', str_pad(it, 4, pad = '0'), '.png', sep = '')
      png(file, width = 10, height = 8, res = 100, units = 'in')
      
      if (transparent.plot) {
        plot(rast.obs, col = addalpha(col = gradient.col, alpha))
      } else {
        plot(rast.obs, col = brewer.pal(11, 'Spectral')[11:1])
      }
    }
    
    if (plot.iteration.results) {
      triangles.spdf     <- triangulate(pop.spdf, rast.obs)
      plot(triangles.spdf, add = T, border = 'black', lwd = 0.5)
    }
    
    x.computed <- coordinates(pop.spdf)[, 'x']
    y.computed <- coordinates(pop.spdf)[, 'y']
    z <- pop.spdf@data[, 1]
    rast.int <- nni(x.computed, y.computed, z, rast.base, n = 2)
    
    overall.e.rnd[i] <- sqrt(mean(values(rast.int - rast.obs) ^ 2))
    if (plot.iteration.results) {
      print(overall.e.rnd[i])
    }
    
    if (output.triangle.error.plot) {
      print("output triangle error plot for random method")
      triangles.spdf     <- triangulate(pop.spdf, rast.obs)
      e <- evaluate(triangles.spdf)
      pdf(file = paste('figures/tri-error_random_repetition_',
                       it, '_iteration_', i, '.pdf', sep = ''),
          width = 17, height = 10)
      triangles.e.spdf  <- SpatialPolygonsDataFrame(
        triangles.spdf, data = data.frame(error = abs(e)), match.ID = F)
      plot(triangles.e.spdf, col = gradient.col.tri.error(length(e)))
      legend.col(gradient.col.tri.error(length(e)), abs(e))
      dev.off()
    }
    
    if (i != length(nums.rnd.pts)) {
      pop.new.spdf = generate.inital.population(
        rast.obs, pts.edge = 0,
        size = (nums.rnd.pts[i + 1] - nums.rnd.pts[i]))
      plot(pop.new.spdf, add = T, pch = 19, cex = 0.5,
           col = col.new.points)
    }
    pop.spdf <- spRbind(pop.spdf, pop.new.spdf)
    pop.spdf <- remove.duplicates(pop.spdf)
    
    if (compute.AnEn) {
      selected.points <- xy.to.pixels(
        x = pop.spdf@coords[, 1],
        y = pop.spdf@coords[, 2],
        xgrids.total = 200,
        start = 1
      )
      pop.spdf@data[, 1] <- compute.AnEn.on.vertices(
          selected.points, fcts.subset, obs.subset,
          test.ID.start, test.ID.end,
          train.ID.start, train.ID.end,
          members.size, rolling, quick,
          cores, verbose)
    }
    
    if (output.triangle.plot & plot.iteration.results) {
      dev.off()
    }
  }
  
  if (plot.repetition.figures || repetition == 1) {
    plot(nums.rnd.pts, overall.e.rnd,
         type = 'l', col = 'red',
         ylim = range(c(overall.e.rnd, overall.e.tri)))
    lines(nums.tri.pts, overall.e.tri,
          lty = 'solid', col = 'blue')
    legend('topright', col = c('red', 'blue'), lty = 1,
           legend = c('random', 'adaptive'))
  }
  
  mat.errors.rnd[it,] <- overall.e.rnd
  mat.errors.tri[it,] <- overall.e.tri
}

colnames(mat.errors.rnd) <- nums.rnd.pts
colnames(mat.errors.tri) <- nums.rnd.pts
#--------------------- End of Main Algorithm ---------------------#

#--------------------- Extra figures -----------------------------#
if (plot.extra.figures) {
  # A. error distribution plot
  combine <- rbind(mat.errors.rnd, mat.errors.tri)
  df <- as.data.frame(combine)
  method <- c(rep('random method', repetition),
              rep('adaptive method', repetition))
  df <- melt(cbind(df, method), id = 'method')
  colnames(df) <- c('method', 'pixels', 'RMSE')
  
  
  if (save.plot.data) {
    save(df, file = 'error_plot.rdata')
  }
  
  #range <- range(rbind(mat.errors.rnd, mat.errors.tri))
  range <- range(df$RMSE)
  lower <- range[1] - 0.3
  upper <- range[2] + 0.3
  
  if (output.error.plot) {
    png(
      'EX_PSU_errors.png',
      width = 14,
      height = 8,
      res = 200,
      units = 'in'
    )
  }
  
  x.ticks <- unique(as.numeric(as.character(df$pixels)))
  if (length(x.ticks) > x.ticks.display.limit) {
    x.ticks <- x.ticks[floor(seq(
      from = 1,
      to = length(x.ticks),
      length.out = x.ticks.display.limit
    ))]
  }
  
  p <- ggplot(df, aes(pixels, RMSE, fill = method)) +
    geom_boxplot(outlier.shape = NA) +
    scale_fill_brewer(palette = 'Dark2') +
    scale_x_discrete(name = '# of points computed',
                     breaks = x.ticks) +
    coord_cartesian(ylim = c(lower, upper)) +
    theme(
      legend.justification = c(1, 1),
      legend.position = c(1, 1),
      text = element_text(size = 25),
      plot.margin = margin(.5, .8, 0, .1, 'cm')
    )
  p
  
  if (output.error.plot) {
    dev.off()
  }



  # B. speedup distribution plot

  # get average of data
  num.powers <- 20
  RMSE.sample.size <- 40
  xticks.to.show <- 5
  selected.ticks <- round(seq(
    from = 1,
    to = RMSE.sample.size,
    length.out = xticks.to.show
  ),
  digits = 0)
  selected.ticks <- unique(selected.ticks)
  mat.speedup <-
    matrix(NA, nrow = repetition, ncol = RMSE.sample.size)
  for (it in 1:repetition) {
    RMSE.rnd <- mat.errors.rnd[it, ]
    RMSE.tri <- mat.errors.tri[it, ]
    pixels   <- as.numeric(as.character(colnames(mat.errors.rnd)))
    
    powers <- seq(from = -1,
                  to = -10,
                  length.out = num.powers)
    avg.resids <- sapply(powers, function(power, RMSE) {
      RMSE.power <- RMSE ^ power
      lm <- lm(pixels ~ RMSE.power)
      return(mean(abs(resid(lm))))
    }, RMSE = RMSE.rnd)
    best.power.rnd <- powers[order(avg.resids)[1]]
    RMSE.power <- RMSE.rnd ^ best.power.rnd
    lm.rnd <- lm(pixels ~ RMSE.power)
    print(paste("The best average residual for random is",
                avg.resids[order(avg.resids)[1]]))
    print(paste("The best power for random is", best.power.rnd))
    
    # find the best power function to fit
    avg.resids <- sapply(powers, function(power, RMSE) {
      RMSE.power <- RMSE ^ power
      lm <- lm(pixels ~ RMSE.power)
      return(mean(abs(resid(lm))))
    }, RMSE = RMSE.tri)
    best.power.tri <- powers[order(avg.resids)[1]]
    RMSE.power <- RMSE.tri ^ best.power.tri
    lm.tri <- lm(pixels ~ RMSE.power)
    print(paste("The best average residual for adaptive is",
                avg.resids[order(avg.resids)[1]]))
    print(paste("The best power for adaptive is", best.power.tri))
    
    if (plot.regression) {
      plot(RMSE.tri, predict(lm.tri), type = 'l')
      points(RMSE.tri, pixels, pch = 19, cex = 0.5)
      lines(RMSE.rnd, predict(lm.rnd), col = 'red')
      points(RMSE.rnd,
             pixels,
             pch = 19,
             cex = 0.5,
             col = 'red')
      legend(
        "topright",
        legend = c("triangulation", "random"),
        col = c('black', 'red'),
        lty = c('solid', 'solid')
      )
      if (readline() == 'q') {
        stop('Stop the execution!')
      }
    }
    
    RMSE.samples <-
      seq(max(c(range(RMSE.tri)[1], range(RMSE.rnd)[1])),
          #                    min(c(range(RMSE.tri)[2], range(RMSE.rnd)[2])),
          5,
          length.out = RMSE.sample.size)
    pixels.rnd <-
      predict(lm.rnd,
              newdata = data.frame(RMSE.power = RMSE.samples ^ best.power.rnd))
    pixels.tri <-
      predict(lm.tri,
              newdata = data.frame(RMSE.power = RMSE.samples ^ best.power.tri))
    dif <- pixels.rnd - pixels.tri
    speedup <- dif / pixels.rnd
    
    df <- data.frame(RMSE = RMSE.samples, rate = speedup)
    
    if (plot.regression) {
      p <- ggplot(data = df, aes(x = RMSE, y = rate, group = 1)) +
        geom_line() +
        ylab('Speedup Rate') +
        theme(
          legend.justification = c(1, 1),
          legend.position = c(1, 1),
          text = element_text(size = 20)
        )
      plot(p)
      if (readline() == 'q') {
        stop('Stop the execution!')
      }
    }
    mat.speedup[it, ] <- speedup
  }
  
  if (output.speedup.plot) {
    pdf('EX_PSU_speedup.pdf',
        width = 10,
        height = 8)
    
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
  df <-
    df[which((df$rate > bound.lower) & (df$rate < bound.upper)),]
  
  p <- ggplot(df, aes(x = RMSE, y = rate)) +
    geom_boxplot(outlier.shape = NA, na.rm = T) +
    ylab('Speedup Rate') +
    scale_x_discrete(breaks = RMSE.samples[selected.ticks]) +
    theme(
      legend.justification = c(1, 1),
      legend.position = c(1, 1),
      text = element_text(size = 20),
      plot.margin = unit(c(.3, .5, .5, .3), "cm")
    )
  p
  
  # plot(error.samples, dif, type = 'l')
  # plot(error.samples, speedup, type = 'l')
  
  if (output.speedup.plot) {
    dev.off()
  }
}
#--------------------- End of Extra figures ------------------------#