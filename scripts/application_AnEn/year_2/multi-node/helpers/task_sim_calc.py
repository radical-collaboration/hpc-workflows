from utils import extract_month, get_indices
from radical.entk import Task
from pprint import pprint
import os


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

    sim_file = '{}{:05d}.nc'.format(global_cfg['sims-folder'], i)

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

    # Calculate the indices for starts and counts
    [test_starts, test_counts] = get_indices('forecasts', test_month, i, files_dims, global_cfg)

    t.arguments = [
        '--test-forecast-nc', global_cfg['test-forecast-nc'],
        '--similarity-nc', sim_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--config', global_cfg['config'],
        '--obs-along', 2,
        '--search-along', 2,
        '--max-num-sims', stage_cfg['args']['max-num-sims'],

        '--config', "{}search-{:05d}.cfg".format(global_cfg['config-folder'], i),
        '--config', "{}obs-{:05d}.cfg".format(global_cfg['config-folder'], i),
    ]
    
    # Add list arguments
    t.arguments.append('--test-start'); t.arguments.extend(test_starts)
    t.arguments.append('--test-count'); t.arguments.extend(test_counts)

    if global_cfg['print-help']:
        t.arguments.append('-h')

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
