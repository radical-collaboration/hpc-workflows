/* 
 * File:   LucaMethod.h
 * Author: guido
 *
 * Created on October 4, 2013, 12:15 AM
 */

#ifndef LUCAMETHOD_H
#define LUCAMETHOD_H

#include "Array4D.h"
#include "Functions.h"


// This is a generic class for the analog ensemble. 
// It contains pure virtual methods that must be overwritten in child classes.
//

class Ensemble {
    virtual Array4D computeAnalogs(
            Array4D const & forecasts,
            Array4D const & observations,
            std::vector <double> const & weights, // The weights to use in the computations
            int parameter_ID, // The parameter for which we perform the analogs
            std::vector < int > const & stations_ID, // For which stations should we perform the analogs            
            int test_ID_start, int test_ID_end, // the days for which we do the test (verification)
            int train_ID_start, int train_ID_end, // the days for which we perform the analogs
            int members_size = 100, // how many members to keep
            int rolling = 0, // This indicates that the training / testing are rolling as in an operational sense
            bool quick = true, // Use sort of Kth element
            int num_cores = 2) const = 0;
};

class AnEn : public Ensemble {
public:
    AnEn();
    AnEn(const AnEn& orig);
    virtual ~AnEn();

    //    Array2D computeMetricLuca(Array4D const & forecasts, Array4D const & observations, std::vector<double> const & weights,
    //            int parameter_ID, int station_ID, int test_ID, int train_ID_start, int train_ID_end) const;

    Array4D computeAnalogs(Array4D const & forecasts,
            Array4D const & observations,
            std::vector <double> const & weights, // The weights to use in the computations
            int parameter_ID, // The parameter for which we perform the analogs
            std::vector < int > const & stations_ID, // For which stations should we perform the analogs            
            int test_ID_start, int test_ID_end, // the days for which we do the test (verification)
            int train_ID_start, int train_ID_end, // the days for which we perform the analogs
            int members_size = 100, // how many members to keep
            int rolling = 0, // This indicates that the training / testing are rolling as in an operational sense
            bool quick = true,
            int num_cores = 2) const; // Use sort of Kth element

protected:
    bool computeMetricSingle_(
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
            Array2D & metric) const;

    bool computeSds(
            Array4D const & forecasts,
            unsigned int const & station_ID,
            unsigned int const & train_ID_start,
            unsigned int const & train_ID_end,
            Array2D & sds) const;
    
};

#endif /* LUCAMETHOD_H */

