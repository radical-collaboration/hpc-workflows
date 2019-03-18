from utils import get_indices, get_months_between
from radical.entk import Task
from pprint import pprint
import os

def create_analog_select_task(i, stage_cfg, global_cfg, files_dims):
    """
    This function creates a analog selection task for the specified task number.

    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-analog-select-{:05d}'.format(i)

    analog_file = '{}{:05d}{}'.format(global_cfg['analogs-folder'], i, '.nc')

    if os.path.isfile(analog_file):
        print t.name + ": " + analog_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating analog selection task {}".format(t.name)

    # Calculate the indices for starts and counts
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])
    obs_counts = []; obs_starts = [];
    for month in months:
        [obs_start, obs_count] = get_indices('observations', month, i, files_dims, global_cfg)
        obs_starts.extend(obs_start)
        obs_counts.extend(obs_count)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    t.arguments = [
        '--quick', stage_cfg['args']['quick'],
        '--members', stage_cfg['args']['members'],
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],

        '--similarity-nc', '{}{:05d}{}'.format(global_cfg['sims-folder'], i, '.nc'),
        '--analog-nc', analog_file,
        '--obs-along', 2,
    ]

    t.arguments.append('--observation-nc'); t.arguments.extend(files_dims['observations']['search_files'])
    t.arguments.append('--obs-start'); t.arguments.extend(obs_starts)
    t.arguments.append('--obs-count'); t.arguments.extend(obs_counts)

    if global_cfg['print-help']:
        t.arguments.append('-h')

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
