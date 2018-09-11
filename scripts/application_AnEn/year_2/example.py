from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager
import os, sys

# ------------------------------------------------------------------------------
# Set default verbosity

if not os.environ.get('RADICAL_ENTK_VERBOSE'):
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

if not os.environ.get('RADICAL_PILOT_DBURL'):
    os.environ['RADICAL_PILOT_DBURL'] = "mongodb://138.201.86.166:27017/ee_exp_4c"

CUR_STAGE = 1

def generate_pipeline():
    
    def func_condition():

        global CUR_STAGE
    
        if CUR_STAGE < MAX_STAGES:
            CUR_STAGE += 1
            return True

        return False

    def func_on_true():

        global CUR_STAGE

        s = Stage()

        for i in range(16):
            t = Task()    
            t.pre_exec = ['export PATH=/home/vivek91/tools/stress-ng-0.09.04:$PATH']
            t.executable = ['stress-ng']   
            t.arguments = [ '-c', '20', '-t', str(duration)] 
            t.cores = 20

            # Add the Task to the Stage
            s.add_tasks(t)

        # Add post-exec to the Stage
        s.post_exec = {
                       'condition': func_condition,
                       'on_true': func_on_true,
                       'on_false': func_on_false
                    }

        p.add_stages(s)

    def func_on_false():
        print 'Done'

    # Create a Pipeline object
    p = Pipeline()

    # Create a Stage object 
    s1 = Stage()

    for i in range(16):

        t1 = Task()    
        t1.pre_exec = ['export PATH=/home/vivek91/tools/stress-ng-0.09.04:$PATH']
        t1.executable = ['stress-ng']   
        t1.arguments = [ '-c', '20', '-t', str(duration)]  
        t1.cores = 20

        # Add the Task to the Stage
        s1.add_tasks(t1)

    # Add post-exec to the Stage
    s1.post_exec = {
                       'condition': func_condition,
                       'on_true': func_on_true,
                       'on_false': func_on_false
                   }

    # Add Stage to the Pipeline
    p.add_stages(s1)    

    return p

if __name__ == '__main__':

    duration = int(sys.argv[1])
    MAX_STAGES = int(sys.argv[2])

    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

            'resource': 'xsede.supermic',
            'walltime': ((duration*(MAX_STAGES+1))/60) + 20,
            'cores': 17*20,
            'project': 'TG-MCB090174',
            'access_schema': 'gsissh',
            'queue': 'hybrid'
    }

    # Create Resource Manager object with the above resource description
    rman = ResourceManager(res_dict)

    # Create Application Manager
    appman = AppManager(port=33076)

    # Assign resource manager to the Application Manager
    appman.resource_manager = rman

    p = generate_pipeline()
    
    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.assign_workflow(set([p]))

    # Run the Application Manager
    appman.run()
