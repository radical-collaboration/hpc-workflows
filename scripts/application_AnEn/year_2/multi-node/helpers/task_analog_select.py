from radical.entk import Task
from pprint import pprint
import os

def create_analog_select_task(i, stage_cfg, global_cfg):
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
        '--observation-nc', '{}{:05d}{}'.format(global_cfg['observations-folder'], i, '.nc'),
        '--mapping-txt', global_cfg['mapping-file'],
        '--analog-nc', analog_file,
    ]

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
