# This is the integration test for Analog Ensemble and Ensemble Toolkit on Cheyenne supercomputer.

from radical.entk import Pipeline, Stage, Task, AppManager
import os

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_REPORT'] = 'True'

res_dict = {
        #'resource': 'xsede.wrangler',
        'resource': 'xsede.stampede',
        'walltime': 5,
        'cpus': 5,
        'project': 'TG-MCB090174',
        'schema': 'gsissh'}

if __name__ == "__main__":

    # Create a Pipeline object
    p = Pipeline()

    # Create a Stage object
    s = Stage()

    # Create a Tastk object
    t = Task()
    t.name = 'test-task'
    t.executable = ['~/github/AnalogsEnsemble/output/bin/similarityCalculator']

    s.add_tasks(t)
    p.add_stages(s)

    # Create Application manager
    appman = AppManager(hostname='two.radical-project.org', port=33239)

    appman.resource_desc = res_dict

    appman.workflow = set([p])

    appman.run()
