# Generate test data
library(ncdf4)

out.forecasts <- 'syn_forecasts.nc'
out.observations <- 'syn_observations.nc'

num.parameters <- 10
num.stations <- 1
num.times.forecasts <- 1000 * 365
num.flts <- 1
num.times.observations <- num.times.forecasts * num.flts

dim.chars <- ncdim_def("num_chars", "", 1:50, create_dimvar = F)
dim.parameters <- ncdim_def("num_parameters", "", 1:num.parameters, create_dimvar = F)
dim.stations <- ncdim_def("num_stations", "", 1:num.stations, create_dimvar = F)
dim.times.forecasts <- ncdim_def("num_times", "", 1:num.times.forecasts, create_dimvar = F)
dim.flts <- ncdim_def("num_flts", "", 1:num.flts, create_dimvar = F)
dim.times.observations <- ncdim_def("num_times", "", 1:num.times.observations, create_dimvar = F)

var.parameter.names <- ncvar_def("ParameterNames", "char", list(dim.chars, dim.parameters), prec = 'char')
var.station.names <- ncvar_def("StationNames", "char", list(dim.chars, dim.stations), prec = 'char')

var.data.forecasts <- ncvar_def("Data","double", list(
  dim.parameters, dim.stations, dim.times.forecasts, dim.flts
), NaN, "Data", prec = "double")

var.times.forecasts <- ncvar_def("Times", "double", list(dim.times.forecasts), NaN, prec = "double")
var.flts <- ncvar_def("FLTs", "double", list(dim.flts), NaN, prec = "double")

var.data.observations <- ncvar_def("Data","double", list(
  dim.parameters, dim.stations, dim.times.observations
), NaN, "Data", prec = "double")

var.times.observations <- ncvar_def("Times", "double", list(dim.times.observations), NaN, prec = "double")

unlink(out.forecasts)
unlink(out.observations)

# Synthesized forecast data
data <- array(NA, dim = c(num.parameters, num.stations, num.times.forecasts, num.flts))
for (i in 1:num.parameters) {
  data[i, , , ] <- runif(num.stations * num.times.forecasts * num.flts) * 10 ^ i
}

times <- (1:num.times.forecasts) * 100
flts <- 1:num.flts

nc.forecasts <- nc_create(out.forecasts, list(
  var.station.names, var.parameter.names, var.data.forecasts, var.flts, var.times.forecasts), force_v4 = T)
ncvar_put(nc.forecasts, var.data.forecasts, data)
ncvar_put(nc.forecasts, var.parameter.names, paste('parameter_', 1:num.parameters, sep = ''))
ncvar_put(nc.forecasts, var.station.names, paste('stations_', 1:num.stations, sep = ''))
ncvar_put(nc.forecasts, var.times.forecasts, times)
ncvar_put(nc.forecasts, var.flts, flts)
nc_close(nc.forecasts)


# Synthesized data
data <- array(NA, dim = c(num.parameters, num.stations, num.times.observations))
for (i in 1:num.parameters) {
  data[i, , ] <- runif(num.stations * num.times.observations) * 10 ^ i
}

times <- rep(times, each = length(flts)) + flts

nc.observations <- nc_create(out.observations, list(
  var.station.names, var.parameter.names, var.data.observations, var.times.observations), force_v4 = T)
ncvar_put(nc.observations, var.parameter.names, paste('parameter_', 1:num.parameters, sep = ''))
ncvar_put(nc.observations, var.station.names, paste('stations_', 1:num.stations, sep = ''))
ncvar_put(nc.observations, var.data.observations, data)
ncvar_put(nc.observations, var.times.observations, times)
nc_close(nc.observations)
