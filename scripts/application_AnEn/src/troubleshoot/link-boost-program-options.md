# c++ linking problem with boost::program_options in Mac

### Description
After Booost library is installed (using HomeBrew) and the option `-lboost_program_options` is added to the linker options, the compiler gives the following linking errors:

```
Undefined symbols for architecture x86_64:
  "boost::program_options::to_internal(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)", referenced from:
      std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > boost::program_options::to_internal<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&) in main.o
  "boost::program_options::validation_error::get_template[abi:cxx11](boost::program_options::validation_error::kind_t)", referenced from:
      boost::program_options::validation_error::validation_error(boost::program_options::validation_error::kind_t, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int) in main.o
  "boost::program_options::options_description::options_description(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, unsigned int, unsigned int)", referenced from:
      _main in main.o
  "boost::program_options::invalid_option_value::invalid_option_value(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)", referenced from:
      void boost::program_options::validate<int, char>(boost::any&, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, int*, long) in main.o
  "boost::program_options::error_with_option_name::error_with_option_name(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int)", referenced from:
      boost::program_options::validation_error::validation_error(boost::program_options::validation_error::kind_t, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int) in main.o
  "boost::program_options::arg[abi:cxx11]", referenced from:
      boost::program_options::typed_value<int, char>::name[abi:cxx11]() const in main.o
  "boost::program_options::detail::cmdline::set_additional_parser(boost::function1<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&>)", referenced from:
      boost::program_options::basic_command_line_parser<char>::extra_parser(boost::function1<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&>) in main.o
  "boost::program_options::detail::cmdline::cmdline(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&)", referenced from:
      boost::program_options::basic_command_line_parser<char>::basic_command_line_parser(int, char const* const*) in main.o
  "boost::program_options::operator<<(std::basic_ostream<char, std::char_traits<char> >&, boost::program_options::options_description const&)", referenced from:
      _main in main.o
  "boost::program_options::abstract_variables_map::operator[](std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) const", referenced from:
      boost::program_options::variables_map::operator[](std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) const in main.o
  "boost::program_options::error_with_option_name::substitute_placeholders(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) const", referenced from:
      vtable for boost::exception_detail::clone_impl<boost::exception_detail::error_info_injector<boost::program_options::unknown_option> > in main.o
      vtable for boost::exception_detail::error_info_injector<boost::program_options::unknown_option> in main.o
      vtable for boost::program_options::invalid_option_value in main.o
      vtable for boost::program_options::validation_error in main.o
      vtable for boost::program_options::unknown_option in main.o
      vtable for boost::program_options::error_with_no_option_name in main.o
      vtable for boost::exception_detail::clone_impl<boost::exception_detail::error_info_injector<boost::program_options::validation_error> > in main.o
      ...
  "boost::program_options::value_semantic_codecvt_helper<char>::parse(boost::any&, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, bool) const", referenced from:
      vtable for boost::program_options::typed_value<int, char> in main.o
ld: symbol(s) not found for architecture x86_64
collect2: error: ld returned 1 exit status
make[2]: *** [dist/Debug/GCC-7-MacOSX/canalogsmp] Error 1
make[1]: *** [.build-conf] Error 2
make: *** [.build-impl] Error 2

BUILD FAILED (exit value 2, total time: 15s)
```

### Diagnosis
The problem is that the compiler cannot successfully link library `program options` from Boost. There is a conflict in the compatibility between Boost compiled with clang and Boost compiler with GNU.

To see which compiler was used, use the following command in the shell:

```
$ otool -L /opt/local/lib/libboost_program_options-mt.dylib
/opt/local/lib/libboost_program_options-mt.dylib:
    /opt/local/lib/libboost_program_options-mt.dylib (compatibility version 0.0.0, current version 0.0.0)
    /usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 120.0.0)
    /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1213.0.0)
```

If you see `libc++`, it is probably compiled using Clang.

### Solution
Tell HomeBrew to use the specific compiler to install the library. Here, since I know that I will be using GCC7, I tell HomeBrew to install packages using GCC7. The option `--c++11` tells the HomeBrew to make it compatible with c++11 standard.

```
HOMEBREW_CC=gcc-7 HOMEBREW_CXX=g++-7 brew reinstall boost --c++11
```

After it is done, do the `otool` check again:

```
$ otool -L libboost_program_options.dylib
libboost_program_options.dylib:
	/usr/local/opt/boost/lib/libboost_program_options.dylib (compatibility version 0.0.0, current version 0.0.0)
	/usr/local/opt/gcc/lib/gcc/7/libstdc++.6.dylib (compatibility version 7.0.0, current version 7.23.0)
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1238.51.1)
	/usr/local/lib/gcc/7/libgcc_s.1.dylib (compatibility version 1.0.0, current version 1.0.0)
```

Now there is `libstdc++` instead of `libc++` which means that it is compiled with GNU.

Try to clean and re-compile your code with `-lboost_program_options`, good luck.
