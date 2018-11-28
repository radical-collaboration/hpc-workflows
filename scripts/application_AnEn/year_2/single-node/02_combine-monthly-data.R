# Convert monthly data to yearly data

##################################
# Combine monthly forecast files #
##################################

# Define common arguments
monthly.data.folder <- '~/ExFat-Hu/Data/NCEI/forecasts_reformat'
yearly.data.folder <- '~/ExFat-Hu/Data/NCEI/forecasts_yearly'
exec <- 'fileReshape'
type <- 'Forecasts'
years <- 2008:2018
verbose <- 3
append <- 2

for (i in 1:length(years)) {
  year <- years[i]
  
  # Define input and output files
  out.file <- paste(yearly.data.folder, '/', year, '.nc', sep = '')
  in.files <- list.files(path = monthly.data.folder, full.names = T,
                         pattern = paste(year, '[[:digit:]]{2}\\.nc', sep = ''))
  
  # Check whether files for 12 months are found
  if (length(in.files) == 12) {
    in.files <- paste(in.files, collapse = ' ')
    
    # Combine monthly files
    command <- paste(exec, '-t', type, '-o', out.file, '-i', in.files, '-a', append, '-v', verbose)
    print(command)
    system(command)
  } else {
    print(paste("Error: Year", year, "does not have 12 monthly files. Skip this year."))
  }
}

##################################
# Combine monthly analysis files #
##################################
# Missing
# Because I did not do it due to the limit of machine memory
#