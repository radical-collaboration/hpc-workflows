from radical.entk import Task
from utils import extract_month, get_indices
from pprint import pprint
import os

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
    t.name = 'task-sims-calc-{}-{:05d}'.format(month, i)

    sim_comb_file = '{}{:05d}{}'.format(global_cfg['analogs-folder'], i, '.nc')
    sim_file = '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc')

    if os.path.isfile(sim_comb_file):
        print t.name + ": " + sim_comb_file + " already exists. Skip generating this file!"
        return False

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
