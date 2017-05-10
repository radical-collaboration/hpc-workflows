/* 
 * File:   WeimingMethod.h
 * Author: Weiming
 *
 * Created on March 10, 2017, 3:44 PM
 */

#include "WeimingMethod.h"
#include <fstream>

#if defined(_OPENMP)
#include <omp.h>
#endif

WeimingMethod::WeimingMethod() {
}

WeimingMethod::WeimingMethod(const WeimingMethod& orig) {
}

WeimingMethod::~WeimingMethod() {
}

bool
WeimingMethod::fill_search_stations_map_from_file(
        std::map< unsigned int, vector< unsigned int> > &search_stations_map, int max) {
    // This function will read the guide file for station search space
    // and generate a search_stations_map
    //
    std::string path = "SearchSpace.csv";
    std::ifstream spaceFile(path);
    if (spaceFile.fail()) {
        std::cout << "WARNING: SearchSpace.csv may not be found in the current folder." << std::endl
                << "Please provide the full path of SearchSpace.csv" << std::endl;
        getline(std::cin, path);
        spaceFile.open(path);
        if (spaceFile.fail()) {
            std::cout << "WARNING: Still didn't find the file " << path << ". Program terminated." << std::endl;
            return false;
        }
    }

    // parse file
    std::string line;
    std::vector <unsigned int> stations;
    while (std::getline(spaceFile, line)) {
        std::stringstream ss(line);
        std::string i;
        while (std::getline(ss, i, ',')) {
            int i_int = std::stoi(i);
            if (i_int >= max) {
                std::cout << "ERROR: index # " << i_int << " exceeds the number of stations in SearchSpace.csv file." << std::endl;
                return false;
            }
            stations.push_back(i_int);
        }

        std::pair< unsigned int, vector< unsigned int> > p;
        p.first = stations.at(0);
        stations.erase(stations.begin());
        p.second = stations;

        search_stations_map.insert(p);

        stations.clear();
    }

    return true;
}

