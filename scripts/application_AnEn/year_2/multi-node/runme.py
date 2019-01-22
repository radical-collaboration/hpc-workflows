import os
import sys
import yaml
import datetime
import argparse
from math import floor
from pprint import pprint
from netCDF4 import Dataset
from radical.entk import Pipeline, Stage, Task, AppManager


def expand_tilde(cfg):
    # This function can use os.path.expanduser() to expand the tilde sign.
    # First, get the expanded path of tilde, and then replace tildes in all strings.
    #
    return True


def get_months_between(start, end, format="%Y%m", reverse=False):
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
    # Get a list of search months
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Define the dimensions for both forecast and observation files
    files_dims = dict.fromkeys(["forecasts", "observations"])
    files_dims['forecasts'] = dict.fromkeys(months)
    files_dims['observations'] = dict.fromkeys(months)

    # Read dimensions from forecast files
    forecast_files = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]

    for i in range(len(forecast_files)):
        if global_cfg['verbose']:
            sys.stdout.write('Processing {}'.format(forecast_files[i]))
            sys.stdout.flush()

        nc = Dataset(forecast_files[i])
        dims = (len(nc.dimensions['num_parameters']), len(nc.dimensions['num_stations']),
                len(nc.dimensions['num_times']), len(nc.dimensions['num_flts']))
        nc.close()

        if check_dims:
            if (dims[0] != global_cfg['num-parameters']) or \
                    (dims[1] != global_cfg['num-grids']) or \
                    (dims[3] != global_cfg['num-flts']):
                sys.exit("File ({}) does not meet the dimension requirement.".format(forecast_files[i]))

        files_dims['forecasts'][months[i]] = dims

        if global_cfg['verbose']:
            sys.stdout.write(' Done!\n')

    # Read dimensions from observation files
    observation_files = ['{}{}{}'.format(global_cfg['observations-folder'], month, '.nc') for month in months]

    for i in range(len(observation_files)):
        if global_cfg['verbose']:
            sys.stdout.write('Processing {}'.format(observation_files[i]))
            sys.stdout.flush()

        nc = Dataset(observation_files[i])
        dims = (len(nc.dimensions['num_parameters']),
                len(nc.dimensions['num_grids']),
                len(nc.dimensions['num_times']))
        nc.close()

        if check_dims:
            if (dims[0] != global_cfg['num-parameters']) or (dims[1] != global_cfg['num-stations']):
                sys.exit("File ({}) does not meet the dimension requirement.".format(forecast_files[i]))

        files_dims['observations'][months[i]] = dims

        if global_cfg['verbose']:
            sys.stdout.write(' Done!\n')

    return files_dims

def task_sd_calc(i, stage_cfg, global_cfg, files_dims):
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
        index_starts.append(0)
        index_counts.append(global_cfg['num-parameters'])
        index_starts.append(int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
        if i == global_cfg['task-count'] - 1:
            index_counts.append(global_cfg['num-grids'] - int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
        else:
            index_counts.append(global_cfg['num-grids'] / global_cfg['task-count'])
        index_starts.append(0)
        index_counts.append(files_dims['forecasts'][month][2])
        index_starts.append(0)
        index_counts.append(global_cfg['num-flts'])

    t.arguments = [
        '--in', in_files,
        '--out', out_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--start', index_starts,
        '--count', index_counts,
    ]

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t

def task_sim_calc(i, month, stage_cfg, global_cfg, files_dims):
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

    # Calculate the indices for starts and counts
    test_starts = []; test_counts = []
    search_starts = []; search_counts = []
    obs_starts = []; obs_counts = []


    for month in months:


        ## This part can be written to a function
        index_starts.append(0)
        index_counts.append(global_cfg['num-parameters'])
        index_starts.append(int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
        if i == global_cfg['task-count'] - 1:
            index_counts.append(global_cfg['num-grids'] - int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
        else:
            index_counts.append(global_cfg['num-grids'] / global_cfg['task-count'])
        index_starts.append(0)
        index_counts.append(files_dims['forecasts'][month][2])
        index_starts.append(0)
        index_counts.append(global_cfg['num-flts'])

    t.arguments = [
        '--test-forecast-nc', stage_cfg['args']['test-forecast-nc'],
        '--search-forecast-nc', '{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--similarity-nc', '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc'),
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--sds-nc', '{}task-sd-calc-{:05d}{}'.format(global_cfg['sds-folder'], i, '.nc')

        # '--test-start', stage_cfg['args']['test-start'],
        # '--test-count', stage_cfg['args']['test-count'],
        # '--search-start', stage_cfg['args']['search-start'],
        # '--search-count', stage_cfg['args']['search-count'],
        # '--obs-start', stage_cfg['args']['obs-start'],
        # '--obs-count', stage_cfg['args']['obs-count'],
    ]

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t


def create_analog_select_task(i, month, stage_cfg, global_cfg, files_dims):
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
    index_starts = []
    index_counts = []

    index_starts.append(0)
    index_counts.append(global_cfg['num-parameters'])
    index_starts.append(int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
    if i == global_cfg['task-count'] - 1:
        index_counts.append(global_cfg['num-grids'] - int(global_cfg['num-grids'] / global_cfg['task-count']) * i)
    else:
        index_counts.append(global_cfg['num-grids'] / global_cfg['task-count'])
    index_starts.append(0)
    index_counts.append(files_dims['observations'][month][2])

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

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t


def create_pipelines(wcfg):

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

    with open('./resource_cfg.yml', 'r') as fp:
        rcfg = yaml.load(fp)

    with open('./workflow_cfg.yml', 'r') as fp:
        wcfg = yaml.load(fp)

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
