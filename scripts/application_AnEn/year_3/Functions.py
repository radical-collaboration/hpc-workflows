# "`-''-/").___..--''"`-._
#  (`6_ 6  )   `-.  (     ).`-.__.`)   WE ARE ...
#  (_Y_.)'  ._   )  `._ `. ``-..-'    PENN STATE!
#    _ ..`--'_..-_/  /--'_.' ,'
#  (il),-''  (li),'  ((!.-'
#
# Author:
#
#     Weiming Hu <weiming@psu.edu>
#
# Geoinformatics and Earth Observation Laboratory (http://geolab.psu.edu)
# Department of Geography and Institute for CyberScience
# The Pennsylvania State University
#

# Basic modules
from pprint import pprint
import os

# HPC modules
from radical.entk import Task, Stage


def stage_power(wcfg):
    """
    This function create a Stage with the given configuration dictionary for power simulation.
    :param wcfg: The configuration dictionary.
    :return: A Stage object.
    """

    # Initialization
    s = Stage()

    # The stage name should match the dictionary key in the workflow configuration
    s.name = 'stage-power'
    stage_cfg = wcfg[s.name]
    global_cfg = wcfg['global']

    # Extra all domain configuration files
    domain_cfgs = [f for f in os.listdir(global_cfg['subset-config']) if f.endswith('.cfg')]

    for domain_cfg in domain_cfgs:
        t = Task()
        t.name = 'task-power_{}'.format(domain_cfg)
        t.executable = stage_cfg["executable"]
        t.pre_exec = stage_cfg['pre-exec']

        t.cpu_reqs = {
            'processes': stage_cfg['cpu']['processes'],
            'process_type': stage_cfg['cpu']['process-type'],
            'threads_per_process': stage_cfg['cpu']['threads-per-process'],
            'thread_type': stage_cfg['cpu']['thread-type'],
        }

        file_to_process = os.path.join(
            global_cfg['out-folder'], 'analogs_{}.nc'.format(os.path.basename(domain_cfg).split('.')[0]))

        if global_cfg['print-help']:
            t.arguments = ['-h']
        else:
            t.arguments = [
                stage_cfg['python-main'],
                '--map', stage_cfg["map-file"],
                '--scenario', stage_cfg["scenario-file"],
                '--silent', '--solar nrel_numba',
                '--profile', '--profiler simple',
                '--nc', file_to_process,
            ]

        s.add_tasks(t)

        if global_cfg['print-tasks-only']:
            pprint(t.to_dict())

    return s


def stage_analogs(wcfg):
    """
    This function creates a Stage with the given configuration dictionary for analog generation.

    :param wcfg: The configuration dictionary.
    :return: A Stage object.
    """

    # Initialization
    s = Stage()

    # The stage name should match the dictionary key in the workflow configuration
    s.name = 'stage-analogs'
    stage_cfg = wcfg[s.name]
    global_cfg = wcfg['global']

    # Extra all domain configuration files
    domain_cfgs = [f for f in os.listdir(global_cfg['subset-config']) if f.endswith('.cfg')]

    if len(domain_cfgs) == 0:
        raise Exception("No domain subset files (*.cfg) found under {}".format(global_cfg['subset-config']))

    # For each domain subset, a task will be created and added to the current stage
    for domain_cfg in domain_cfgs:
        basename = os.path.basename(domain_cfg).split('.')[0]
        output_file = os.path.join(global_cfg['out-folder'], 'analogs_{}.nc'.format(basename))

        if os.path.exists(output_file):
            print("{} exists. Do not generate this file again [stage analogs]".format(output_file))
            continue
        else:
            t = Task()
            t.name = 'task-analogs_{}'.format(basename)
            t.executable = stage_cfg["executable"]
            t.pre_exec = stage_cfg['pre-exec']

            t.cpu_reqs = {
                'processes': stage_cfg['cpu']['processes'],
                'process_type': stage_cfg['cpu']['process-type'],
                'threads_per_process': stage_cfg['cpu']['threads-per-process'],
                'thread_type': stage_cfg['cpu']['thread-type'],
            }

            if global_cfg['print-help']:
                t.arguments = ['-h']
            else:

                t.link_input_data = [
                    "$SHARED/{}".format(global_cfg['shared-config']),
                    "$SHARED/{}".format(domain_cfg),
                ]

                t.arguments = [
                    '--config', global_cfg['shared-config'], domain_cfg,
                    '--out', output_file,
                ]

            s.add_tasks(t)

            if global_cfg['print-tasks-only']:
                pprint(t.to_dict())

    return s
