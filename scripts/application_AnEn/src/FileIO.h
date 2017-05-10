/* 
 * File:   FileIO.h
 * Author: guido
 *
 * Created on October 2, 2013, 9:56 AM
 */

#ifndef FILEIO_H
#define	FILEIO_H

#include <cstring>
#include <vector>

#include "Array4D.h"

class FileIO {
public:
    FileIO();
    FileIO(const FileIO& orig);
    virtual ~FileIO();
    
    static bool  readTxt( std::string const & filename, std::vector< double > & data );
    static bool  readBin( std::string const & filename, std::vector< double > & data, bool big_endian = true );
        
private:

};

#endif	/* FILEIO_H */

