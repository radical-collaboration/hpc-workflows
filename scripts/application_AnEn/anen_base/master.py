import os, sys
import rpy2
import rpy2.robjects as robjects
import traceback

from glob import glob
from rpy2.robjects.packages import STAP
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager, Profiler

'''
EnTK 0.6 script - Analog Ensemble application

In this example, we intend to execute 32 canalogs tasks each using 4 cores and different station IDs on Stampede
with a total resource reservation of 32 cores. Once completed, we determine the execution time of the
tasks using the EnTK profiler.
'''


resource_key = {
    
                    'xsede.stampede': 
                                    [   'module load netcdf',    
                                        'export PATH=/home1/04672/tg839717/git/CAnalogsV2/build:$PATH']
                                ,

                    'xsede.supermic': 
                                    [   'module load netcdf',      
                                        'module load gcc',
                                        'export PATH=/home/whu/git/CAnalogsV2/install/bin:$PATH']
                                

                }


def test_initial_config(d):

    possible_keys = [   'file.forecast', 'file.observation','output.AnEn',
                        'stations.ID', 'cores', 'test.ID.start', 'test.ID.end',
                        'train.ID.start', 'train.ID.end', 'rolling',
                        'members.size','num.flts','num.times','num.parameters',
                        'num.stations_per_chunk','num.stations'
                    ]

    all_ok = True

    for keys in possible_keys:

        if keys not in d:

            print 'Expected key %s not in initial_config dictionary'%keys
            all_ok = False


    return all_ok


def process_initial_config(initial_config):

    initial_config['stations.ID'] = ["%s"%str(int(k)) for k in list(initial_config['stations.ID'])]

    possible_keys = [   'file.forecast', 'file.observation','output.AnEn',
                        'cores', 'test.ID.start', 'test.ID.end',
                        'train.ID.start', 'train.ID.end', 'rolling',
                        'members.size','num.flts','num.times','num.parameters',
                        'num.stations_per_chunk','num.stations'
                    ]

    for keys in possible_keys:
        initial_config[keys] = initial_config[keys][0]


    for key, val in initial_config.iteritems():
        if type(val) not in [str,int, float, list]:
            sys.exit(1)


    return initial_config


