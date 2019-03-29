from radical.entk import Task
from pprint import pprint
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

    sim_file = '{}sims-{:05d}.nc'.format(global_cfg['sims-folder'], i)
    anen_file = '{}analogs-{:05d}.nc'.format(global_cfg['analogs-folder'], i)

    if os.path.isfile(sim_file):
        print t.name + ": " + sim_file + " already exists. Skip generating this file!"
        return False

    if os.path.isfile(anen_file):
        print t.name + ": " + anen_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating analog generation task {}".format(t.name)

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
        '--analog-nc', anen_file,
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--obs-along', 2,
        '--test-along', 2,
        '--search-along', 2,
        '--members', stage_cfg['args']['members'],
        '--max-num-sims', stage_cfg['args']['max-num-sims'],

        '--config', global_cfg['weight-config'],
        '--config', "{}test-{:05d}.cfg".format(global_cfg['config-folder'], i),
        '--config', "{}search-{:05d}.cfg".format(global_cfg['config-folder'], i),
        '--config', "{}obs-{:05d}.cfg".format(global_cfg['config-folder'], i),
    ]
    
    if global_cfg['print-help']:
        t.arguments.append('-h')

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
