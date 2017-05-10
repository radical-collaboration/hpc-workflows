/* 
 * File:   Ensemble.cpp
 * Author: guido
 * 
 * Created on October 3, 2013, 9:22 PM
 */

#include "Ensemble.h"

#if defined(_OPENMP)
#include <omp.h>
#endif

AnEn::AnEn() {
}

AnEn::AnEn(const AnEn& orig) {
}

AnEn::~AnEn() {
}

Array4D
AnEn::computeAnalogs(Array4D const & forecasts,
        Array4D const & observations,
        std::vector <double> const & weights, // The weights to use in the computations
        int parameter_ID, // The parameter for which we perform the analogs
        std::vector < int > const & stations_ID, // For which stations should we perform the analogs            
        int test_ID_start, int test_ID_end, // the days for which we do the test (verification)
        int train_ID_start, int train_ID_end, // the days for which we perform the analogs
        int members_size, // how many analog members to keep
        int rolling, // This indicates that the training / testing are rolling as in an operational sense
        bool quick, // Use sort of Kth element
        int num_cores) const { // How many cores we want to use

    // We need to add +1 because it is inclusive of the last day of the training 
    //
    int training_size = train_ID_end - train_ID_start + 1;
    int testing_size = test_ID_end - test_ID_start + 1;
    int flt = forecasts.getSizeDim3();
    int forecasts_parameter_size = forecasts.getSizeDim0();

    // This is the substring that is used when computing the metric.  1 means a size of 3, from -1..1
    //
    int substring_size = 1;


    // Stores the standard deviation for the metric
    //
    Array2D sds(forecasts_parameter_size, flt);



    // This is the matrix that will keep the indexes for the results
    //
    Array4D analogs(stations_ID.size(), testing_size, flt, members_size);


    // If the training and testing sets are intersecting, then rolling cannot be true
    //
    if (train_ID_end >= test_ID_start && rolling < 0) {
        std::cerr << ("ERROR: Rolling cannot be true if the training and testing sets are intersecting.") << endl;
        return ( analogs);
    }

    if (rolling > 0) {
        std::cerr << ("ERROR: Rolling must be zero or negative.") << endl;
        return ( analogs);
    }


    if (training_size < members_size) {
        std::cerr << ("ERROR: The number of members is larger than the number of training days.") << endl;
        return ( analogs);
    }


    // Loop through the all the stations
    //

    for (unsigned int station_ID_index = 0; station_ID_index < stations_ID.size(); station_ID_index++) {
        int station_ID = stations_ID[ station_ID_index];



        // XXX For optimization we should compute SDs here, so they are not computed each time in the metric.
        // XXX This makes no difference is rolling is set, as they have to be recomputed anyway

        // Compute the SD for all the training at a specific time.   
        //
        // Note that there might be a discrepancy in the code since the SD is computed
        // for all the training events, including those values that might be removed
        // in the computations because corresponding observations have NaN values
        //

        if (rolling >= 0) {
            computeSds(forecasts, station_ID, train_ID_start, train_ID_end, sds);
        }

        //int init_train_ID_end = 0, init_training_size = 0;
        // Loop through all the testing days
        //
#if defined(_OPENMP)
#pragma omp parallel for num_threads(num_cores) shared(analogs) firstprivate(train_ID_end, training_size, sds)
#endif
        for (int test_ID_index = 0; test_ID_index < testing_size; test_ID_index++) {
            int test_ID = test_ID_index + test_ID_start;

            //std::cout << "Working on Station " << station_ID_index << " from thread #" << omp_get_thread_num() << std::endl;

            // the days for which we perform the analogs
            //
            if (rolling < 0) {
                train_ID_end = test_ID + rolling; // The training are up to the current test ID (remember rolling is always negative)
                training_size = train_ID_end - train_ID_start + 1;

                computeSds(forecasts, station_ID, train_ID_start, train_ID_end, sds);
            }

            // The matrix that computes the error for each measure
            // We are adding + 1 to the flt because the last column will include an index
            // This is to speed up the computations as it will save copying all the data
            //        
            Array2D metric(training_size, flt + 1);

            // Loop for all the FLT
            //
            for (int time = 0; time < flt; time++) {
                int begin_time = time - substring_size;
                int end_time = time + substring_size;

                // Make sure that we do not have only NAN values
                // There can be a problem if all values are NAN
                //
                bool valid = false;


                // Make sure we are within the boundaries
                //
                begin_time = (begin_time < 0) ? 0 : begin_time;
                end_time = (end_time == flt) ? flt - 1 : end_time;

                // Now loop through all the training days
                //
                for (int train_ID_index = 0; train_ID_index < training_size; train_ID_index++) {
                    int train_ID = train_ID_index + train_ID_start;

                    bool ret = computeMetricSingle_(
                            forecasts, observations, weights, sds, parameter_ID,
                            station_ID, train_ID_index, train_ID, test_ID,
                            time, begin_time, end_time, metric);
                    valid = valid | ret;


                } // end loop through training

                // Now we need to sort the results and keep the members_size
                //
                if (valid) {
                    //                    std::cout << metric << endl;

                    if (quick) {
                        // find the least n elements, and put them in the front
                        // ATTENTION: the least n elements are not sorted
                        nth_element(metric.begin(), metric.begin() + members_size, metric.end(), Array2DCompare(time));
                    } else {
                        //partial_sort(metric.begin(), metric.begin() + members_size, metric.end(), Array2DCompare(time));
                        sort(metric.begin(), metric.end(), Array2DCompare(time));
                    }
                    //                    cout << "Sorted" << endl;
                    //                    std::cout << metric << endl;
                    // store the best members after they have been sorted
                    //
                    for (int metric_index = 0; metric_index < members_size; metric_index++) {

                        // the flt corresponds to the sorted indexes (the last column in the array)
                        // It is safe to cast into an int, because the last value is always an integer
                        // We need to add the train_ID_start because the indexes are relative to this
                        //
                        int observation_index = (int) metric[metric_index][flt] + train_ID_start;

                        double observation = observations[parameter_ID][station_ID][observation_index][time];
                        //double observation = observations[parameter_ID][station_ID][observation_index * flt + time,1];

                        //cout << metric_index << " " << metric[metric_index][flt] << " " << observation << endl;
                        // Assign the analog value corresponding to this metric index
                        //
                        analogs[station_ID_index][test_ID_index][time][metric_index] = observation;
                    }
                } else { // If there are only NANs, set the analogs as all NAN
                    for (int metric_index = 0; metric_index < members_size; metric_index++) {
                        analogs[station_ID_index][test_ID_index][time][metric_index] = NAN;
                    }
                }

            } // end loop through the flt
        } // end loop testing days
    } // end loop stations
    return (analogs);
}



