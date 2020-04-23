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
import os
import sys
import yaml
import argparse

# HPC modules
from radical.entk import AppManager, Pipeline

# Self hosted modules
from Functions import stage_analogs, stage_power

"""
Global environment settings
"""
# The database setting for storing standard output messages
os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://hpcworkflows:hpcw0rkf70w@two.radical-project.org:27017/hpcworkflows'

# Enable profiling information
os.environ['RADICAL_PILOT_PROFIL'] = 'True'
os.environ['RADICAL_PROFILE'] = 'True'

# Set output verbosity
# os.environ['RADICAL_ENTK_VERBOSE'] = 'REPORT'     # Succinct
# os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'       # Detailed
os.environ['RADICAL_ENTK_VERBOSE'] = 'DEBUG'        # Debugging


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ensemble simulation of our PV future')
    parser.add_argument('--workflow', help='path to workflow config file',
                        required=False, default='stampede_workflow_cfg.yaml')
    parser.add_argument('--resource', help='path to resource config file',
                        required=False, default='stampede_resource_cfg.yaml')

    args = parser.parse_args()

    # Expand user tilde
    args.workflow = os.path.expanduser(args.workflow)
    args.resource = os.path.expanduser(args.resource)

    if not os.path.isfile(args.workflow):
        print('%s does not exist' % args.workflow)
        sys.exit(1)

    if not os.path.isfile(args.resource):
        print('%s does not exist' % args.resource)
        sys.exit(1)

    with open(args.resource, 'r') as fp:
        rcfg = yaml.load(fp, Loader=yaml.FullLoader)

    with open(args.workflow, 'r') as fp:
        wcfg = yaml.load(fp, Loader=yaml.FullLoader)

    amgr = AppManager(hostname=rcfg['rabbitmq']['hostname'],
                      port=rcfg['rabbitmq']['port'])

    res_desc = {
        'resource': rcfg['resource-desc']['name'],
        'walltime': rcfg['resource-desc']['walltime'],
        'cpus': rcfg['resource-desc']['cpus'],
        'queue': rcfg['resource-desc']['queue'],
        'project': rcfg['resource-desc']['project'],
        'access_schema': rcfg['resource-desc']['schema']
    }

    amgr.resource_desc = res_desc

    # This shared configuration will be copied to each unit folder
    amgr.shared_data = [wcfg['global']['shared-config']]

    # Add stages
    p = Pipeline()

    s = stage_analogs(wcfg)
    if len(s.tasks) != 0:
        p.add_stages(s)

    p.add_stages(stage_power(wcfg))

    # Add pipelines
    amgr.workflow = [p]

    if wcfg['global']['print-tasks-only']:
        print("Print tasks created only. Nothing has been run.")
    else:
        amgr.run()