Array4D
WeimingMethod::compute_analogs(
        const Array4D& forecasts, const Array4D& observations,
        const std::vector<double>& weights,
        int parameter_ID,
        const std::vector<int>& stations_ID,
        unsigned int test_ID_start, unsigned int test_ID_end,
        unsigned int train_ID_start, unsigned int train_ID_end,
        unsigned int members_size,
        int rolling,
        int num_cores,
        bool single_station_search) {

    typedef Array4D::index index;

    index forecasts_parameter_size = forecasts.getSizeDim0();
    index flt_size = forecasts.getSizeDim3();

    // because of the INCLUSIVE range, we need to add 1
    int testing_size = test_ID_end - test_ID_start + 1;

    // sds stores the standard deviation for the metric
    Array2D sds(forecasts_parameter_size, flt_size);

    // the matrix that will keep the values of analog members
    Array4D analogs(stations_ID.size(), testing_size, flt_size, members_size);


    // validate parameters
    if (!validate_parameters(forecasts, observations, weights, parameter_ID, stations_ID, test_ID_start, test_ID_end, train_ID_start, train_ID_end, members_size, rolling)) {
        return (analogs);
    }

    index num_stations_in_forecasts = forecasts.getSizeDim1();
    std::map< unsigned int, vector< unsigned int> > search_stations_map;
    if (!single_station_search) {
        std::cout << "Search space: multiple stations" << std::endl
                << "Read SearchSpace.csv file ... ";
        if (!fill_search_stations_map_from_file(search_stations_map, int(num_stations_in_forecasts))) {
            std::cout << "ERROR: filling search_stations_map failed!" << std::endl;
            return (analogs);
        }
        std::cout << "Done!" << std::endl;
    }

    std::vector<unsigned int> search_stations_ID;

    // start compute analogs
    // 
    // compute the analog for each forecast
    // the result will be combined to form the variable analogs
    //
    for (unsigned int station_ID_index = 0; station_ID_index < stations_ID.size(); station_ID_index++) {
        int station_ID = stations_ID[station_ID_index];

        if (rolling == 0 && single_station_search) {
            // compute standard deviation within one station
            for (index parameter = 0; parameter != forecasts_parameter_size; parameter++) {
                for (index flt = 0; flt != flt_size; flt++) {
                    sds[parameter][flt] = Functions::computeSdDim3(
                            forecasts, parameter, station_ID, train_ID_start, train_ID_end, flt);
                }
            }
        }

        // configure the search stations ID for this station
        //
        if (single_station_search) {
            search_stations_ID.push_back(station_ID);
        } else {
            std::map< unsigned int, vector< unsigned int > >::iterator it = search_stations_map.find(station_ID);
            if (it == search_stations_map.end()) {
                search_stations_ID.push_back(station_ID);
            } else {
                // if this the search space for this station is specified in the map
                // add all the specified stations into the search space
                //
                search_stations_ID = it->second;
            }
        }

        std::cout << "The search space for station #" << station_ID << "\t contains: ";
        for (std::vector <unsigned int>::iterator it_stations = search_stations_ID.begin();
                it_stations != search_stations_ID.end(); it_stations++) {
            std::cout << *it_stations << ',';
        }
        std::cout << std::endl;


#if defined(_OPENMP)
#pragma omp parallel for num_threads(num_cores) shared(analogs) firstprivate(train_ID_end, sds, search_stations_ID)
#endif
        for (int test_ID_index = 0; test_ID_index < testing_size; test_ID_index++) {
            int test_ID = test_ID_index + test_ID_start;

            // if rolling is used, training days will be changing for each test day
            if (rolling < 0) {
                train_ID_end = test_ID + rolling;
                
                if (single_station_search) {

                    // compute sds in each loop because training dataset is changing
                    for (index parameter = 0; parameter != forecasts_parameter_size; parameter++) {
                        for (index flt = 0; flt != flt_size; flt++) {
                            sds[parameter][flt] = Functions::computeSdDim3(
                                    forecasts, parameter, station_ID, train_ID_start, train_ID_end, flt);
                        }
                    }
                }
            }

            for (index time = 0; time < flt_size; time++) {

                // set up the search space for the single forecast
                // the ranges here are INCLUSIVE
                //
                // here, we limit the search space to
                // the same station and the same flt
                //
                int train_start = train_ID_start;
                int train_end = train_ID_end;
                int flt_start = time;
                int flt_end = time;

                // pass a view of the analogs that will be changed
                // after computating the single analog
                //
                typedef boost::multi_array_types::index_range range;
                Array4D::array_view<1>::type analogs_part =
                        analogs[ boost::indices[station_ID_index][test_ID_index][time][range()] ];

                // compute the single analog
                // TODO: views of forecasts and observations
                compute_single_analog(analogs_part, forecasts, observations, sds,
                        station_ID, test_ID, time, parameter_ID, single_station_search,
                        search_stations_ID,
                        train_start, train_end,
                        flt_start, flt_end, weights, members_size);
            }
        }

        search_stations_ID.clear();
    }

    return (analogs);
}

