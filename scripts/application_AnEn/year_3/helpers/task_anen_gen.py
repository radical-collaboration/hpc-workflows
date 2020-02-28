from radical.entk import Task
from pprint import pprint
import numpy
import os


def task_anen_gen(i, stage_cfg, global_cfg):
    """
    This function creates an analog generation task for the specified task number.

    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-anen-gen-{:05d}'.format(i)

    # The output file will be appended with the current task ID
    out_file = '{}anen_task-{:05d}.nc'.format(global_cfg['out-folder'], i)

    # Calculate the station indices assigned to this task
    total_grid = range(global_cfg['grid-count'] - 1)
    stations_index = numpy.array_split(total_grid, global_cfg['task-count'])[i]

    # Check if the output file exists
    if os.path.isfile(out_file):
        print(t.name + ": " + out_file + " already exists. Skip generating this file!")
        return False

    t.executable = stage_cfg['executable']
    t.pre_exec = stage_cfg['pre-exec']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    t.arguments = [
        '--config', global_cfg['shared-config'],
        '--stations-index'] + [str(x) for x in stations_index] + \
        ['--out', out_file]

    t.link_input_data = ["$SHARED/{}".format(global_cfg['shared-config'])]
    
    if global_cfg['print-help']:
        t.arguments.append('-h')

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
