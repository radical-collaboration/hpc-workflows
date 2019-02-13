from radical.entk import Task
from utils import get_indices
from pprint import pprint

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

    if global_cfg['print-progress']:
        print "Creating analog selection task {}".format(t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
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
    ]

    # Add list arguments
    t.arguments.append('--obs-start'); t.arguments.extend(index_starts)
    t.arguments.append('--obs-count'); t.arguments.extend(index_counts)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t