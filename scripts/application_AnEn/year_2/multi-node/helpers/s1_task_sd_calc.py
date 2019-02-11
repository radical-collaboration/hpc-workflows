from radical.entk import Task
from utils import get_months_between, get_indices
from pprint import pprint


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

    if global_cfg['print-progress']:
        print "Creating standard deviation task {}".format(t.name)

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
        '--out', out_file,
        '--verbose', stage_cfg['args']['verbose'],
    ]

    # Add list arguments
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