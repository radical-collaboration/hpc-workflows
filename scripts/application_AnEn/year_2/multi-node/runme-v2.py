import os
import sys
import yaml
import argparse
from radical.entk import Pipeline, Stage, AppManager
from helpers.utils import get_files_dims, get_months_between, check_empty, expand_tilde
from helpers.task_sim_calc import task_sim_calc_v2
from helpers.task_analog_select import create_analog_select_task
from helpers.task_combine import task_combine

os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://entk:entk123@dbh63.mlab.com:27637/anen'

def create_pipelines(wcfg):
    """
    This function creates a Pipeline with the given configuration dictionary.

    :param wcfg: The configuration dictionary.
    :return: A Pipeline object.
    """

    # Get dimensions of all forecast and observation files
    files_dims = get_files_dims(wcfg['global'])

    # Get the number of forecast files to be used. This is the number of months specified.
    months = get_months_between(wcfg['global']['search-month-start'], wcfg['global']['search-month-end'])

    p = Pipeline()

    # Create the stage for reorganizing forecast and observation files
    print "Adding task reorganizing forecast and observation files"
    s = Stage()
    s.name = 'stage-combination'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = task_combine('Forecasts', i, stage_cfg, wcfg['global'], 2, files_dims)
        t = task_combine('Observations', i, stage_cfg, wcfg['global'], 2, files_dims)
        if t: s.add_tasks(t) # Add the task if it is created successfully

    if len(s.tasks) != 0: p.add_stages(s)

    # Create the stage for similarity calculator tasks
    print "Adding task sim calc stage ..."
    s = Stage()
    s.name = 'stage-sim-calc'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = task_sim_calc_v2(i, stage_cfg, wcfg['global'], files_dims)
        if t: s.add_tasks(t) # Add the task if it is created successfully

    if len(s.tasks) != 0: p.add_stages(s)

    # Create the stage for analog selector tasks
    print "Adding task analog select stage ..."
    s = Stage()
    s.name = 'stage-analog-select'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = create_analog_select_task(i, stage_cfg, wcfg['global'])
        if t: s.add_tasks(t) # Add the task if it is created successfully

    if len(s.tasks) != 0: p.add_stages(s)

    # TODO: Create the stage for analog file aggregation

    return p


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--wcfg', help='path to workflow cfg file', required=False, default='./workflow_cfg.yml')
    parser.add_argument('--rcfg', help='path to resource cfg file', required=False, default='./resource_cfg.yml')

    args = parser.parse_args()
    if not os.path.isfile(args.wcfg):
        print '%s does not exist' % args.wcfg
        sys.exit(1)

    if not os.path.isfile(args.rcfg):
        print '%s does not exist' % args.rcfg
        sys.exit(1)

    with open(args.rcfg, 'r') as fp:
        rcfg = yaml.load(fp)

    with open(args.wcfg, 'r') as fp:
        wcfg = yaml.load(fp)

    wcfg = expand_tilde(wcfg)

    check_empty(wcfg['global'])

    amgr = AppManager(hostname=rcfg['rabbitmq']['hostname'],
                      port=rcfg['rabbitmq']['port'])

    res_desc = {
        'resource': rcfg['resource-desc']['name'],
        'walltime': rcfg['resource-desc']['walltime'],
        'cpus': rcfg['resource-desc']['cpus'],
        'queue': rcfg['resource-desc']['queue'],
        'project': rcfg['resource-desc']['project']
    }

    amgr.resource_desc = res_desc

    pipelines = create_pipelines(wcfg)
    if not isinstance(pipelines, list):
        pipelines = [pipelines]

    amgr.workflow = pipelines

    if wcfg['global']['print-tasks-only']:
        print("Print tasks created only. Nothing has been run.")
    else:
        amgr.run()