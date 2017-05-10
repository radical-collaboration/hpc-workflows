/* 
 * File:   main.cpp
 * Author: guido
 *
 * Created on October 1, 2013, 8:59 AM
 */

#include <iostream>
#include <vector>
#include <boost/program_options.hpp>

#include "Array4D.h"
#include "Functions.h"
#include "FileIO.h"
#include "Ensemble.h"
#include "boost/multi_array.hpp"
#include "boost/filesystem.hpp"
#include "WeimingMethod.h"

#include <fstream>

#if defined(_OPENMP)
#include <omp.h>
#else
double omp_get_wtime() {return 0.0;}
#endif

//#include <netcdf>
//#include "NcVarReservoir.h"

using namespace std;

void
run_analogs_Weiming(string bin_path, int parameter_ID, int stations, int test_ID_start, int test_ID_end,
        int train_ID_start, int train_ID_end, int rolling, int members_size,
        int num_cores, bool single_station_search, bool flag_print, string output_file) {

    // WeimingMethod
    cout << "**** Using WeimingMethod ****" << endl;


    Array4D observations(1, 669, 457, 17);
    Array4D forecasts(4, 669, 457, 17);

    cout << "Read and Assign observations... ";
    cout.flush();
    // flag indicate the way to read data
    // 1 --- binary
    // 2 --- netcdf
    int flag = 1;
    if (flag == 1) {
        vector<double> numbers;
        string file_path;

        file_path = bin_path + "obsWspd.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            observations.setFirstDimension(numbers, 0);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modPRES.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 0);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modTMP.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 1);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modWspd.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 2);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modWdir.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 3);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        forecasts.setCircular(3);
    } else if (flag == 2) {
        cout << "Warning: NetCDF has not been implemented yet!" << endl;
        return;
        //        NcVarReservoir<float> var;
        //        //string file_forecasts = "/Volumes/geolab_storage_V2/data/Analogs/netcdf/forecasts.nc";
        //        //string file_observations = "/Volumes/geolab_storage_V2/data/Analogs/netcdf/observations.nc";
        //        string file_forecasts = "/Users/weiming/Documents/Rutger/forecasts.nc";
        //        string file_observations = "/Users/weiming/Documents/Rutger/observations.nc";
        //        
        //        var.readVar(file_forecasts, "forecasts");
        //        var.transform_data_to_Array4D(forecasts);
        //        var.readVar(file_observations, "observations");
        //        var.transform_data_to_Array4D(observations);
    }

    cout << "Done!" << endl;

    // define the stations
    vector< int > stations_ID;
    for (int i = 0; i < stations; i++)
        stations_ID.push_back(i);
    vector<double> weights(forecasts.getSizeDim0(), 1);


    // compute analog ensembles
    WeimingMethod wm;
    cout << "** Computing Analogs **" << endl
            << "** start clock **" << endl;
    const double begin_runtime = omp_get_wtime();
    const clock_t begine_time = clock();
    Array4D analogs = wm.compute_analogs(
            forecasts,
            observations,
            weights, // The weights to use in the computations
            parameter_ID, // The parameter for which we perform the analogs
            stations_ID, // For which stations should we perform the analogs            
            test_ID_start, test_ID_end, // the days for which we do the test (verification)
            train_ID_start, train_ID_end, // the days for which we perform the analogs
            members_size, // how many members to keep
            rolling, // This indicates that the training / testing are rolling as in an operational sense
            num_cores,
            single_station_search);
    const double end_runtime = omp_get_wtime();
    cout << "** stop clock **" << endl
            << "** CPU time: " << float(clock() - begine_time) / CLOCKS_PER_SEC << " s" << endl
            << "** RUN time: " << end_runtime - begin_runtime << " s" << endl;

    cout << "Stations\t " << analogs.shape()[0] << endl;
    cout << "Testing Days\t " << analogs.shape()[1] << endl;
    cout << "Forecast Lead Times\t " << analogs.shape()[2] << endl;
    cout << "Number of Members\t " << analogs.shape()[3] << endl;
    cout << "Rolling\t" << rolling << endl;
    cout << "Multiple stations search\t" << !single_station_search << endl;

    if (flag_print) {
        string str_console = "console";
        if (output_file == str_console) {
            // output_file = 'console'
            cout << analogs << endl;
        } else {
            // output_file has been set to another file
            std::ofstream ofile(output_file, std::ofstream::out);
            ofile << analogs << endl;
            ofile.close();
        }
    }

    cout << "*****************************" << endl;

}

