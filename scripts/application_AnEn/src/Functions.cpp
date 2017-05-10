/* 
 * File:   Functions.cpp
 * Author: guido
 * 
 * Created on October 1, 2013, 11:55 PM
 */

#include "Functions.h"
#include "Array2D.h"


using namespace std;

// Disregard NAN values when computing the mean
//

double
Functions::mean(vector<double> const & rhs) {

    double sum = 0.0;
    int valid = 0;

    for (unsigned int i = 0; i < rhs.size(); i++) {
        if (!std::isnan(rhs[i])) {
            sum += rhs[i];
            valid++;
        }
    }

    // Added on 2.1.2014.  If there are only NAN values, then return NAN
    //
    if (valid == 0) return NAN;

    return sum / (double) valid;
}

double
Functions::mean(Array2D const & rhs) {

    double sum = 0.0;
    int valid = 0;

    int M = rhs.sizeM();
    int N = rhs.sizeN();


    for (int m = 0; m < M; m++) {
        for (int n = 0; n < N; n++) {
            if (!std::isnan(rhs[m][n])) {
                sum += rhs[m][n];
                valid++;
            }
        }
    }
    return sum / (double) valid;
}

double
Functions::sd(vector<double> const & rhs) {
    double var = Functions::var(rhs);
    double sd = sqrt(var);
    return (sd);
}

double
Functions::sdCircular(vector<double> const & rhs) {

    //double val = Math.PI / 180.0;
    // This is to convert from degrees to radians
    //
    double val = 0.01745329;
    double b = 0.1547;

    vector<double> dirRad(rhs.size());
    vector<double> sins(rhs.size());
    vector<double> coss(rhs.size());

    for (unsigned int i = 0; i < rhs.size(); i++) {

        // This is to convert from degrees to radians
        //
        dirRad[i] = rhs[i] * val;

        sins[i] = sin(dirRad[i]);
        coss[i] = cos(dirRad[i]);
    }

    double s = mean(sins);
    double c = mean(coss);

    // Yamartino estimator
    //
    double e = sqrt(1.0 - (pow(s, 2.0) + pow(c, 2.0)));
    double asine = asin(e);
    double ex3 = pow(e, 3);

    double q = asine * (1 + b * ex3);

    // Convert back to degrees
    //
    return (q / val);
}

double
Functions::var(vector<double> const & rhs) {

    double mean = Functions::mean(rhs);
    double sum = 0.0;

    int valid = 0;

    for (unsigned int i = 0; i < rhs.size(); i++) {

        if (!std::isnan(rhs[i])) {
            sum += pow(rhs[i] - mean, 2);
            valid++;
        }
    }
    return sum / ((double) valid - 1.0);
}

double
Functions::diffCircular(double dir1, double dir2) {

    double res1 = abs(dir1 - dir2);
    double res2 = abs(res1 - 360);

    return ( min(res1, res2));
}

double Functions::swap_endian(double u) {

    union {
        double u;
        unsigned char u8[sizeof (double)];
    } source, dest;

    source.u = u;

    for (size_t k = 0; k < sizeof (double); k++)
        dest.u8[k] = source.u8[sizeof (double) -k - 1];

    return dest.u;
}

double
Functions::computeSdDim3(Array4D const & array, int m, int n, int train_ID_start, int train_ID_end, int p) {

    bool isCircular = array.isCircular(m);
    double res = 0.0;

    int training_size = train_ID_end - train_ID_start + 1;

    vector<double> values(training_size);


    for (int i = 0, train_ID_index = train_ID_start;
            i < training_size;
            i++, train_ID_index++) {
        values[i] = array[ m ][ n ][ train_ID_index ][ p ];
    }



    if (isCircular == true) {
        res = Functions::sdCircular(values);
    } else {
        res = Functions::sd(values);
    }

    return ( res);
}

double
Functions::computeSdDim3(Array4D const & array, int m, int n, std::vector<int> trains_ID, int p) {

    bool isCircular = array.isCircular(m);
    double res = 0.0;

    int training_size = trains_ID.size();

    vector<double> values(training_size);

    std::vector<int>::iterator trains_it = trains_ID.begin();
    for (int i = 0; i < training_size; i++, trains_it++) {
        values[i] = array[ m ][ n ][ *trains_it ][ p ];
    }

    if (isCircular == true) {
        res = Functions::sdCircular(values);
    } else {
        res = Functions::sd(values);
    }

    return ( res);
}
