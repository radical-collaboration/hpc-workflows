import re
import os
import sys
import datetime
from netCDF4 import Dataset


def extract_month(file_path, pattern = '.*?/(\d{6})\.nc$'):
    """
    This function extracts the month string from a file path using the specified pattern.

    :param file_path The string of the file path.
    :param pattern The pattern string to be used.
    :return: A string of the year and month, for example, 201001.
    """

    month = re.search(pattern, file_path)

    if month is None:
        print 'Error: Cannot extract month from the file path {}'.format(file_path)
        sys.exit(1)

    return month.group(1)


def get_months_between(start, end, format="%Y%m", reverse=False):
    """
    This functions generate a month sequence of strings between the specified dates
    with the input format.

    :param start: The string for the start of the month, for example, 201001.
    :param end: The string for the end of the month, for example, 201010.
    :param format: The format of the input and output month strings.
    :param reverse: Whether to reverse order the sequence.
    :return: A list of month strings.
    """

    start = datetime.datetime.strptime(start, format)
    end = datetime.datetime.strptime(end, format)

    # Add one day to the end to make the range inclusive
    dates = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days + 1)]
    dates_str = [i.strftime(format) for i in dates]

    # Only keep the unique strings
    months = list(set(dates_str))
    months.sort(reverse=reverse)

    return months


def get_files_dims(global_cfg, check_dims=True):
    """
    This functions reads and records the dimension information of test and search files.
    Observation and forecast search files are defined by global arguments.

    :param global_cfg: A dictionary with global arguments.
    :param check_dims: Whether to check dimensions.
    :return: A dictionary of dimension information for each month of observations and forecasts.
    """

    # Get a list of search months
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Define the dimensions for both forecast and observation files
    files_dims = dict.fromkeys(["forecasts", "observations"])
    files_dims['forecasts'] = dict.fromkeys(months)
    files_dims['observations'] = dict.fromkeys(months)

    # Add search files for observations and forecasts
    files_dims['forecasts']['search-files'] = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]
    files_dims['observations']['search-files'] = ['{}{}{}'.format(global_cfg['observations-folder'], month, '.nc') for month in months]

    # Read dimensions from forecast files
    forecast_files = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]

    # Add the forecast file
    month = extract_month(global_cfg['test-forecast-nc'])
    months.append(month)
    forecast_files.append('{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc'))

    for i in range(len(forecast_files)):
        if global_cfg['print-progress']:
            sys.stdout.write('Processing {}'.format(forecast_files[i]))
            sys.stdout.flush()

        nc = Dataset(forecast_files[i])
        dims = (len(nc.dimensions['num_parameters']), len(nc.dimensions['num_stations']),
                len(nc.dimensions['num_times']), len(nc.dimensions['num_flts']))
        nc.close()

        if check_dims:
            if (dims[0] != global_cfg['num-forecast-parameters']) or \
                    (dims[1] != global_cfg['num-grids']) or \
                    (dims[3] != global_cfg['num-flts']):
                print "Error: File ({}) does not meet the dimension requirement.".format(forecast_files[i])
                sys.exit(1)

        files_dims['forecasts'][months[i]] = dims

        if global_cfg['print-progress']:
            sys.stdout.write(' Done!\n')

    # Read dimensions from observation files
    observation_files = ['{}{}{}'.format(global_cfg['observations-folder'], month, '.nc') for month in months]

    for i in range(len(observation_files)):
        if global_cfg['print-progress']:
            sys.stdout.write('Processing {}'.format(observation_files[i]))
            sys.stdout.flush()

        nc = Dataset(observation_files[i])
        dims = (len(nc.dimensions['num_parameters']),
                len(nc.dimensions['num_stations']),
                len(nc.dimensions['num_times']))
        nc.close()

        if check_dims:
            if (dims[0] != global_cfg['num-observation-parameters']) or (dims[1] != global_cfg['num-grids']):
                print "Error: File ({}) does not meet the dimension requirement.".format(forecast_files[i])
                sys.exit(1)

        files_dims['observations'][months[i]] = dims

        if global_cfg['print-progress']:
            sys.stdout.write(' Done!\n')

    return files_dims


def get_indices(type, month, task_i, files_dims, global_cfg):
    """
    This function generates the indices to be used by PEF based on the task number and the month.
    Currently, the dimension of grids are distributed among tasks.

    :param type: A string of either 'forecasts' or 'observations'.
    :param month: A string of year and month, for example, 201001.
    :param task_i: The task number.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :param global_cfg: The global configuration dictionary
    :return: A list of indices
    """

    # Add the index for parameters
    starts = [0]
    if type is "forecasts":
        counts = [global_cfg['num-forecast-parameters']]
    elif type is "observations":
        counts = [global_cfg['num-observation-parameters']]
    else:
        print "Error: Unrecognized type {}".format(type)
        sys.exit(1)

    # Add the index for stations
    starts.append(int(global_cfg['num-grids'] / global_cfg['task-count']) * task_i)
    if task_i == global_cfg['task-count'] - 1:
        counts.append(global_cfg['num-grids'] - int(global_cfg['num-grids'] / global_cfg['task-count']) * task_i)
    else:
        counts.append(int(global_cfg['num-grids'] / global_cfg['task-count']))

    # Add the index for times
    starts.append(0)
    counts.append(files_dims[type][month][2])

    # Add the index for FLTs
    if type is 'forecasts':
        starts.append(0)
        counts.append(global_cfg['num-flts'])

    return [starts, counts]