void
run_analogs_Luca(string bin_path, int parameter_ID, int stations, int test_ID_start, int test_ID_end,
        int train_ID_start, int train_ID_end, int rolling, int members_size,
        int quick, int num_cores, bool flag_print, string output_file) {

    // LucaMethod
    cout << "**** Using LucaMethod ****" << endl;

    Array4D observations(1, 669, 457, 17);
    Array4D forecasts(4, 669, 457, 17);

    cout << "Read and Assign observations... ";
    cout.flush();
    // flag indicate the way to read data
    // 1 --- binary
    // 2 --- netcdf
    int flag = 1;
    if (flag == 1) {
        vector<double> numbers;
        string file_path;

        file_path = bin_path + "obsWspd.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            observations.setFirstDimension(numbers, 0);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modPRES.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 0);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modTMP.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 1);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modWspd.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 2);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        file_path = bin_path + "modWdir.bin";
        if (boost::filesystem::exists(file_path)) {
            FileIO::readBin(file_path, numbers);
            forecasts.setFirstDimension(numbers, 3);
        } else {
            cout << "Error: " << file_path << " does not exist!" << endl;
            return;
        }

        forecasts.setCircular(3);
    } else if (flag == 2) {
        cout << "Warning: NetCDF has not been implemented yet!" << endl;
        return;
        //        NcVarReservoir<float> var;
        //        //string file_forecasts = "/Volumes/geolab_storage_V2/data/Analogs/netcdf/forecasts.nc";
        //        //string file_observations = "/Volumes/geolab_storage_V2/data/Analogs/netcdf/observations.nc";
        //        string file_forecasts = "/Users/weiming/Documents/Rutger/forecasts.nc";
        //        string file_observations = "/Users/weiming/Documents/Rutger/observations.nc";
        //        
        //        var.readVar(file_forecasts, "forecasts");
        //        var.transform_data_to_Array4D(forecasts);
        //        var.readVar(file_observations, "observations");
        //        var.transform_data_to_Array4D(observations);
    }

    cout << "Done!" << endl;

    // define the stations
    vector< int > stations_ID;
    for (int i = 0; i < stations; i++)
        stations_ID.push_back(i);
    vector<double> weights(forecasts.getSizeDim0(), 1);

    // compute analog ensembles
    AnEn lm;
    cout << "** Computing Analogs **" << endl
            << "** start clock **" << endl;
    const double begin_runtime = omp_get_wtime();
    const clock_t begine_time = clock();
    Array4D analogs = lm.computeAnalogs(forecasts,
            observations,
            weights, // The weights to use in the computations
            parameter_ID, // The parameter for which we perform the analogs
            stations_ID, // For which stations should we perform the analogs            
            test_ID_start, test_ID_end, // the days for which we do the test (verification)
            train_ID_start, train_ID_end, // the days for which we perform the analogs
            members_size, // how many members to keep
            rolling, // This indicates that the training / testing are rolling as in an operational sense
            quick, // Use sort of Kth element
            num_cores);

    const double end_runtime = omp_get_wtime();
    cout << "** stop clock **" << endl
            << "** CPU time: " << float(clock() - begine_time) / CLOCKS_PER_SEC << " s" << endl
            << "** RUN time: " << end_runtime - begin_runtime << " s" << endl;

    cout << "Stations\t " << analogs.shape()[0] << endl;
    cout << "Testing Days\t " << analogs.shape()[1] << endl;
    cout << "Forecast Lead Times\t " << analogs.shape()[2] << endl;
    cout << "Number of Members\t " << analogs.shape()[3] << endl;
    cout << "Rolling\t" << rolling << endl;

    if (flag_print) {
        string str_console = "console";
        if (output_file == str_console) {
            // output_file = 'console'
            cout << analogs << endl;
        } else {
            // output_file has been set to another file
            std::ofstream ofile(output_file, std::ofstream::out);
            ofile << analogs << endl;
            ofile.close();
        }
    }

    cout << "*****************************" << endl;
}

