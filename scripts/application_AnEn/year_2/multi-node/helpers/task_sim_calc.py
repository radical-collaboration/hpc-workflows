from radical.entk import Task
from utils import extract_month, get_indices, get_months_between
from pprint import pprint
import os

def task_sim_calc_v2(i, stage_cfg, global_cfg, files_dims):
    """
    This function creates a similarity calculation task for the specified task number.

    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-sims-calc-{:05d}'.format(i)
    sim_file = '{}{:05d}{}'.format(global_cfg['sims-folder'], i, '.nc')

    if os.path.isfile(sim_file):
        print t.name + ": " + sim_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating similarity task {}".format(t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    t.arguments = [
        '--similarity-nc', sim_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--test-forecast-nc', global_cfg['test-forecast-nc'],
        '--search-forecast-nc', '{}{:05d}{}'.format(global_cfg['forecasts-folder'], i, '.nc'),
        '--observation-nc', '{}{:05d}{}'.format(global_cfg['observations-folder'], i, '.nc'),
    ]

    test_month = extract_month(global_cfg['test-forecast-nc'])
    [test_starts, test_counts] = get_indices('forecasts', test_month, i, files_dims, global_cfg)

    t.arguments.append('--test-start'); t.arguments.extend(test_starts)
    t.arguments.append('--test-count'); t.arguments.extend(test_counts)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t


def task_sim_calc(i, stage_cfg, global_cfg, files_dims):
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

    sim_file = '{}{:05d}{}'.format(global_cfg['sims-folder'], i, '.nc')

    if os.path.isfile(sim_file):
        print t.name + ": " + sim_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating similarity task {}".format(t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    # Extract the month
    test_month = extract_month(global_cfg['test-forecast-nc'])
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Calculate the indices for starts and counts
    [test_starts, test_counts] = get_indices('forecasts', test_month, i, files_dims, global_cfg)
    search_counts = []; search_starts = [];
    obs_counts = []; obs_starts = [];
    for month in months:
        [search_start, search_count] = get_indices('forecasts', month, i, files_dims, global_cfg)
        search_starts.extend(search_start)
        search_counts.extend(search_count)
        [obs_start, obs_count] = get_indices('observations', month, i, files_dims, global_cfg)
        obs_starts.extend(obs_start)
        obs_counts.extend(obs_count)

    t.arguments = [
        '--test-forecast-nc', global_cfg['test-forecast-nc'],
        '--search-forecast-nc', '{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--similarity-nc', sim_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--sds-nc', '{}task-sd-calc-{:05d}{}'.format(global_cfg['sds-folder'], i, '.nc'),
    ]
    
    # Add list arguments
    t.arguments.append('--test-start'); t.arguments.extend(test_starts)
    t.arguments.append('--test-count'); t.arguments.extend(test_counts)
    t.arguments.append('--search-start'); t.arguments.extend(search_starts)
    t.arguments.append('--search-count'); t.arguments.extend(search_counts)
    t.arguments.append('--obs-start'); t.arguments.extend(obs_starts)
    t.arguments.append('--obs-count'); t.arguments.extend(obs_counts)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
