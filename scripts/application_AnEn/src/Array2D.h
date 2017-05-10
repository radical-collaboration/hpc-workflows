/* 
 * File:   Array2D.h
 * Author: Guido Cervone
 *  */

#ifndef ARRAY2D_H
#define	ARRAY2D_H

//#include <boost/multi_array.hpp>
#include <iostream>
#include <vector>

using namespace std;

/** GC:
 */
//class Array2D : public boost::multi_array<double, 2> {
class Array2D : public vector < vector < double > > {
public:

    Array2D();
    Array2D(int, int);
    Array2D(const Array2D&);

    double sizeM() const;
    double sizeN() const;
    
    virtual ~Array2D();

    void randomize();
    
    void print_size(ostream &) const;
    void print(ostream &) const;
    void print_dim( ostream &, int ) const;
    friend ostream & operator<<(ostream &, Array2D const &);

private:

};

class Array2DCompare {
public:

    explicit Array2DCompare(int column);
    
    bool operator()(vector <double> const& lhs,
        vector <double> const& rhs);

private:
    int m_column_;
};


#endif	/* ARRAY2D_H */

