/* 
 * File:   Matrix2D.cpp
 * Author: guido
 * 
 * Created on October 1, 2013, 9:00 AM
 */

#include "Array2D.h"
#include <iostream>
#include <cmath>
#include <cstdlib>
#include <ctime>

using namespace std;

Array2D::Array2D() {
    //cout << "Array2D Constructor: Default" << endl;
}

Array2D::Array2D(int d1, int d2) {

    //cout << "Array2D Constructor: With Dimensions" << endl;
    //resize(boost::extents[d1][d2]);
    resize(d1);

    vector< vector < double > >::iterator iter;

    for (iter = begin(); iter < end(); iter++) {
        iter->resize(d2, 0.0);
    }

}

Array2D::Array2D(Array2D const & rhs) {
    //cout << "Array2D Constructor: Copy" << endl;

    //resize(boost::extents
    //        [rhs.shape()[0]]
    //        [rhs.shape()[1]]);

    *this = rhs;
}

Array2D::~Array2D() {
    //cout << "Array2D Destructor" << endl;
}

void
Array2D::randomize() {

    int M = sizeM();
    int N = sizeN();

    for (int m = 0; m < M; m++) {
        for (int n = 0; n < N; n++) {
            // drand48() is not an actual function in newer version of gcc
            //(*this)[m][n] = drand48();
            std::srand(std::time(0));
            (*this)[m][n] = std::rand();
        }
    }
}

double
Array2D::sizeM() const {
    // return( shape()[0] );
    return ( size());
}

double
Array2D::sizeN() const {
    // return( shape()[1] );
    return ( begin()->size());
}

void
Array2D::print_size(ostream & os) const {

    int M = sizeM();
    int N = sizeN();

    os << "["
            << M << ", "
            << N << "]"
            << endl;
}

void
Array2D::print(ostream & os) const {

    os << "Array Shape = ";
    os << "[ " << sizeM() << " ][ " << sizeN() << " ]" << endl;

    os << endl;

    int M = sizeM();
    int N = sizeN();

    for (int m = 0; m < M; m++) {
        for (int n = 0; n < N; n++) {
            os << (*this)[m][n] << "\t";
        }
        os << endl;
    }
}

void
Array2D::print_dim(ostream & os, int m) const {

    int N = sizeN();

    for (int n = 0; n < N; n++) {
        os << (*this)[m][n] << "\t";
    }
    os << endl;
}

ostream &
operator<<(ostream & os, Array2D const & bv) {

    bv.print(os);

    return os;
}

Array2DCompare::Array2DCompare(int column)
: m_column_(column) {
}


bool
Array2DCompare::operator()(vector <double> const& lhs,
        vector <double> const& rhs) {

    if (isnan(lhs[m_column_])) return false;
    if (isnan(rhs[m_column_])) return true;

    return lhs[m_column_] < rhs[m_column_];
}