def check_empty(global_cfg):
    empty = True
    num_sims_files = len(os.listdir(global_cfg['sims-folder']))
    num_analogs_files = len(os.listdir(global_cfg['analogs-folder']))
    num_config_files = len(os.listdir(global_cfg['config-folder']))

    if num_config_files != 0:
        print "Directory {} is not empty.".format(global_cfg['config-folder'])
        empty = False

    if num_sims_files != 0:
        if num_sims_files != global_cfg['task-count']:
            print "Directory {} is not empty.".format(global_cfg['sims-folder'])
            empty = False

    if num_analogs_files != 0:
        if num_analogs_files != global_cfg['task-count']:
            print "Directory {} is not empty.".format(global_cfg['analogs-folder'])
            empty = False

    return empty


def expand_tilde(cfg):
    """
    This function uses os.path.expanduser() to expand the tilde sign.
    First, get the expanded path of tilde, and then replace tildes in all strings
    contained in the input dict.

    :param cfg: A dictionary.
    :return: A dictionary.
    """

    # Get the expanded path of the tilde sign
    path = os.path.expanduser('~')

    # Match the tilde sign and change
    def iterdict(d):
        for k, v in d.items():
            if isinstance(v, dict):
                iterdict(v)
            else:
                if isinstance(v, str) and "~" in v:
                    d[k] = v.replace('~',path)
                elif isinstance(v, list):
                    d[k] = [x if '~' not in x else x.replace('~',path) for x in v]

    iterdict(cfg)
    return cfg


def write_config_files(file_type, global_cfg, files_dims):
    """
    This function writes the configuration files for

    - search-forecasts: search-forecast-nc, search-start, search-count;
    - observations: observation-nc; obs-start; obs-count;

    :param file_type: The type of configurations.
    :param global_cfg: The global configurations.
    :param files_dims: The dimension information for files.
    :return: A boolean for whether it is successfully finished.
    """

    if file_type == 'test-forecasts':
        config_prefix = 'test'
        par_name_file = 'test-forecast-nc'
        par_name_start = 'test-start'
        par_name_count = 'test-count'
    elif file_type == 'search-forecasts':
        config_prefix = 'search'
        par_name_file = 'search-forecast-nc'
        par_name_start = 'search-start'
        par_name_count = 'search-count'
    elif file_type == 'observations':
        config_prefix = 'obs'
        par_name_file = 'observation-nc'
        par_name_start = 'obs-start'
        par_name_count = 'obs-count'
    else:
        print 'Error: Wrong file_type {}'.format(file_type)
        sys.exit(1)

    if file_type == 'test-forecasts':
        months = [extract_month(global_cfg['test-forecast-nc'])]
    else:
        months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    for i in range(global_cfg['task-count']):
        config_file = "{}{}-{:05d}.cfg".format(global_cfg['config-folder'], config_prefix, i)

        if os.path.isfile(config_file):
            print "{} exists. Skip writing to this file!".format(config_file)
        else:
            print "Generating configuration file {} ...".format(config_file)

            with open(config_file, 'a') as out_file:
                for month in months:

                    if file_type == 'test-forecasts':
                        [start, count] = get_indices('forecasts', month, i, files_dims, global_cfg)
                        nc_file = [global_cfg['test-forecast-nc']]
                    elif file_type == 'search-forecasts':
                        [start, count] = get_indices('forecasts', month, i, files_dims, global_cfg)
                        nc_file = [file for file in files_dims['forecasts']['search-files'] if month in file]
                    elif file_type == 'observations':
                        [start, count] = get_indices('observations', month, i, files_dims, global_cfg)
                        nc_file = [file for file in files_dims['observations']['search-files'] if month in file]
                    else:
                        print 'Error: Wrong file_type {}'.format(file_type)
                        sys.exit(1)

                    if len(nc_file) != 1:
                        print 'Error: Cannot find the file for month {}.'.format(month)
                        sys.exit(1)

                    out_file.write(' '.join([par_name_file, '=', nc_file[0]]))
                    out_file.write('\n')

                    str_list = [par_name_start, '=']
                    str_list =  ['{} {}'.format(' '.join(str_list), s) for s in start]
                    out_file.write('\n'.join(str_list))
                    out_file.write('\n')

                    str_list = [par_name_count, '=']
                    str_list =  ['{} {}'.format(' '.join(str_list), s) for s in count]
                    out_file.write('\n'.join(str_list))

                    out_file.write('\n\n')

    return True