bool
WeimingMethod::compute_single_analog(
        Array4D::array_view<1>::type part_analogs,
        const Array4D& forecasts, const Array4D& observations,
        Array2D& sds,
        unsigned int test_station, unsigned int test_day, unsigned int test_time,
        int observations_parameter_ID,
        bool single_station_search,
        std::vector <unsigned int> const & search_stations_ID,
        unsigned int train_start, unsigned int train_end,
        int flt_start, int flt_end,
        const std::vector<double>& weights,
        unsigned int members_size) {

    typedef Array4D::index index;
    bool valid = false;
    index parameters = forecasts.getSizeDim0();
    index flts = forecasts.getSizeDim3();

    // substring_size is used to create the window when computing the metric
    // 1 means a window of 3 flts, from -1 to 1
    //
    int substring_size = 1;

    multimap<double, vector<index> > metric_map;

    // compute the single analog
    // loop through the search space
    //
    //    for (unsigned int station = test_station; station != test_station + 1; station++) {
    for (std::vector<unsigned int>::const_iterator station_it = search_stations_ID.begin();
            station_it != search_stations_ID.end(); station_it++) {
        unsigned int station = *station_it;

        // if search space is across stations
        // for each station we need to compute sds
        if (!single_station_search) {
            for (index parameter = 0; parameter != parameters; parameter++) {
                for (index flt = 0; flt != flts; flt++) {
                    sds[parameter][flt] = Functions::computeSdDim3(forecasts, parameter, station, train_start, train_end, flt);
                }
            }
        }

        for (int flt = flt_start; flt != flt_end + 1; flt++) {
            for (unsigned int train = train_start; train != train_end + 1; train++) {
                double metric = 0;

                if (train != test_day) {
                    for (index parameter = 0; parameter != parameters; parameter++) {

                        // compute metric between test forecast and the past forecast
                        double forecast = forecasts[parameter][station][train][flt];
                        double observation = observations[observations_parameter_ID][station][train][flt];

                        // make sure that NAN value does not exist
                        if (!std::isnan(forecast) & !std::isnan(observation) & !std::isnan(metric)) {

                            // a window is created to compare the flts
                            int begin_test_time = test_time - substring_size;
                            int end_test_time = test_time + substring_size;
                            int begin_flt = flt - substring_size;
                            int end_flt = flt + substring_size;

                            if (begin_test_time < 0)
                                begin_test_time = 0;
                            if (end_test_time == flts)
                                end_test_time = flts - 1;
                            if (begin_flt < 0)
                                begin_flt = 0;
                            if (end_flt == flts)
                                end_flt = flts - 1;


                            // compute difference between the forecast and this ensemble member
                            vector<double> substring(std::min(end_test_time - begin_test_time + 1,
                                    end_flt - begin_flt + 1));

                            for (int i = begin_test_time, j = begin_flt, index = 0;
                                    i != end_test_time + 1 && j != end_flt + 1;
                                    i++, j++, index++) {
                                double test_value = forecasts[parameter][test_station][test_day][i];
                                double train_value = forecasts[parameter][station][train][j];

                                if (forecasts.isCircular(parameter)) {
                                    substring[index] = pow(Functions::diffCircular(train_value, test_value), 2);
                                } else {
                                    substring[index] = pow(train_value - test_value, 2);
                                }
                            } // end loop of flt window difference

                            double sd = sds[parameter][flt];
                            double mean = Functions::mean(substring);

                            // make sure the standard deviation is not 0
                            if (sd > 0) {
                                metric += weights[parameter] * (sqrt(mean) / sd);
                                valid = true;
                            }
                        } else {
                            // if any one of the forecast, observation, and metric is NAN
                            metric = NAN;
                        }
                    } // end loop of parameters

                    if (valid & !std::isnan(metric)) {
                        vector<index> metric_index = {station, train, flt};
                        metric_map.insert(std::pair< double, vector<index> >(metric, metric_index));

                        if (metric_map.size() > members_size) {
                            metric_map.erase(std::prev(metric_map.end()));
                        }
                    }
                }
            } // end loop of training days
        } // end loop of flts
    } // end loop of stations

    if (valid) {
        multimap<double, vector<index> >::const_iterator map_it = metric_map.begin();
        for (unsigned int i = 0; i != members_size && map_it != metric_map.end(); i++, map_it++) {
            part_analogs[i] = observations[observations_parameter_ID][map_it->second[0]][map_it->second[1]][map_it->second[2]];
        }

        return true;
    } else {
        return false;
    }
}

bool
WeimingMethod::validate_parameters(
        const Array4D& forecasts, const Array4D& observations,
        const std::vector<double>& weights,
        int parameter_ID, const std::vector<int>& stations_ID,
        unsigned int test_ID_start, unsigned int test_ID_end,
        unsigned int train_ID_start, unsigned int train_ID_end,
        unsigned int members_size, int rolling) const {

    if (train_ID_end >= test_ID_start) {
        std::cerr << ("ERROR: The training and testing sets are intersecting.") << std::endl;
        return ( false);
    }

    if (rolling > 0) {
        std::cerr << ("ERROR: Rolling must be zero or negative.") << std::endl;
        return ( false);
    }

    if (train_ID_end - train_ID_start + 1 < members_size) {
        std::cerr << ("ERROR: The number of members is larger than the number of training days.") << std::endl;
        return ( false);
    }

    return true;
}