// This method computes the metric for a single train/test day combination
//

bool
AnEn::computeMetricSingle_(
        Array4D const & forecasts,
        Array4D const & observations,
        std::vector <double> const & weights,
        Array2D const & sds,
        unsigned int const & parameter_ID,
        unsigned int const & station_ID,
        unsigned int const & train_ID_index,
        unsigned int const & train_ID,
        unsigned int const & test_ID,
        unsigned int const & time,
        unsigned int const & begin_time,
        unsigned int const & end_time,
        Array2D & metric) const {


    // This ensure that the metric was properly computed for this location
    //
    bool valid = false;

    int flt = forecasts.getSizeDim3();

    // Do not compute if the training and testing are the same
    //
    if (train_ID != test_ID) {

        // The size of the substring of the analogs
        //
        int size = end_time - begin_time + 1;
        int forecasts_parameter_size = forecasts.getSizeDim0();


        // This is the substring for the analogs
        //
        vector<double> window(size);


        // Get the data for this prediction
        //
        double observation = observations[parameter_ID][station_ID][train_ID][time];

        // Loop through all the parameters
        //
        for (int parameter = 0; parameter < forecasts_parameter_size; parameter++) {

            // Get the data for this prediction
            //                            
            double forecast = forecasts[parameter][station_ID][train_ID][time];

            // Make sure that we have a good corresponding value in the
            // observations, otherwise skip the computation of the metric
            //                  
            // Also make sure that the no forecasts had NAN values
            // The analog can be NAN if the forecasts were missing for any other parameter
            //
            if (!isnan(observation) & !isnan(forecast) & !isnan(metric[train_ID_index][time])) {

                // compute the difference between the forecast and this ensemble member
                //
                for (unsigned int i = begin_time, index = 0; i <= end_time; i++, index++) {

                    double train_value = forecasts[parameter][station_ID][train_ID][i];
                    double test_value = forecasts[parameter][station_ID][test_ID][i];

                    // check if we need to do a circular difference
                    //
                    if (forecasts.isCircular(parameter)) {
                        window[index] = pow(Functions::diffCircular(train_value, test_value), 2);
                    } else {
                        window[index] = pow(train_value - test_value, 2);
                    }

                } // end loop through the substring

                double sd = sds[parameter][time];
                double mean = Functions::mean(window);



                // Make sure that the standard deviation is not zero
                //
                if (sd > 0) {
                    // assign the value
                    //
                    metric[train_ID_index][time] += weights[parameter] * ((sqrt(mean) / sd));
                    //std::cout << time <<  " " << train_ID_index << " " << parameter << " " << sd << " " << mean << " " << metric[train_ID_index][time] << endl;
                    valid = true;
                }

            } else { // this means that the corresponding observation or forecast has a NaN value
                metric[train_ID_index][time] = NAN;
                return false;
            }
        } // end loop through parameters]

    } else { // make sure the train_ID and test_ID are different
        // Set to no value for all the flt
        //
        //fill(metric[train_ID_index].begin(), metric[train_ID_index].end(), NAN);
        metric[train_ID_index][time] = NAN;
        return false;
    } // Make sure there is a valid observation

    metric[train_ID_index][flt] = train_ID_index;

    return valid;
}

bool AnEn::computeSds(
        Array4D const & forecasts,
        unsigned int const & station_ID,
        unsigned int const & train_ID_start,
        unsigned int const & train_ID_end,
        Array2D & sds) const {

    int flt = forecasts.getSizeDim3();
    int forecasts_parameter_size = forecasts.getSizeDim0();

    for (int parameter = 0; parameter < forecasts_parameter_size; parameter++) {
        for (int time = 0; time < flt; time++) {
            sds[parameter][time] = Functions::computeSdDim3(forecasts, parameter, station_ID, train_ID_start, train_ID_end, time);
        }
    }

    return true;
}