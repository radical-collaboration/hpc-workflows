from radical.entk import Task
from pprint import pprint
import os
import re

def task_sim_combine(i, stage_cfg, global_cfg):
    """
    This function combines the similarity files along time for a specific geographic region.

    :param i: The task number.
    :param stage_cfg: The configuration dictionary for this stage.
    :param global_cfg: The global configuration dictionary.
    :return: A Task object.
    """

    t = Task()
    t.name = 'task-sim_combine-{:05d}'.format(i)

    sim_comb_file = '{}{:05d}{}'.format(global_cfg['sims-folder'], i, '.nc')

    if os.path.isfile(sim_comb_file):
        print t.name + ": " + sim_comb_file + " already exists. Skip generating this file!"
        return False

    if global_cfg['print-progress']:
        print "Creating similarity combination task {}".format(t.name)

    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_reqs = {
        'processes': stage_cfg['cpu']['processes'],
        'process_type': stage_cfg['cpu']['process-type'],
        'threads_per_process': stage_cfg['cpu']['threads-per-process'],
        'thread_type': stage_cfg['cpu']['thread-type'],
    }

    # This pattern matches similarity files for this specific geographic region for all months.
    pattern = r'[0-9]{{6}}-{:05d}\.nc'.format(i)
    sims_in = ['{}{}'.format(global_cfg['sims-folder'], file) for file in os.listdir(global_cfg['sims-folder']) if re.match(pattern, file)]

    t.arguments = [
        '--type', 'Similarity',
        '--out', sim_comb_file,
        '--along', 3, # Appending along the dimension num_entries
        '--verbose', stage_cfg['args']['verbose'],
    ]

    t.arguments.append('--in'); t.arguments.extend(sims_in)

    if global_cfg['print-help']:
        t.arguments.extend(['-h'])

    t.link_input_data = []
    t.copy_output_data = []

    if global_cfg['print-tasks-only']:
        pprint(t.to_dict())

    return t
