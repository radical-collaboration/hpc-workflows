import re
import os
import sys
import yaml
import argparse
import datetime
from pprint import pprint
from netCDF4 import Dataset
from radical.entk import Pipeline, Stage, Task, AppManager


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


def task_sd_calc(i, stage_cfg, global_cfg, files_dims):
    """
    This function creates a standard deviation task for the specified task number.

    :param i: The task number.
    :param stage_cfg: The configuration for this stage.
    :param global_cfg: The global configuration.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """
    t = Task()
    t.name = 'task-sd-calc-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }

    # Select input files based on the search month range
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Append the data folder prefix and the file format suffix
    in_files = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]
    out_file = '{}{}{}'.format(global_cfg['sds-folder'], t.name, '.nc')

    # Calculate the indices for starts and counts
    index_starts = []; index_counts = []

    for month in months:
        [starts, counts] = get_indices('forecasts', month, i, files_dims, global_cfg)
        index_starts.extend(starts)
        index_counts.extend(counts)

    t.arguments = [
        '--in', in_files,
        '--out', out_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--start', index_starts,
        '--count', index_counts,
    ]

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t

def task_sim_calc(i, month, stage_cfg, global_cfg, files_dims):
    """
    This function creates a similarity calculation task for the specified task number.

    :param i: The task number.
    :param month: The string for year and month, for example, 201001.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-sims-calc-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }

    # Extract the test month from the test forecast file path
    test_month = extract_month(global_cfg['test-forecast-nc'])

    # Calculate the indices for starts and counts
    [test_starts, test_counts] = get_indices('forecasts', test_month, i, files_dims, global_cfg)
    [search_starts, search_counts] = get_indices('forecasts', month, i, files_dims, global_cfg)
    [obs_starts, obs_counts] = get_indices('observations', month, i, files_dims, global_cfg)

    t.arguments = [
        '--test-forecast-nc', global_cfg['test-forecast-nc'],
        '--search-forecast-nc', '{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--similarity-nc', '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc'),
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--sds-nc', '{}task-sd-calc-{:05d}{}'.format(global_cfg['sds-folder'], i, '.nc'),
        '--test-start', test_starts,
        '--test-count', test_counts,
        '--search-start', search_starts,
        '--search-count', search_counts,
        '--obs-start', obs_starts,
        '--obs-count', obs_counts,
    ]

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t


def create_analog_select_task(i, month, stage_cfg, global_cfg, files_dims):
    """
    This function creates a analog selection task for the specified task number.

    :param i: The task number.
    :param month: The string of year and month, for example, 201001.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-analog-select-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }

    # Calculate the indices for starts and counts
    [index_starts, index_counts] = get_indices('observations', month, i, files_dims, global_cfg)

    t.arguments = [
        '--quick', stage_cfg['args']['quick'],
        '--members', stage_cfg['args']['members'],
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],

        '--similarity-nc', '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--analog-nc', '{}{}-{:05d}{}'.format(global_cfg['analogs-folder'], month, i, '.nc'),

        '--obs-start', index_starts,
        '--obs-count', index_counts,
    ]

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t


def create_pipelines(wcfg):
    """
    This function creates a Pipeline with the given configuration dictionary.

    :param wcfg: The configuration dictionary.
    :return: A Pipeline object.
    """

    # Get dimensions of all forecast and observation files
    files_dims = get_files_dims(wcfg['global'])

    p = Pipeline()

    # Create the stage for standard deviation calculator tasks
    s = Stage()
    s.name = 'stage-sd-calc'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = task_sd_calc(i, stage_cfg, wcfg['global'], files_dims)
        s.add_tasks(t)

    p.add_stages(s)

    # Create the stage for similarity calculator tasks
    s = Stage()
    s.name = 'stage-sim-calc'
    stage_cfg = wcfg[s.name]

    # Get the number of forecast files to be used. This is the number of months specified.
    months = get_months_between(wcfg['global']['search-month-start'], wcfg['global']['search-month-end'])

    for i in range(wcfg['global']['task-count']):
        for j in range(len(months)):
            t = task_sim_calc(i, months[j], stage_cfg, wcfg['global'], files_dims)
            s.add_tasks(t)

    p.add_stages(s)

    # Create the stage for analog selector tasks
    s = Stage()
    s.name = 'stage-analog-select'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        for j in range(len(months)):
            t = create_analog_select_task(i, months[j], stage_cfg, wcfg['global'], files_dims)
            s.add_tasks(t)

    p.add_stages(s)

    return p


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--wcfg', help='path to workflow cfg file', required=False, default='./workflow_cfg.yml')
    parser.add_argument('--rcfg', help='path to resource cfg file', required=False, default='./resource_cfg.yml')

    args = parser.parse_args()
    if not os.path.isfile(args.wcfg):
        print '%s does not exist' % args.wcfg
        sys.exit(1)

    if not os.path.isfile(args.rcfg):
        print '%s does not exist' % args.rcfg
        sys.exit(1)

    with open(args.rcfg, 'r') as fp:
        rcfg = yaml.load(fp)

    with open(args.wcfg, 'r') as fp:
        wcfg = yaml.load(fp)

    with open('./workflow_cfg.yml', 'r') as fp:
        wcfg = yaml.load(fp)

    wcfg = expand_tilde(wcfg)

    amgr = AppManager(hostname=rcfg['rabbitmq']['hostname'],
                      port=rcfg['rabbitmq']['port'])

    res_desc = {
        'resource': rcfg['resource-desc']['name'],
        'walltime': rcfg['resource-desc']['walltime'],
        'cpus': rcfg['resource-desc']['cpus'],
        'queue': rcfg['resource-desc']['queue'],
        'project': rcfg['resource-desc']['project']
    }

    amgr.resource_desc = res_desc

    pipelines = create_pipelines(wcfg)
    if not isinstance(pipelines, list):
        pipelines = [pipelines]

    amgr.workflow = pipelines

    if wcfg['global']['print-tasks-only']:
        print("Print tasks created only. Nothing has been run.")
    else:
        amgr.run()
