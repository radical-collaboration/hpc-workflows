/* 
 * File:   Functions.h
 * Author: guido
 *
 * Created on October 1, 2013, 11:55 PM
 */

#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "Array2D.h"
#include "Array4D.h"
#include <vector>

namespace Functions {
    double mean(vector<double> const & rhs);
    double mean(Array2D const & rhs);

    double sd(vector<double> const & rhs);
    double sdCircular(vector<double> const & rhs);
    double computeSdDim3(Array4D const & array, int m, int n, int train_ID_start, int train_ID_end, int p);
    double computeSdDim3(Array4D const & array, int m, int n, std::vector<int> trains_ID, int p);
    double var(vector<double> const & rhs);


    double diffCircular(double, double);
    double swap_endian(double u);



}

#endif /* FUNCTIONS_H */

