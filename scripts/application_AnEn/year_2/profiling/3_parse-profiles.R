# Parse the log.txt file generated from the bash script profile-AnEn.sh

# Set working directory
setwd('~/github/hpc-workflows/scripts/application_AnEn/year_2/profiling')

# Define the number of cores used to carry out the profiling
num.cores <- c(1, 2, 4, 8, 16)

# Define the number of repetition
search.sizes <- seq(10000, 20000, by = 5000)

# Initialize a list to store all the profiling results
profile <- list()
profile$cpu <- list()
profile$wall <- list()
for (name in names(profile)) {
  profile[[name]]$total <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                  dimnames = list(search.sizes, num.cores))
  profile[[name]]$read <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                 dimnames = list(search.sizes, num.cores))
  profile[[name]]$compute <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                    dimnames = list(search.sizes, num.cores))
  profile[[name]]$sd <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                               dimnames = list(search.sizes, num.cores))
  profile[[name]]$map <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                dimnames = list(search.sizes, num.cores))
  profile[[name]]$sim <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                dimnames = list(search.sizes, num.cores))
  profile[[name]]$select <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                   dimnames = list(search.sizes, num.cores))
  profile[[name]]$write <- matrix(NA, nrow = length(search.sizes), ncol = length(num.cores),
                                  dimnames = list(search.sizes, num.cores))
}