if __name__ == '__main__':



    # Our application currently will contain only one pipeline
    p = Pipeline()


    # -------------------------- Stage 1 ---------------------------------------
    # Read initial configuration from R function
    with open('setup.R', 'r') as f:
        R_code = f.read()
    initial_config = STAP(R_code, 'initial_config')
    config = initial_config.initial_config(False)
    initial_config = dict(zip(config.names, list(config)))


    if not test_initial_config(initial_config):
        sys.exit(1)

    initial_config = process_initial_config(initial_config)
    

    #################################################
    # additional conversion from for the dictionary #
    #################################################

    
    # First stage corresponds to the AnEn computation
    s1 = Stage()

    # List to catch all the uids of the AnEn tasks
    anen_task_uids = list()

    stations_subset = list()

    for ind in range(10):

        # Create a new task
        t1 = Task()
        # task executable
        t1.executable    = ['canalogs']       
        # All modules to be loaded for the executable to be detected
        t1.pre_exec      = resource_key['xsede.supermic']
        # Number of cores for this task
        t1.cores         = int(initial_config['cores'])
        # List of arguments to the executable      
        t1.arguments     = [ '-N','-p',
                            '--forecast-nc', initial_config['file.forecast'],
                            '--observation-nc', initial_config['file.observation'],
                            '-o', './' + os.path.basename(initial_config['output.AnEn']), '--stations-ID',
                            '--start-forecasts','0 %s 0 0'%initial_config['stations.ID'][ind*10],
                            '--count-forecasts','%s %s %s %s'%( initial_config['num.parameters'],
                                                                # TODO: Needs to be fixed for case when number of stations is not multiple of 10
                                                                initial_config['num.stations.per.chunk'],
                                                                initial_config['num.times'],
                                                                initial_config['num.flts']
                                                            ),  
                            '--stride-forecasts','1 1 1 1',
                            '--start-observations','0 %s 0 0'%initial_config['stations.ID'][ind*10],
                            '--count-observations','1 %s %s %s'%(
                                                                # TODO: Needs to be fixed for case when number of stations is not multiple of 10
                                                                initial_config['num.stations.per.chunk'],
                                                                initial_config['num.times'],
                                                                initial_config['num.flts'],
                                                            )
                            '--stride-observations','1 1 1 1']

        t1.arguments.extend(initial_config['stations.ID'][ind*10:(ind+1)*10])

        t1.arguments.extend([
                            '--number-of-cores', int(initial_config['cores']),
                            '--test-ID-start', int(initial_config['test.ID.start']),
                            '--test-ID-end', int(initial_config['test.ID.end']),
                            '--train-ID-start', int(initial_config['train.ID.start']),
                            '--train-ID-end', int(initial_config['train.ID.end']),
                            '--rolling', int(initial_config['rolling']),
                            '--members-size',int(initial_config['members.size'])])

        #t1.copy_output_data = ['{0} > /home/vivek91/{1}-starts-{2}-ends-{3}.nc'.format( os.path.basename(initial_config['output.AnEn'],
        #                                                                            os.path.basename(initial_config['output.AnEn']).split('.')[0],
        #                                                                            initial_config['stations.ID'][ind*10],
        #                                                                            initial_config['stations.ID'][(ind+1)*10]), 
        #                                                                            ind)]

        if ind==1:
            stations_subset = initial_config['stations.ID'][ind*10:(ind+1)*10]

        anen_task_uids.append(t1.uid)

        # Add this task to our stage
        s1.add_tasks(t1)

    
    # Add the stage to our pipeline
    p.add_stages(s1)
    # --------------------------------------------------------------------------


    # -------------------------- Stage 2 ---------------------------------------

    s2 = Stage()

    t2 = Task()
    t2.executable       = ['canalogs']
    t2.pre_exec         = resource_key['xsede.supermic']
    t2.arguments        = [ '-C',
                            '--file-new','%s'%len(initial_config['output.AnEn']),
                            '--files-from']

    t2.link_input_data = []

    for ind in range(10):
        t2.link_input_data += ['$Pipeline_%s_Stage_%s_Task_%s/%s-starts-%s-ends-%s.nc'%(
                                                            p.uid,
                                                            s1.uid,
                                                            anen_task_uids[ind],
                                                            os.path.basename(initial_config['output.AnEn']).split('.')[0],
                                                            initial_config['stations.ID'][ind*10],
                                                            initial_config['stations.ID'][(ind+1)*10])]

        t2.arguments.append('%s-starts-%s-ends-%s.nc'%(
                                                        os.path.basename(initial_config['output.AnEn']).split('.')[0],
                                                        initial_config['stations.ID'][ind*10],
                                                        initial_config['stations.ID'][(ind+1)*10])
                                                    )
                                                

    t2.arguments.extend(analog_files)



    # --------------------------------------------------------------------------

    # -------------------------- Stage 3 ---------------------------------------
    

    # Third stage corresponds to evaluation of interpolated data
    s3 = Stage()

    t3 = Task()
    t3.executable    = ['python']
    t3.pre_exec      =  [   'module load python/2.7.7/GCC-4.9.0',
                            'source $HOME/ve_rpy2/bin/activate',
                            'module load r',
                            'module load netcdf']
    t3.cores         = 1
    t3.arguments     = [ 'evaluation.py', 
                        '--file_observation', initial_config['file.observation'],
                        '--file_AnEn', initial_config['output.AnEn'],
                        '--stations_ID', stations_subset,
                        '--test_ID_start', initial_config['test.ID.start'],
                        '--test_ID_end', initial_config['test.ID.end'],
                        '--nflts', initial_config['num.flts'],
                        '--nrows', initial_config['nrows'],
                        '--ncols', initial_config['ncols']
                    ]
    t3.upload_input_data = ['./evaluation.py', './evaluation.R']
    t3.link_input_data = ['$Pipeline_%s_$Stage_%s_$Task_%s/%s'%(
                                                                p.uid,
                                                                s2.uid,
                                                                t2.uid,
                                                                initial_config['output.AnEn']
                                                            )]
    

    s3.add_tasks(t3)

    p.add_stages(s3)
    # --------------------------------------------------------------------------


    # Create a dictionary to describe our resource request
    res_dict = {

            'resource': 'xsede.supermic',
            'walltime': 60,
            'cores': 180,
            'project': 'TG-MCB090174',
            #'queue': 'development',
            'schema': 'gsissh'

    }

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        # Create an Application Manager for our application
        appman = AppManager()

        # Assign the resource manager to be used by the application manager
        appman.resource_manager = rman

        # Assign the workflow to be executed by the application manager
        appman.assign_workflow(set([p]))

        # Run the application manager -- blocking call
        appman.run()


        # Once completed, use EnTK profiler to get the time between 'SCHEDULING' and 'EXECUTING' states for all
        # tasks. This is the execution time of the tasks as seen by EnTK.
        #p = Profiler()
        #print 'Task uids: ', task_uids
        #print 'Total execution time for all tasks: ', p.duration(objects = task_uids, states=['SCHEDULING', 'EXECUTED'])

    except Exception, ex:

        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()

    finally:

        profs = glob('./*.prof')
        for f in profs:
            os.remove(f)
