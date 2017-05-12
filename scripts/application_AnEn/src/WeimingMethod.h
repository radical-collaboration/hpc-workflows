/* 
 * File:   WeimingMethod.h
 * Author: Weiming
 *
 * Created on March 10, 2017, 3:44 PM
 */

#ifndef WEIMINGMETHOD_H
#define WEIMINGMETHOD_H

#include "Array4D.h"
#include "Functions.h"
#include "FileIO.h"
#include "boost/multi_array.hpp"
#include "boost/filesystem.hpp"

#include <map>
#include <vector>
#include <cmath>
#include <string>
#include <sstream>
#include <cstdlib>
#include <iostream>


class WeimingMethod {
public:
    WeimingMethod();
    WeimingMethod(const WeimingMethod & orig);
    virtual ~WeimingMethod();

    Array4D compute_analogs(
            Array4D const & forecasts,
            Array4D const & observations,
            std::vector <double> const & weights, // the weights to use in computations
            int parameter_ID, // the parameter for which we perform the analogs
            std::vector < unsigned int > const & stations_ID, // for which stations should we perform the analogs            
            unsigned int test_ID_start, unsigned int test_ID_end, // the days for which we do the test (verification)
            unsigned int train_ID_start, unsigned int train_ID_end, // the days for which we perform the analogs
            unsigned int members_size = 11, // how many members to keep
            int rolling = 0, // this indicates that the training and testing days are rolling as in an operational sense
            int num_cores = 4,
            bool single_station_search = true);

    bool compute_single_analog(
            Array4D::array_view<1>::type part_analogs, // the forecast to compute analog for
            Array4D const & forecasts, Array4D const & observations,
            Array2D & sds,
            unsigned int station, unsigned int test_day, unsigned int time, // the index to the forecast to compute analog for
            int parameter_ID, // the parameter in the observations for which we perform the analogs
            bool single_station_search, // controls the computation of sds
            std::vector <unsigned int> const & search_stations_ID, // search space for stations
            unsigned int train_start, unsigned int train_end, // training day search range
            int flt_start, int flt_end, // forecast lead time search range
            std::vector <double> const & weights, // the weights to use in computations
            unsigned int members_size); // how many members to keep in the single analog

    bool validate_parameters(
            const Array4D& forecasts, const Array4D& observations,
            const std::vector<double>& weights,
            int parameter_ID,
            const std::vector<unsigned int>& stations_ID,
            unsigned int test_ID_start, unsigned int test_ID_end,
            unsigned int train_ID_start, unsigned int train_ID_end,
            unsigned int members_size = 11,
            int rolling = 0) const;

    bool fill_search_stations_map_from_file(
            std::map< unsigned int, vector< unsigned int> > &search_stations_map,
            int max);
    
    bool replicate_data(unsigned int num_stations, unsigned int num_days);

};

#endif /* WEIMINGMETHOD_H */