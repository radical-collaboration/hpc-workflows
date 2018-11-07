# Parse the log.txt file generated from the bash script profile-AnEn.sh

# Set working directory
setwd('~/github/hpc-workflows/scripts/application_AnEn/year_2/profiling')

# Define the number of cores used to carry out the profiling
num.cores <- c(1, 2, 4, 8, 16)

# Define the number of repetition
num.repetition <- 5

# Initialize a list to store all the profiling results
profile <- list()
profile$cpu <- list()
profile$wall <- list()
for (name in names(profile)) {
  profile[[name]]$total <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$read <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$compute <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$sd <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$map <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$sim <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$select <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
  profile[[name]]$write <- matrix(NA, nrow = num.repetition, ncol = length(num.cores))
}

# Read profiling results from log files
for (i.rep in 1:num.repetition) {
  file <- paste('log_rep-', i.rep, '.txt', sep = '')
  stopifnot(file.exists(file))
  
  lines <- readLines(file)
  
  # Check whether the correct number of lines are found based on the number of cores used.
  # For each profiling test, 22 lines of output are expected consisting of the CPU and wall time profiling.
  #
  stopifnot(length(num.cores) * 22 == length(lines))
  
  for (i.chunk in 1:length(num.cores)) {
    profile$cpu$total[i.rep, i.chunk] <- as.numeric(gsub("Total time: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 3]))
    profile$cpu$read[i.rep, i.chunk] <- as.numeric(gsub("Reading data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 4]))
    profile$cpu$compute[i.rep, i.chunk] <- as.numeric(gsub("Computation: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 5]))
    profile$cpu$sd[i.rep, i.chunk] <- as.numeric(gsub(" -- SD: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 6]))
    profile$cpu$map[i.rep, i.chunk] <- as.numeric(gsub(" -- Mapping: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 7]))
    profile$cpu$sim[i.rep, i.chunk] <- as.numeric(gsub(" -- Similarity: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 8]))
    profile$cpu$select[i.rep, i.chunk] <- as.numeric(gsub(" -- Selection: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 9]))
    profile$cpu$write[i.rep, i.chunk] <- as.numeric(gsub("Writing data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 10]))
    
    profile$wall$total[i.rep, i.chunk] <- as.numeric(gsub("Total wall time: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 14]))
    profile$wall$read[i.rep, i.chunk] <- as.numeric(gsub("Reading data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 15]))
    profile$wall$compute[i.rep, i.chunk] <- as.numeric(gsub("Computation: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 16]))
    profile$wall$sd[i.rep, i.chunk] <- as.numeric(gsub(" -- SD: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 17]))
    profile$wall$map[i.rep, i.chunk] <- as.numeric(gsub(" -- Mapping: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 18]))
    profile$wall$sim[i.rep, i.chunk] <- as.numeric(gsub(" -- Similarity: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 19]))
    profile$wall$select[i.rep, i.chunk] <- as.numeric(gsub(" -- Selection: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 20]))
    profile$wall$write[i.rep, i.chunk] <- as.numeric(gsub("Writing data: (.+?) seconds.*?$", "\\1", lines[(i.chunk-1) * 22 + 21]))
  }
}

library(grid)
library(ggplot2)
library(reshape2)
require(gridExtra)
library(RColorBrewer)

# Define the name of the variable you want to plot
plot.name <- names(profile$cpu)[1]

# Define the proportion being parallelized
parallel.portion <- .90

pdf('profile.pdf', width = 15, height = 8)
for (plot.name in names(profile$cpu)) {
  if (T) {
    melted.cpu <- cbind(melt(profile$cpu[[plot.name]]), 'cpu')[2:4]
    melted.wall <- cbind(melt(profile$wall[[plot.name]]), 'wall')[2:4]
    colnames(melted.cpu) <- colnames(melted.wall) <- c('num.cores', 'time', 'type')
    
    melted.all <- rbind(melted.cpu, melted.wall)
    melted.all$type <- as.factor(melted.all$type)
    melted.all$num.cores <- as.factor(melted.all$num.cores)
    
    g1 <- ggplot(melted.all, aes(y = time, x = num.cores)) + 
      xlab('Number of Cores') + ylab('Time (s)') +
      geom_boxplot(aes(fill = type), outlier.shape = NA) + 
      theme(legend.position = 'top', text = element_text(size=18)) +
      guides(color = guide_legend(title = "Time Type"))
    
    # Calculate the theoretical optimum
    amdahl.x <- seq(min(num.cores), max(num.cores), length.out = 1000)
    amdahl.y <- 1 / (1 - parallel.portion + parallel.portion / amdahl.x)
    amdahl <- data.frame(x = amdahl.x, y = amdahl.y, type = 'Amdahl')
    
    real.speed.up <- profile$wall[[plot.name]][, 1] / profile$wall[[plot.name]]
    real.speed.up.mean <- colMeans(real.speed.up)
    real.speed.up.sd <- apply(real.speed.up, 2, sd)
    
    real <- data.frame(x = num.cores, y = real.speed.up.mean, type = 'Real')
    
    g2 <- ggplot(rbind(real, amdahl), aes(y = y, x = x, group = type)) + 
      xlab('Number of Cores') + ylab('Speed Up') +
      geom_line(aes(linetype = type, color = type), size = 1.2) +
      geom_errorbar(data = data.frame(
        x = num.cores, y = real.speed.up.mean,
        sd = real.speed.up.sd, type = 'Real'),
        aes(ymin = y - sd, ymax = y + sd), width = .2) +
      theme(legend.position="top", text = element_text(size=18))
    
    grid.arrange(g1, g2, ncol=2, top = textGrob(
      paste('Profiling for Routine', plot.name), gp = gpar(fontsize = 20,font = 3)))
  }
  
}
dev.off()
