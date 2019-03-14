from radical.entk import Task
from utils import get_months_between, get_indices
from pprint import pprint
import os
import re

def task_obs_combine(i, stage_cfg, global_cfg, files_dims):
    """
    This function combines the observation files along time for a specific geographic region.

    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-obs_combine-{:05d}'.format(i)

    obs_comb_file = '{}{:05d}{}'.format(global_cfg['observations-folder'], i, '.nc')

    if os.path.isfile(obs_comb_file):
        print t.name + ": " + obs_comb_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating observation combination task {}".format(t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    # Select input files based on the search month range
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Append the data folder prefix and the file format suffix
    in_files = ['{}{}{}'.format(global_cfg['observations-folder'], month, '.nc') for month in months]

    # Calculate the indices for starts and counts
    index_starts = []; index_counts = []

    for month in months:
        [starts, counts] = get_indices('observations', month, i, files_dims, global_cfg)
        index_starts.extend(starts)
        index_counts.extend(counts)

    t.arguments = [
        '--type', 'Observations',
        '--out', obs_comb_file,
        '--along', 1, # Appending along the dimension times
        '--verbose', stage_cfg['args']['verbose'],
    ]

    t.arguments.append('--in'); t.arguments.extend(in_files)
    t.arguments.append('--start'); t.arguments.extend(index_starts)
    t.arguments.append('--count'); t.arguments.extend(index_counts)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t