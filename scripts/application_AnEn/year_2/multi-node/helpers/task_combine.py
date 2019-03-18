from utils import get_months_between, get_indices
from radical.entk import Task
from pprint import pprint
import os
import sys


def task_combine(type, i, stage_cfg, global_cfg, along, files_dims):
    """
    This function combines the similarity files along time for a specific geographic region.

    :param type: The file type to aggregate.
    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :param along: Which dimension is appended to.
    :param files_dims: The dimension information generated from the function get_files_dims.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-{}_combine-{:05d}'.format(type, i)

    if type is "Observations":
        data_folder = global_cfg['observations-folder']
    elif type is "Forecasts":
        data_folder = global_cfg['forecasts-folder']
    elif type is "Analogs":
        data_folder = global_cfg['analogs-folder']
    else:
        print "Unsupported file type {}!".format(type)
        sys.exit(1)

    comb_file = '{}{:05d}{}'.format(data_folder, i, '.nc')

    if os.path.isfile(comb_file):
        print t.name + ": " + comb_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating {} combination task {}".format(type, t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    if type is "Observations" or type is "Forecasts":
        # Get the number of forecast files to be used. This is the number of months specified.
        months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

        # Define the similarity files to combine
        files_in = ['{}{}-{:05d}.nc'.format(data_folder, month, i) for month in months]

        # Calculate the indices for starts and counts
        index_starts = []; index_counts = []

        for month in months:
            [starts, counts] = get_indices('forecasts', month, i, files_dims, global_cfg)
            index_starts.extend(starts)
            index_counts.extend(counts)

    elif type is "Analogs":
        # Input files are all the analog files in analogs folder
        files_in = ['{}{:05d}{}'.format(global_cfg['analogs-folder'], i, '.nc') for i in range(global_cfg['task-count'])]

    t.arguments = [
        '--type', type,
        '--out', comb_file,
        '--along', along,  # Appending along the dimension num_entries
        '--verbose', stage_cfg['args']['verbose'],
    ]

    t.arguments.append('--in'); t.arguments.extend(files_in)

    if type is "Observations" or type is "Forecasts":
        t.arguments.append('--start'); t.arguments.extend(index_starts)
        t.arguments.append('--count'); t.arguments.extend(index_counts)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