# Read profiling results from log files
for (i.search.size in 1:length(search.sizes)) {
  file <- paste('log_rep-', search.sizes[i.search.size], '.txt', sep = '')
  stopifnot(file.exists(file))
  
  lines <- readLines(file)
  
  # Check whether the correct number of lines are found based on the number of cores used.
  # For each profiling test, 22 lines of output are expected consisting of the CPU and wall time profiling.
  #
  stopifnot(length(num.cores) * 22 == length(lines))
  
  for (i.chunk in 1:length(num.cores)) {
    profile$cpu$total[i.search.size, i.chunk] <- as.numeric(gsub("Total time: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 3]))
    profile$cpu$read[i.search.size, i.chunk] <- as.numeric(gsub("Reading data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 4]))
    profile$cpu$compute[i.search.size, i.chunk] <- as.numeric(gsub("Computation: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 5]))
    profile$cpu$sd[i.search.size, i.chunk] <- as.numeric(gsub(" -- SD: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 6]))
    profile$cpu$map[i.search.size, i.chunk] <- as.numeric(gsub(" -- Mapping: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 7]))
    profile$cpu$sim[i.search.size, i.chunk] <- as.numeric(gsub(" -- Similarity: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 8]))
    profile$cpu$select[i.search.size, i.chunk] <- as.numeric(gsub(" -- Selection: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 9]))
    profile$cpu$write[i.search.size, i.chunk] <- as.numeric(gsub("Writing data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 10]))
    
    profile$wall$total[i.search.size, i.chunk] <- as.numeric(gsub("Total wall time: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 14]))
    profile$wall$read[i.search.size, i.chunk] <- as.numeric(gsub("Reading data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 15]))
    profile$wall$compute[i.search.size, i.chunk] <- as.numeric(gsub("Computation: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 16]))
    profile$wall$sd[i.search.size, i.chunk] <- as.numeric(gsub(" -- SD: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 17]))
    profile$wall$map[i.search.size, i.chunk] <- as.numeric(gsub(" -- Mapping: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 18]))
    profile$wall$sim[i.search.size, i.chunk] <- as.numeric(gsub(" -- Similarity: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 19]))
    profile$wall$select[i.search.size, i.chunk] <- as.numeric(gsub(" -- Selection: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 20]))
    profile$wall$write[i.search.size, i.chunk] <- as.numeric(gsub("Writing data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 21]))
  }
}

# library(grid)
# library(ggplot2)
# library(reshape2)
# require(gridExtra)
library(RColorBrewer)

# Define the name of the variable you want to plot
plot.name <- names(profile$wall)[6]
lwd <- 1.5

# Define the proportion being parallelized
parallel.portion <- .80

pdf('profile.pdf', width = 15, height = 6)

for (plot.name in names(profile$cpu)) {
  
  par(mfrow = c(1, 3))
  
  if (T) {
    # Core plot
    cols <- colorRampPalette(brewer.pal(8, 'Dark2'))(length(search.sizes))
    ylim <- range(unlist(profile$wall[[plot.name]]))
    plot(num.cores, num.cores, type = 'n', ylim = ylim, main = plot.name, 
         xlab = '# of Cores', ylab = 'Time (s)', xaxt = 'n')
    axis(1, at = num.cores, labels = num.cores)
    
    for (i.row in 1:nrow(profile$wall[[plot.name]])) {
      lines(num.cores, profile$wall[[plot.name]][i.row, ],
            col = cols[i.row], lwd = lwd)
    }
    
    legend('topright', legend = search.sizes, col = cols, lwd = lwd)
  }
  
  if (T) {
    # Search size plot
    cols <- colorRampPalette(brewer.pal(8, 'Dark2'))(length(num.cores))
    ylim <- range(unlist(profile$wall[[plot.name]]))
    plot(search.sizes, search.sizes, type = 'n', ylim = ylim, main = plot.name,
         xlab = 'Search Years', ylab = 'Time (s)', xaxt = 'n')
    axis(1, at = search.sizes, labels = search.sizes)
    
    for (i.col in 1:ncol(profile$wall[[plot.name]])) {
      lines(search.sizes, profile$wall[[plot.name]][, i.col],
            col = cols[i.col], lwd = lwd)
    }
    
    legend('topleft', legend = num.cores, col = cols, lwd = lwd)
  }
  
  if (T) {
    # Speed up plot
    amdahl.x <- seq(min(num.cores), max(num.cores), length.out = 1000)
    amdahl.y <- 1 / (1 - parallel.portion + parallel.portion / amdahl.x)
    amdahl <- data.frame(x = amdahl.x, y = amdahl.y, type = 'Amdahl')
    
    mat <- profile$wall[[plot.name]]
    mat <- mat[, 1] / mat

    cols <- colorRampPalette(brewer.pal(8, 'Dark2'))(length(search.sizes))
    ylim <- range(c(mat, amdahl.y))
    plot(num.cores, num.cores, type = 'n', ylim = ylim,
         main = "Comparison with 90% Parallelization",
         xlab = '# of Cores', ylab = 'Speed Up', xaxt = 'n')
    axis(1, at = num.cores, labels = num.cores)
    
    for (i.row in 1:nrow(mat)) {
      lines(num.cores, mat[i.row, ],
            col = cols[i.row], lwd = lwd)
    }
    
    lines(amdahl.x, amdahl.y, lwd = lwd, col = 'red', lty = 'dotted')
    
    legend('topright', legend = search.sizes, col = cols, lwd = lwd)
  }
}

dev.off()

# 
# pdf('profile.pdf', width = 15, height = 8)
# for (plot.name in names(profile$cpu)) {
#   if (T) {
#     melted.cpu <- cbind(melt(profile$cpu[[plot.name]]), 'cpu')[2:4]
#     melted.wall <- cbind(melt(profile$wall[[plot.name]]), 'wall')[2:4]
#     colnames(melted.cpu) <- colnames(melted.wall) <- c('num.cores', 'time', 'type')
#     
#     melted.all <- rbind(melted.cpu, melted.wall)
#     melted.all$type <- as.factor(melted.all$type)
#     melted.all$num.cores <- as.factor(melted.all$num.cores)
#     
#     g1 <- ggplot(melted.all, aes(y = time, x = num.cores)) + 
#       xlab('Number of Cores') + ylab('Time (s)') +
#       geom_boxplot(aes(fill = type), outlier.shape = NA) + 
#       theme(legend.position = 'top', text = element_text(size=18)) +
#       guides(color = guide_legend(title = "Time Type"))
#     
#     # Calculate the theoretical optimum
#     amdahl.x <- seq(min(num.cores), max(num.cores), length.out = 1000)
#     amdahl.y <- 1 / (1 - parallel.portion + parallel.portion / amdahl.x)
#     amdahl <- data.frame(x = amdahl.x, y = amdahl.y, type = 'Amdahl')
#     
#     real.speed.up <- profile$wall[[plot.name]][, 1] / profile$wall[[plot.name]]
#     real.speed.up.mean <- colMeans(real.speed.up)
#     real.speed.up.sd <- apply(real.speed.up, 2, sd)
#     
#     real <- data.frame(x = num.cores, y = real.speed.up.mean, type = 'Real')
#     
#     g2 <- ggplot(rbind(real, amdahl), aes(y = y, x = x, group = type)) + 
#       xlab('Number of Cores') + ylab('Speed Up') +
#       geom_line(aes(linetype = type, color = type), size = 1.2) +
#       geom_errorbar(data = data.frame(
#         x = num.cores, y = real.speed.up.mean,
#         sd = real.speed.up.sd, type = 'Real'),
#         aes(ymin = y - sd, ymax = y + sd), width = .2) +
#       theme(legend.position="top", text = element_text(size=18))
#     
#     grid.arrange(g1, g2, ncol=2, top = textGrob(
#       paste('Profiling for Routine', plot.name), gp = gpar(fontsize = 20,font = 3)))
#   }
#   
# }
# dev.off()
