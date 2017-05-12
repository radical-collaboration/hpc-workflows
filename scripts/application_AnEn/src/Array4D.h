/* 
 * File:   Array4D.h
 * Author: Guido Cervone
 *
 * Created on October 1, 2013, 9:00 AM
 *
 * This is the main container class for the 4D data structure that 
 * contains both the observations and the forecasts
 * 
 * It is implemented starting from the boost multidimensional array
 * library, which is optimized for speed and for compatibility with 
 * the STL containers. 
 *  */

#ifndef ARRAY4D_H
#define ARRAY4D_H

#include <boost/multi_array.hpp>
#include <iostream>
#include <vector>

using namespace std;

/** GC:
 This is the basic data structure that is used to store the forecasts and
 * the observations.  Normally the data is stored in the following format:
 * 
 * [Parameter][Station][Days][Forecast Lead Time]
 * 
 * It is assumed that all the data is stored as double.  It has not been
 * templated for optimization purposes, but it should be rather trivial
 * to make this class work with different data types. 
 * 
 * The class extends the functionality of the boost multidimensional array
 * structure, which is used as the underlying container for the data.  Although
 * defining a built 4D array could lead to an increase in speed, it 
 * is not possible to use standard STL paradigm and algorithms.  The boost 
 * library allows for a transparent integration with STL, and provides an
 * optimized data structure bug free.  The library is currently maintained and
 * used worldwide.
 * 
 */
class Array4D : public boost::multi_array<double, 4> {
public:

    Array4D();
    Array4D(const Array4D&);

    Array4D(int d1, int d2, int d3, int d4);
    Array4D(vector< double > const &, int M, int N, int O, int P);

    virtual ~Array4D();

    Array4D & operator=(const Array4D &rhs);


    /** GC: 
     * Used to set the data from a file when read one parameter at a time
     */
    void setFirstDimension(vector<double> const & data, int pos);
    //void setFirstDimension(string const & filename, int pos, bool big_endian = true);

    void getDimension(vector<double> & data, int pos);


    bool isCircular(int pos) const;
    void setCircular(int pos);
    void unsetCircular(int pos);

    int getSizeDim0() const;
    int getSizeDim1() const;
    int getSizeDim2() const;
    int getSizeDim3() const;

    bool myresize(int, int, int, int);

    /** GC: 
     * Randomize the array
     */
    void randomize();

    void print(ostream &) const;
    void print_size(ostream &) const;
    friend ostream & operator<<(ostream &, Array4D const &);

private:

    vector< bool > circular_;
};

#endif /* ARRAY4D_H */

