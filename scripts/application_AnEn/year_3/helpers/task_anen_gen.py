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

    out_file = '{}anen_task-{:05d}.nc'.format(global_cfg['out-folder'], i)

    if os.path.isfile(out_file):
        print(t.name + ": " + out_file + " already exists. Skip generating this file!")
        return False

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    t.arguments = [
        '--config', "/glade/u/home/wuh20/github/hpc-workflows/scripts/application_AnEn/year_3/anen_shared_config.cfg",
        '--out', out_file,
    ]
    
    if global_cfg['print-help']:
        t.arguments.append('-h')

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
