import os
import sys
import yaml
import argparse
from radical.entk import Pipeline, Stage, Task, AppManager



def create_sd_calc_task(i, task_desc):

    t = Task()
    t.name = 'task-%s'%i
    t.pre_exec = task_desc['pre_exec']
    t.executable = task_desc['executable']
    t.cpu_threads = {
        'processes': task_desc['cpu']['processes'],
        'process_type': task_desc['cpu']['process_type'],
        'threads_per_process': task_desc['cpu']['threads_per_process'],
        'thread_type': task_desc['cpu']['thread_type'],
    }
    t.arguments = [
        # The following arguments solely depend on the configuration file
        '--in', task_desc['args']['in'],
        '--out', task_desc['args']['out'],
        '--verbose', task_desc['args']['verbose'],

        # The following arguments depend on the configuration file and the task number i
        '--start', task_desc['args']['start'],
        '--count', task_desc['args']['count'],
    ]

    t.link_input_data = []
    t.copy_output_data = []

    return t



def create_sim_calc_task(i, task_desc):

    t = Task()
    t.name = 'task-%s'%i
    t.pre_exec = task_desc['pre_exec']
    t.executable = task_desc['executable']
    t.cpu_threads = {
                        'processes': task_desc['cpu']['processes'],
                        'process_type': task_desc['cpu']['process_type'],
                        'threads_per_process': task_desc['cpu']['threads_per_process'],
                        'thread_type': task_desc['cpu']['thread_type'],
                    }
    t.arguments = [
        # The following arguments solely depend on the configuration file
                    '--test-forecast-nc', task_desc['args']['test-forecast-nc'],
                    '--search-forecast-nc', task_desc['args']['search-forecast-nc'],
                    '--observation-nc', task_desc['args']['observation-nc'],
                    '--similarity-nc', task_desc['args']['similarity-nc'],
                    '--verbose', task_desc['args']['verbose'],
                    '--time-match-mode', task_desc['args']['time-match-mode'],
                    '--observation-id', task_desc['args']['observation-id'],
                    '--sds-nc', task_desc['args']['sds-nc'],

        # The following arguments depend on the configuration file and the task number i
                    '--test-start', task_desc['args']['test-start'],
                    '--test-count', task_desc['args']['test-count'],
                    # '--search-start', task_desc['args']['search-start'],
                    # '--search-count', task_desc['args']['search-count'],
                    # '--obs-start', task_desc['args']['obs-start'],
                    # '--obs-count', task_desc['args']['obs-count'],
                    # '--sds-start', task_desc['args']['sds-start'],
                    # '--sds-count', task_desc['args']['sds-count']
                ]

    t.link_input_data = []
    t.copy_output_data = []

    return t



def create_analog_select_task(i, task_desc):
    t = Task()
    t.name = 'task-%s'%i
    t.pre_exec = task_desc['pre_exec']
    t.executable = task_desc['executable']
    t.cpu_threads = {
                        'processes': task_desc['cpu']['processes'],
                        'process_type': task_desc['cpu']['process_type'],
                        'threads_per_process': task_desc['cpu']['threads_per_process'],
                        'thread_type': task_desc['cpu']['thread_type'],
                    }
    t.arguments = [
                    '--config', task_desc['args']['config'],
                    '--similarity-nc', task_desc['args']['similarity-nc'],
                    '--observation-nc', task_desc['args']['observation-nc'],
                    '--mapping-txt', task_desc['args']['mapping-txt'],
                    '--analog-nc', task_desc['args']['analog-nc'],
                    '--members', task_desc['args']['members'],
                    '--verbose', task_desc['args']['verbose'],
                    '--observation-id', task_desc['args']['observation-id'],
                    '--obs-start', task_desc['args']['obs-start'],
                    '--obs-count', task_desc['args']['obs-count'],
                    '--quick', task_desc['args']['quick'],
                    '--extend-obs', task_desc['args']['extend-obs'],
                    '--real-time', task_desc['args']['real-time'],
                ]

    t.link_input_data = []
    t.copy_output_data = []

    return t



def create_pipelines(wcfg):
    p = Pipeline

    # Create first stage for similarity calculator tasks
    s1 = Stage()
    s1.name = 'stage-1'
    stage_cfg = wcfg['stage_sim_cal']

    for i in range(stage_cfg['task_count']):
        t = create_sim_calc_task(i, stage_cfg['task_desc'])
        s1.add_tasks(t)

    p.add_stages(s1)

    # Create second stage for analog selector tasks
    s2 = Stage()
    s2.name = 'stage-2'
    stage_cfg = wcfg['stage_analog_select']

    for i in range(stage_cfg['task_count']):
        t = create_analog_select_task(i, stage_cfg['task_desc'])
        s2.add_tasks(t)

    p.add_stages(s2)

    return p



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--wcfg', help='path to workflow cfg file', required=False, default='./workflow_cfg.yml')
    parser.add_argument('--rcfg', help='path to resource cfg file', required=False, default='./resource_cfg.yml')

    args = parser.parse_args()
    if not os.path.isfile(args.wcfg):
        print '%s does not exist'%args.wcfg
        sys.exit(1)

    if not os.path.isfile(args.rcfg):
        print '%s does not exist'%args.rcfg
        sys.exit(1)

    with open(args.rcfg,'r') as fp:
        rcfg = yaml.load(fp)

    with open(args.wcfg,'r') as fp:
        wcfg = yaml.load(fp)

    amgr = AppManager(  hostname=rcfg['rabbitmq']['hostname'], 
                        port=rcfg['rabbitmq']['port'])

    res_desc = {
            'resource': rcfg['resource_desc']['name'],
            'walltime': rcfg['resource_desc']['walltime'],
            'cpus': rcfg['resource_desc']['cpus'],
            'queue': rcfg['resource_desc']['queue'],
            'project': rcfg['resource_desc']['project']
        }
    
    amgr.resource_desc = res_desc

    pipelines = create_pipelines(wcfg)
    if not isinstance(pipelines, list):
        pipelines = [pipelines]

    amgr.workflow = pipelines

    # amgr.run()