/* 
 * File:   FileIO.cpp
 * Author: guido
 * 
 * Created on October 2, 2013, 9:56 AM
 */

#include <string>
#include <iostream>
#include <iterator>
#include <fstream>
#include <algorithm>
#include <cstdlib> 
#include <boost/algorithm/string.hpp>

#include "FileIO.h"
#include "Functions.h"

using namespace std;
using namespace boost;

FileIO::FileIO() {
}

FileIO::FileIO(const FileIO& orig) {
}

FileIO::~FileIO() {
}

bool
FileIO::readTxt(std::string const & filename, std::vector< double > & data) {

    std::ifstream file(filename.c_str());

    if (file.is_open()) {
        std::istream_iterator<double> start(file), end;
        std::vector<double> numbers(start, end);
        data = numbers;

    } else {
        cerr << "Cannot open " << filename << endl;
        return ( false);
    }

    return ( true);
}


bool
FileIO::readBin(std::string const & filename, std::vector< double > & vec, bool big_endian) {
    // open the file:
    std::ifstream file(filename.c_str(), std::ios::binary);

    vec.clear(); // It must be clear because it might include prior data
    double read;

    while (!file.eof()) {
        file.read(reinterpret_cast<char*> (&read), sizeof (read));

        if (big_endian) {
            read = Functions::swap_endian(read);
        }
        vec.push_back(read);

    }

    // We need to remove the last element.... for whatever reason
    //
    vec.resize(vec.size() - 1);

    return ( true);
}