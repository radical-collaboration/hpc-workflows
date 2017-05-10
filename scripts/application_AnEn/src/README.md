# Analogs Ensemble User Guide

```
"`-''-/").___..--''"`-._
(`6_ 6  )   `-.  (     ).`-.__.`)   WE ARE ...
(_Y_.)'  ._   )  `._ `. ``-..-'    PENN STATE!
_ ..`--'_..-_/  /--'_.' ,'
(il),-''  (li),'  ((!.-'
```

*Weiming Hu*
*wuh20@psu.edu*
*[Geoinformatics and Earth Observation Laboratory](http://geolab.psu.edu)*
*Department of Geography and Institute for CyberScience*
*The Pennsylvania State University*

This is the guide for compiling Analog Ensemble C++ code.

### Getting Prepared
To compile AnEn, the following tools/libraries are needed:

- GCC (recommended);
- Boost library

##### GCC

To begin with, [GCC](https://gcc.gnu.org/) is preferred to compile the code. If you are using MacOS system, you do not have GCC by default because MacOS uses Clang compiler. Clang sometimes work, but for the sake of standardization, we recommend using GCC.

- Linux: by default, you should already have a functional GCC. If you do not know where is it, you can check in the shell using `which gcc`;
- MacOS: To install GCC, [HomeBrew](https://brew.sh/) can be a great application to help you manage and install the tools and packages. AnEn has been tested by using version `4.8`, `4.9` and `7`;
- Windows: To install GCC, two potential solutions are [MinGW](http://www.mingw.org/) and [Cygwin](https://www.cygwin.com/). But these solutions have not yet been tested. If you have any problem compiling, please contact the AnEn maintainer;

After you have installed GCC, you can check if it works in the shell. For example, if you have installed GCC 7 using HomeBrew, you can type the following:

```
$ gcc-7 --version
gcc-7 (Homebrew GCC 7.1.0) 7.1.0
Copyright (C) 2017 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

##### Boost Library

Next, [Boost](http://www.boost.org/) is a set of libraries for the C++ programming language. **Note** that Boost compiled by GCC is not compatible with Clang, and vice versa. So please be aware of the compiler you use when you compile Boost library, and use the same compiler to compile the AnEn code.

You can install and compile Boost by using a package manager.

- Linux: Depending on your distribution, use `sudo apt-get install libboost-all-dev` for Debian or `yum install boost-devel`;
- MacOS: To use HomeBrew to install Boost, we need to tell HomeBrew to use the specific compiler otherwise HomeBrew will use the system default compiler, clang, Use `HOMEBREW_CC=gcc-7 HOMEBREW_CXX=g++-7 brew install boost --c++11`. Basically we are setting the environment variables for HomeBrew saying that HomeBrew should use `gcc-7` and `g++-7` to compile c/c++ codes, and the installed library should be compatible with C++11 standard;
- Windows: At this point of time, sorry that we do not offer any potential solutions. Please manually compile Boost;

To manually compile Boost library, a detailed guide is offered in the [Boost Getting Started Guide](http://www.boost.org/doc/libs/1_64_0/more/getting_started/index.html). Please choose your system at the bottom right, and follow the guide.

### Compiling AnEn
You can always use an Integrated Development Environment (IDE) application, like [NetBeans]([https://netbeans.org/), to compile the code. If you are using an IDE, you need to set the following options:

- Compiler: use the same compiler that was used to compile Boost;
- Compiler options: `-std=c++11 -fopenmp`;
- Include directories: `/[your directory to boost]/include`;
- Linker options: `-lboost_program_options -lboost_filesystem -lboost_system`;
- Additional library directories: `/[your directory to boost]/lib`;

You can also compile the AnEn code using the provided `Makefile.in` and `configure.ac`. They are located under `troubleshoot`. These two files guide the system how to compile the codes.

```
# assume that we are under the src directory
# copy the two files into our project folder
cp troubleshoot/Makefile.in .
cp troubleshoot/configure.ac .

# configure options for compilation
autoconf

# generate the Makefile
./configure

# compile
make
```

If you have any problems, please contact maintaner. Thank you.
