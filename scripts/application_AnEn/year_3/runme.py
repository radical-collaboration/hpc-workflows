#!/home/weiming/venv/bin/python
import os
import sys
import yaml
import argparse
from helpers.task_anen_gen import task_anen_gen
from radical.entk import Pipeline, Stage, AppManager

os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://hpcworkflows:hpcw0rkf70w@two.radical-project.org:27017/hpcworkflows'

# Keep profiling information
os.environ['RADICAL_PILOT_PROFIL'] = 'True'
os.environ['RADICAL_PROFILE'] = 'True'

# Succinct output
# os.environ['RADICAL_ENTK_VERBOSE'] = 'REPORT'

# Detailed output
# os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'
os.environ['RADICAL_ENTK_VERBOSE'] = 'DEBUG'


def pipeline_analogs(wcfg, rcfg):
    """
    This function creates a Pipeline with the given configuration dictionary.

    :param wcfg: The configuration dictionary.
    :return: A Pipeline object.
    """
    p = Pipeline()

    # Create the stage for similarity calculator tasks
    s = Stage()
    s.name = 'stage-analogs'
    stage_cfg = wcfg['stage-analogs']

    for i in range(wcfg['global']['task-count']):

        t = task_anen_gen(i, stage_cfg, wcfg['global'])

        if t:
            s.add_tasks(t)
            print(("Adding task {}: {}".format(len(s.tasks), t.name)))
        
    if len(s.tasks) != 0:
        print("Adding stage {}.".format(s.name))
        p.add_stages(s)

    return (p)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--wcfg', help='path to workflow cfg file', required=False, default='./workflow_cfg.yml')
    parser.add_argument('--rcfg', help='path to resource cfg file', required=False, default='./resource_cfg_stampede.yml')

    args = parser.parse_args()
    if not os.path.isfile(args.wcfg):
        print('%s does not exist' % args.wcfg)
        sys.exit(1)

    if not os.path.isfile(args.rcfg):
        print('%s does not exist' % args.rcfg)
        sys.exit(1)

    with open(args.rcfg, 'r') as fp:
        rcfg = yaml.load(fp, Loader=yaml.FullLoader)

    with open(args.wcfg, 'r') as fp:
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

    pipelines = pipeline_analogs(wcfg, rcfg)
    if not isinstance(pipelines, list):
        pipelines = [pipelines]

    amgr.workflow = pipelines

    if wcfg['global']['print-tasks-only']:
        print("Print tasks created only. Nothing has been run.")
    else:
        amgr.run()
