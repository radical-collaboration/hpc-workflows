import os
import sys
import yaml
import datetime
import argparse
from pprint import pprint
from radical.entk import Pipeline, Stage, Task, AppManager


def get_months_between(start, end, format="%Y%m", reverse=False):
    start = datetime.datetime.strptime(start, format)
    end = datetime.datetime.strptime(end, format)

    # Add one day to the end to make the range inclusive
    dates = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days + 1)]
    dates_str = [i.strftime(format) for i in dates]

    # Only keep the unique strings
    months = list(set(dates_str))
    months.sort(reverse=reverse)

    return months


def task_sd_calc(i, stage_cfg, global_cfg):
    t = Task()
    t.name = 'task-sd-calc-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }

    # Select input files based on the search month range
    months = get_months_between(global_cfg['search-month-start'], global_cfg['search-month-end'])

    # Append the data folder prefix and the file format suffix
    in_files = ['{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc') for month in months]
    out_file = '{}{}{}'.format(global_cfg['sds-folder'], t.name, '.nc')

    t.arguments = [
        '--in', in_files,
        '--out', out_file,
        '--verbose', stage_cfg['args']['verbose'],
        # '--start', stage_cfg['args']['start'],
        # '--count', stage_cfg['args']['count'],
    ]

    t.link_input_data = []
    t.copy_output_data = []

    pprint(t.to_dict())

    return t


def task_sim_calc(i, month, stage_cfg, global_cfg):
    t = Task()
    t.name = 'task-sims-calc-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }
    t.arguments = [
        '--test-forecast-nc', stage_cfg['args']['test-forecast-nc'],
        '--search-forecast-nc', '{}{}{}'.format(global_cfg['forecasts-folder'], month, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--similarity-nc', '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc'),
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],
        '--sds-nc', '{}task-sd-calc-{:05d}{}'.format(global_cfg['sds-folder'], i, '.nc')

        #'--test-start', stage_cfg['args']['test-start'],
        #'--test-count', stage_cfg['args']['test-count'],
        # '--search-start', stage_cfg['args']['search-start'],
        # '--search-count', stage_cfg['args']['search-count'],
        # '--obs-start', stage_cfg['args']['obs-start'],
        # '--obs-count', stage_cfg['args']['obs-count'],
        # '--sds-start', stage_cfg['args']['sds-start'],
        # '--sds-count', stage_cfg['args']['sds-count']
    ]

    t.link_input_data = []
    t.copy_output_data = []

    pprint(t.to_dict())
    return t


def create_analog_select_task(i, month, stage_cfg, global_cfg):
    t = Task()
    t.name = 'task-analog-select-{:05d}'.format(i)
    t.pre_exec = stage_cfg['pre-exec']
    t.executable = stage_cfg['executable']
    t.cpu_threads = {
        'processes': stage_cfg['cpu']['processes'],
        'process-type': stage_cfg['cpu']['process-type'],
        'threads-per-process': stage_cfg['cpu']['threads-per-process'],
        'thread-type': stage_cfg['cpu']['thread-type'],
    }
    t.arguments = [
        '--quick', stage_cfg['args']['quick'],
        '--members', stage_cfg['args']['members'],
        '--verbose', stage_cfg['args']['verbose'],
        '--observation-id', global_cfg['observation-id'],

        '--similarity-nc', '{}{}-{:05d}{}'.format(global_cfg['sims-folder'], month, i, '.nc'),
        '--observation-nc', '{}{}{}'.format(global_cfg['observations-folder'], month, '.nc'),
        '--analog-nc', '{}{}-{:05d}{}'.format(global_cfg['analogs-folder'], month, i, '.nc'),

        #'--obs-start', stage_cfg['args']['obs-start'],
        #'--obs-count', stage_cfg['args']['obs-count'],
    ]

    t.link_input_data = []
    t.copy_output_data = []
    pprint(t.to_dict())

    return t


def create_pipelines(wcfg):
    p = Pipeline()

    # Create the stage for standard deviation calculator tasks
    s = Stage()
    s.name = 'stage-sd-calc'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        t = task_sd_calc(i, stage_cfg, wcfg['global'])
        s.add_tasks(t)

    p.add_stages(s)

    # Create the stage for similarity calculator tasks
    s = Stage()
    s.name = 'stage-sim-calc'
    stage_cfg = wcfg[s.name]

    # Get the number of forecast files to be used. This is the number of months specified.
    months = get_months_between(wcfg['global']['search-month-start'], wcfg['global']['search-month-end'])

    for i in range(wcfg['global']['task-count']):
        for j in range(len(months)):
            t = task_sim_calc(i, months[j], stage_cfg, wcfg['global'])
            s.add_tasks(t)

    p.add_stages(s)

    # Create the stage for analog selector tasks
    s = Stage()
    s.name = 'stage-analog-select'
    stage_cfg = wcfg[s.name]

    for i in range(wcfg['global']['task-count']):
        for j in range(len(months)):
            t = create_analog_select_task(i, months[j], stage_cfg, wcfg['global'])
            s.add_tasks(t)

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
        rcfg = yaml.load(fp)

    with open(args.wcfg, 'r') as fp:
        wcfg = yaml.load(fp)

    with open('./resource_cfg.yml', 'r') as fp:
        rcfg = yaml.load(fp)

    with open('./workflow_cfg.yml', 'r') as fp:
        wcfg = yaml.load(fp)

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

    #amgr.run()
