/* 
 * File:   Matrix4D.cpp
 * Author: guido
 * 
 * Created on October 1, 2013, 9:00 AM
 */

#include "Array4D.h"
#include "Functions.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <cstdlib>
#include <ctime>


using namespace std;

Array4D::Array4D() {
    //cout << "Array4D Constructor: Default" << endl;
}

Array4D::Array4D(int d1, int d2, int d3, int d4) {

    //cout << "Array4D Constructor: With Dimensions" << endl;
    resize(boost::extents[d1][d2][d3][d4]);

    circular_.resize(d1, false);
}

Array4D::Array4D(Array4D const & rhs) {
    *this = rhs;
}

Array4D & Array4D::operator=(const Array4D &rhs) {

    if (this != &rhs) {
        resize(boost::extents
                [rhs.shape()[0]]
                [rhs.shape()[1]]
                [rhs.shape()[2]]
                [rhs.shape()[3]]);

        *this = rhs;

        circular_ = rhs.circular_;
    }

    return *this;
}

Array4D::Array4D(vector<double> const & data, int M, int N, int O, int P) {
    //cout << "Array4D Constructor: From vector data" << endl;

    // Resize the current array
    //
    resize(boost::extents[M][N][O][P]);

    int m = 0;
    int n = 0;
    int o = 0;
    int p = 0;

    vector<double>::const_iterator citer;

    for (citer = data.begin();
            citer != data.end();
            citer++) {
        if (m == M) {
            m = 0;
            n++;
            if (n == N) {
                n = 0;
                o++;
                if (o == O) {
                    o = 0;
                    p++;
                }
            }
        }
        (*this)[m][n][o][p] = *citer;
        m++;
    }

    circular_.resize(M, false);

}

Array4D::~Array4D() {
    //cout << "Array4D Destructor" << endl;
}

bool
Array4D::myresize(int d1, int d2, int d3, int d4) {
    resize(boost::extents[d1][d2][d3][d4]);
    circular_.resize(d1, false);
    return ( true);
}

void
Array4D::setFirstDimension(vector<double> const & data, int pos) {
    int m = pos;
    int n = 0;
    int o = 0;
    int p = 0;

    int N = shape()[1];
    int O = shape()[2];

    vector<double>::const_iterator citer;

    for (citer = data.begin();
            citer != data.end();
            citer++) {
        if (n == N) {
            n = 0;
            o++;
            if (o == O) {
                o = 0;
                p++;
            }
        }

        (*this)[m][n][o][p] = *citer;
        n++;
    }
}




// This is just a very fast way to read a matrix from a file.  It basically 
// includes the code in FileIO to read a binary files, and instead of creating
// a vector and then assigning it to the matrix, it automatically read the data
// and assigns it to the matrix.
//void
//Array4D::setFirstDimension(string const & filename, int pos, bool big_endian) {
//    int m = pos;
//    int n = 0;
//    int o = 0;
//    int p = 0;
//
//    int N = shape()[1];
//    int O = shape()[2];
//    int P = shape()[3];
//
//    std::ifstream file(filename.c_str(), std::ios::binary);
//
//    double read;
//    int index = 0;
//
//    // The eof check will  cause adding an extra element at the end.  
//    // Furthermore this code will only read as many elements as they fit
//    // in the declared data structure, otherwise an exception will be thrown
//    //
//    while (!file.eof() && index < (N*O*P) ) {
//
//        file.read(reinterpret_cast<char*> (&read), sizeof (read));
//        
//        if (big_endian) {
//            read = Functions::swap_endian(read);
//        }
//
//        if (n == N) {
//            n = 0;
//            o++;
//            if (o == O) {
//                o = 0;
//                p++;
//            }
//        }
//        
//        (*this)[m][n][o][p] = read;
//        index++;
//    }
//}

void
Array4D::randomize() {

    int M = shape()[0];
    int N = shape()[1];
    int O = shape()[2];
    int P = shape()[3];


    for (int m = 0; m < M; m++) {
        for (int n = 0; n < N; n++) {
            for (int o = 0; o < O; o++) {
                for (int p = 0; p < P; p++) {
                    {
//                        (*this)[m][n][o][p] = drand48();
                        std::srand(std::time(0));
                        (*this)[m][n][o][p] = std::rand();
                    }
                }
            }
        }
    }
}

bool
Array4D::isCircular(int pos) const {
    return ( circular_[pos]);
}

void
Array4D::setCircular(int pos) {
    circular_[pos] = true;
}

void
Array4D::unsetCircular(int pos) {
    circular_[pos] = false;
}

int
Array4D::getSizeDim0() const {
    return ( shape()[0]);
}

int
Array4D::getSizeDim1() const {
    return ( shape()[1]);
}

int
Array4D::getSizeDim2() const {
    return ( shape()[2]);
}

int
Array4D::getSizeDim3() const {
    return ( shape()[3]);
}

void
Array4D::print_size(ostream & os) const {

    int M = shape()[0];
    int N = shape()[1];
    int O = shape()[2];
    int P = shape()[3];

    os << "["
            << M << ", "
            << N << ", "
            << O << ", "
            << P << "]"
            << endl;
}

void
Array4D::print(ostream & os) const {

    os << "Array Shape = ";
    for (int i = 0; i < 4; i++) {
        os << "[ " << shape()[i] << " ]";
    }
    os << endl;

    int M = shape()[0];
    int N = shape()[1];
    int O = shape()[2];
    int P = shape()[3];


    for (int m = 0; m < M; m++) {
        for (int n = 0; n < N; n++) {

            os << "[ " << m << ", " << n << ", , ]" << endl;

            for (int p = 0; p < P; p++) {
                os << "\t[,,," << p << "]";
            }
            os << endl;

            for (int o = 0; o < O; o++) {
                os << "[,," << o << ",]\t";

                for (int p = 0; p < P; p++) {
                    os << (*this)[m][n][o][p] << "\t";
                }
                os << endl;

            }
            os << endl;
        }
        os << endl;
    }

//    os << "Circular Parameters:";
//
//    for (unsigned int i = 0; i < shape()[0]; i++) {
//        os << "[" << isCircular(i) << "]";
//    }
//    os << endl;


}

ostream &
operator<<(ostream & os, Array4D const & bv) {

    bv.print(os);

    return os;
}
