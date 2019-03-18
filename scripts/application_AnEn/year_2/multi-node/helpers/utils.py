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
        sys.exit('Cannot extract month from the file path {}'.format(file_path))

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
    files_dims['forecasts']['search_files'] = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]
    files_dims['observations']['search_files'] = ['{}{}{}'.format(global_cfg['observations-folder'], month, '.nc') for month in months]

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
                sys.exit("File ({}) does not meet the dimension requirement.".format(forecast_files[i]))

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
                sys.exit("File ({}) does not meet the dimension requirement.".format(forecast_files[i]))

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
        sys.exit("Unrecognized type {}".format(type))

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
    num_sds_files = len(os.listdir(global_cfg['sds-folder']))
    num_sims_files = len(os.listdir(global_cfg['sims-folder']))
    num_analogs_files = len(os.listdir(global_cfg['analogs-folder'])) 

    if num_sds_files != 0:
        if num_sds_files != global_cfg['task-count'] + 1:
            print "Directory {} is not empty.".format(global_cfg['sds-folder'])
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
