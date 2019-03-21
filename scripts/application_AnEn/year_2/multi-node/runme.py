import os
import sys
import yaml
import argparse
from radical.entk import Pipeline, Stage, AppManager
from helpers.utils import get_files_dims, check_empty, expand_tilde
from helpers.task_sim_calc import task_sim_calc
from helpers.task_analog_select import create_analog_select_task
from helpers.task_combine import task_combine

os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://entk:entk123@dbh63.mlab.com:27637/anen'

# Keep profiling information
os.environ['RADICAL_PILOT_PROFIL'] = 'True'
os.environ['RADICAL_PROFILE'] = 'True'

# os.environ['RADICAL_ENTK_VERBOSE'] = 'REPORT'
os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

def create_pipelines(wcfg):
    """
    This function creates a Pipeline with the given configuration dictionary.

    :param wcfg: The configuration dictionary.
    :return: A Pipeline object.
    """
    # Get dimensions of all forecast and observation files
    files_dims = get_files_dims(wcfg['global'])

    p = Pipeline()

    # Create the stage for similarity calculator tasks
    s = Stage()
    s.name = 'stage-sim-calc'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = task_sim_calc(i, stage_cfg, wcfg['global'], files_dims)
        if t:
            print "Adding task {}".format(t.name)
            s.add_tasks(t)

    if len(s.tasks) != 0:
        print "Adding stage {}".format(s.name)
        p.add_stages(s)

    # Create the stage for analog selector tasks
    s = Stage()
    s.name = 'stage-analog-select'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = create_analog_select_task(i, stage_cfg, wcfg['global'], files_dims)
        if t:
            print "Adding task {}".format(s.name)
            s.add_tasks(t)

    if len(s.tasks) != 0:
        print "Adding stage {}".format(s.name)
        p.add_stages(s)

    # Create the stage for combining analogs
    s = Stage()
    s.name = "stage-analog-combine"
    stage_cfg = wcfg[s.name]

    t = task_combine('Analogs', 0, stage_cfg, wcfg['global'], 0, files_dims)
    if t:
        print "Adding task {}".format(s.name)
        s.add_tasks(t)

    if len(s.tasks) != 0:
        print "Adding stage {}".format(s.name)
        p.add_stages(s)

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
        rcfg = yaml.load(fp, Loader=yaml.FullLoader)

    with open(args.wcfg, 'r') as fp:
        wcfg = yaml.load(fp, Loader=yaml.FullLoader)

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