int
main(int argc, char** argv) {

    // count from 0
    // ranges are inclusive
    //
    int parameter_ID = 0;
    int stations = 3;
    int test_ID_start = 410;
    int test_ID_end = 415;
    int train_ID_start = 0;
    int train_ID_end = 400;
    int rolling = 0;
    int members_size = 11;
    bool quick = false;
    int num_cores = 1;
    bool multiple_stations_search = false;
    bool print_Weiming = false;
    bool print_Luca = false;
    bool use_Weiming_method = false;
    bool use_Luca_method = false;

    string bin_path = "../bin/";
    // output to the console by default
    string output_file = "console";


    // if you pass the parameters via command line
    if (argc > 1) {
        typedef boost::exception_detail::clone_impl<boost::exception_detail::error_info_injector<boost::program_options::unknown_option> > Exception;

        try {

            // specify the supported options
            namespace po = boost::program_options;
            po::options_description desc("Allowed options");
            desc.add_options()
                    ("help,h", "program to compute analog ensembles. Allowed options as followed.")
                    ("parameter-ID", po::value<int>(), "set parameter ID in the observations")
                    ("stations", po::value<int>(), "set number of stations to compute the ensembles")
                    ("test-ID-start", po::value<int>(), "set the start day of test dataset")
                    ("test-ID-end", po::value<int>(), "set the end day of test dataset")
                    ("train-ID-start", po::value<int>(), "set the start day of training dataset")
                    ("train-ID-end", po::value<int>(), "set the end day of training dataset")
                    ("rolling", po::value<int>(), "set the scale for rolling strategy")
                    ("members-size", po::value<int>(), "set the number of members in each ensemble")
                    ("quick,q", po::bool_switch()->default_value(false), "1 for quick/partial sort, 0 for global sort. This is only for Luca method.")
                    ("number-of-cores", po::value<int>(), "set the number of cores to use")
                    ("multiple-stations-search,M", po::bool_switch()->default_value(false), "use single station for search space")
                    ("Weiming-method,W", po::bool_switch()->default_value(false), "use Weiming method to compute analog ensembles")
                    ("Luca-method,L", po::bool_switch()->default_value(false), "use Luca method to compute analog ensembles")
                    ("print-Weiming-method,w", po::bool_switch()->default_value(false), "enable printing results from Weiming method")
                    ("print-Luca-method,l", po::bool_switch()->default_value(false), "enable printing results from Luca method")
                    ("data-folder,d", po::value<string>(), "set the folder of the data")
                    ("output-file,o", po::value<string>(), "set the full path of the output file");

            po::variables_map vm;
            po::store(po::parse_command_line(argc, argv, desc), vm);
            po::notify(vm);

            // respond to the options
            if (vm.count("help")) {
                cout << desc << endl;

                cout << "Default settings:" << endl;
                cout << "parameter_ID: " << parameter_ID << endl;
                cout << "stations: " << stations << endl;
                cout << "test_ID_start: " << test_ID_start << endl;
                cout << "test_ID_end: " << test_ID_end << endl;
                cout << "train_ID_start: " << train_ID_start << endl;
                cout << "train_ID_end: " << train_ID_end << endl;
                cout << "rolling: " << rolling << endl;
                cout << "members_size: " << members_size << endl;
                cout << "quick: " << quick << endl;
                cout << "num_cores: " << num_cores << endl;
                cout << "multiple_stations_search: " << multiple_stations_search << endl;
                cout << "print_Weiming: " << print_Weiming << endl;
                cout << "print_Luca: " << print_Luca << endl;
                cout << "use_Weiming_method: " << use_Weiming_method << endl;
                cout << "use_Luca_method: " << use_Luca_method << endl;
                cout << "bin_path: " << bin_path << endl;
                cout << "output_file: " << output_file << endl;
                return 0;
            }
            if (vm.count("parameter-ID")) {
                parameter_ID = vm["parameter-ID"].as<int>();
            }
            if (vm.count("stations")) {
                stations = vm["stations"].as<int>();
            }
            if (vm.count("test-ID-start")) {
                test_ID_start = vm["test-ID-start"].as<int>();
            }
            if (vm.count("test-ID-end")) {
                test_ID_end = vm["test-ID-end"].as<int>();
            }
            if (vm.count("train-ID-start")) {
                train_ID_start = vm["train-ID-start"].as<int>();
            }
            if (vm.count("train-ID-end")) {
                train_ID_end = vm["train-ID-end"].as<int>();
            }
            if (vm.count("rolling")) {
                rolling = vm["rolling"].as<int>();
            }
            if (vm.count("members-size")) {
                members_size = vm["members-size"].as<int>();
            }
            if (vm.count("quick")) {
                quick = vm["quick"].as<bool>();
            }
            if (vm.count("number-of-cores")) {
                num_cores = vm["number-of-cores"].as<int>();
            }
            if (vm.count("print-Weiming-method")) {
                print_Weiming = vm["print-Weiming-method"].as<bool>();
            }
            if (vm.count("print-Luca-method")) {
                print_Luca = vm["print-Luca-method"].as<bool>();
            }
            if (vm.count("Weiming-method")) {
                use_Weiming_method = vm["Weiming-method"].as<bool>();
            }
            if (vm.count("Luca-method")) {
                use_Luca_method = vm["Luca-method"].as<bool>();
            }
            if (vm.count("multiple-stations-search")) {
                multiple_stations_search = vm["multiple-stations-search"].as<bool>();
            }
            if (vm.count("data-folder")) {
                bin_path = vm["data-folder"].as<string>();
            }
            if (vm.count("output-file")) {
                output_file = vm["output-file"].as<string>();
            }
        } catch (Exception e) {
            cout << "Error: " << e.what() << endl;
            return 1;
        }
    }

    if (quick & !use_Luca_method) {
        cout << "Warning: --quick is specific for LucaMethod. --quick option not used!" << endl;
    }

    if (print_Luca & !use_Luca_method) {
        cout << "Warning: LucaMethod not selected. --print-Luca-method option not used!" << endl;
    }

    if (print_Weiming & !use_Weiming_method) {
        cout << "Warning: WeimingMethod not selected. --print-Weiming-method option not used!" << endl;
    }

    if (!use_Luca_method & !use_Weiming_method) {
        cout << "Warning: Nothing is done. At least you need to select one method from Weiming and Luca!" << endl;
        cout << "Use option --help or -h to get more information." << endl;
        return 0;
    }

    if (!use_Weiming_method & multiple_stations_search) {
        cout << "Warning: single_station_search only works in Weiming's method. The option is ignored." << endl;
    }

    if (use_Luca_method) {
        run_analogs_Luca(bin_path, parameter_ID, stations, test_ID_start, test_ID_end, train_ID_start,
                train_ID_end, rolling, members_size, quick, num_cores, print_Luca, output_file);
    }
    if (use_Weiming_method) {
        run_analogs_Weiming(bin_path, parameter_ID, stations, test_ID_start, test_ID_end, train_ID_start,
                train_ID_end, rolling, members_size, num_cores, !multiple_stations_search, print_Weiming, output_file);
    }

    return 0;
}
