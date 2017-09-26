import os, sys
import rpy2
import rpy2.robjects as robjects
import traceback

from rpy2.robjects.packages import importr

from glob import glob
from rpy2.robjects.packages import STAP
#from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager, Profiler

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

    possible_keys = [   'command.exe',
                        'command.verbose',
                        'file.forecasts',
                        'file.observations',
                        'folder.prefix',
                        'folder.accumulate',
                        'folder.output',
                        'folder.raster.anen',
                        'folder.raster.obs',
                        'folder.tmp',
                        'file.pixels.computed',
                        'num.flts',
                        'num.times',
                        'num.times.to.compute',
                        'num.parameters',
                        'ygrids.total',
                        'xgrids.total',
                        'grids.total',
                        'init.num.pixels.compute',
                        'yinterval',
                        'ycuts',
                        'quick',
                        'cores',
                        'rolling',
                        'observation.ID',
                        'train.ID.start',
                        'train.ID.end',
                        'test.ID.start',
                        'test.ID.end',
                        'weights',
                        'members.size',
                        'num.neighbors',
                        'iteration',
                        'threshold.triangle',
                        'num.pixels.increase',
                        'debug',
                        'pixels.compute'
                    ]

    all_ok = True

    for keys in possible_keys:

        if keys not in d:

            print 'Expected key %s not in initial_config dictionary'%keys
            all_ok = False

    return all_ok


def process_initial_config(initial_config):

    initial_config['pixels.compute'] = ["%s"%str(int(k)) for k in list(initial_config['pixels.compute'])]

    possible_keys = [   'command.exe',
                        'command.verbose',
                        'file.forecasts',
                        'file.observations',
                        'folder.prefix',
                        'folder.accumulate',
                        'folder.output',
                        'folder.raster.anen',
                        'folder.raster.obs',
                        'folder.tmp',
                        'file.pixels.computed',
                        'num.flts',
                        'num.times',
                        'num.times.to.compute',
                        'num.parameters',
                        'ygrids.total',
                        'xgrids.total',
                        'grids.total',
                        'init.num.pixels.compute',
                        'yinterval',
                        'ycuts',
                        'quick',
                        'cores',
                        'rolling',
                        'observation.ID',
                        'train.ID.start',
                        'train.ID.end',
                        'test.ID.start',
                        'test.ID.end',
                        'weights',
                        'members.size',
                        'num.neighbors',
                        'iteration',
                        'threshold.triangle',
                        'num.pixels.increase',
                        'debug'
                    ]

    for keys in possible_keys:
        initial_config[keys] = initial_config[keys][0]


    for key, val in initial_config.iteritems():
        if type(val) not in [str, int, float, list, bool]:
            sys.exit(1)


    return initial_config


if __name__ == '__main__':



    try:

        # -------------------------- Stage 1 ---------------------------------------
        # Read initial configuration from R function
        with open('setup.R', 'r') as f:
            R_code = f.read()
        initial_config = STAP(R_code, 'initial_config')
        RAnEnExtra = importr("RAnEnExtra")
        config = initial_config.initial_config()
        initial_config = dict(zip(config.names, list(config)))

        if not test_initial_config(initial_config):
            sys.exit(1)

        initial_config = process_initial_config(initial_config)
    
        from pprint import pprint
        pprint(initial_config)

    except Exception as ex:
        print 'Error: %s'%ex
        print traceback.format_exc()

    '''

    #################################################
    # additional conversion from for the dictionary #
    #################################################

    # Our application currently will contain only one pipeline
    p = Pipeline()


    # First stage corresponds to rasterizing the observation data

    s1 = Stage()

    t1 =  Task()
    t1.pre_exec = [    'module load python/2.7.7/GCC-4.9.0',
                       'source $HOME/ve_rpy2/bin/activate',
                       'module load r',
                       'module load netcdf']

    t1.executable = ['python']

    t1.arguments = [
                        'generate_observation_raster.py',
                        '--folder',
                        '--num_times_to_compute',
                        '--num_flts', initial_config['num.flts'],
                        '--file_observations', initial_config['file.observations'],
                        '--test_ID_start', initial_config['test.ID.start'],
                        '--xgrids_total', initial_config['xgrids.total'],
                        '--ygrids_total', initial_config['ygrids.total']

                    ]
    t1.cores = 1
    t1.link_input_data = [  '$SHARED/generate_observation_raster.py',
                            '$SHARED/generate_observation_raster.R'
                    ]


    s1.add_tasks(t1)


    # Second stage corresponds to the AnEn computation
    s2 = Stage()

    # List to catch all the uids of the AnEn tasks
    anen_task_uids = list()

    stations_subset = list()

    for ind in range(10):

        # Create a new task
        t2 = Task()
        # task executable
        t2.executable    = ['canalogs']       
        # All modules to be loaded for the executable to be detected
        t2.pre_exec      = resource_key['xsede.supermic']
        # Number of cores for this task
        t2.cores         = int(initial_config['cores'])
        # List of arguments to the executable      
        t2.arguments     = [ '-N','-p',
                            '--forecast-nc', initial_config['file.forecast'],
                            '--observation-nc', initial_config['file.observation'],
                            '--test-ID-start', int(initial_config['test.ID.start']),
                            '--test-ID-end', int(initial_config['test.ID.end']),
                            '--train-ID-start', int(initial_config['train.ID.start']),
                            '--train-ID-end', int(initial_config['train.ID.end']),
                            '--observation-ID', int(initial_config['observation.ID']),
                            '--members-size', int(initial_config['members.size']),
                            '--weights', initial_config['members.size'],
                            '--rolling', int(initial_config['rolling']),
                            '--quick', int(initial_config['quick']),
                            '--number-of-cores', int(initial_config['cores']),
                            '-o', './' + os.path.basename(initial_config['output.AnEn']), '--stations-ID']

        t2.arguments.extend(initial_config['stations.ID'][ind*10:(ind+1)*10])

        t2.arguments.extend([
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
                            '--stride-observations','1 1 1 1'
                            
                            ])


        if ind==1:
            stations_subset = initial_config['stations.ID'][ind*10:(ind+1)*10]

        anen_task_uids.append(t2.uid)

        # Add this task to our stage
        s2.add_tasks(t2)
    
    # Add the stage to our pipeline
    p.add_stages(s2)
    # --------------------------------------------------------------------------


    # -------------------------- Stage 3 ---------------------------------------

    s3 = Stage()

    t3 = Task()
    t3.executable       = ['canalogs']
    t3.pre_exec         = resource_key['xsede.supermic']
    t3.arguments        = [ '-C',
                            '--file-new','iter1_%s.nc'%len(initial_config['output.AnEn']),
                            '--files-from']

    t3.link_input_data = []

    for ind in range(10):
        t3.link_input_data += ['$Pipeline_%s_Stage_%s_Task_%s/%s-starts-%s-ends-%s.nc'%(
                                                            p.uid,
                                                            s1.uid,
                                                            anen_task_uids[ind],
                                                            os.path.basename(initial_config['output.AnEn']).split('.')[0],
                                                            initial_config['stations.ID'][ind*10],
                                                            initial_config['stations.ID'][(ind+1)*10])]

        t3.arguments.append('%s-starts-%s-ends-%s.nc'%(
                                                        os.path.basename(initial_config['output.AnEn']).split('.')[0],
                                                        initial_config['stations.ID'][ind*10],
                                                        initial_config['stations.ID'][(ind+1)*10])
                                                    )
                                                

    t3.arguments.extend(analog_files)

    s3.add_tasks(t3)
    p.add_stages(s3)

    # --------------------------------------------------------------------------

    # -------------------------- Stage 4 ---------------------------------------
    

    # Third stage corresponds to evaluation of interpolated data
    s4 = Stage()

    t4 = Task()
    t4.executable    = ['python']
    t4.pre_exec      =  [   'module load python/2.7.7/GCC-4.9.0',
                            'source $HOME/ve_rpy2/bin/activate',
                            'module load r',
                            'module load netcdf']
    t4.cores         = 1
    t4.arguments     = [ 'evaluation.py', 
                        '--file_observation', initial_config['file.observation'],
                        '--file_AnEn', initial_config['output.AnEn'],
                        '--stations_ID', stations_subset,
                        '--test_ID_start', initial_config['test.ID.start'],
                        '--test_ID_end', initial_config['test.ID.end'],
                        '--nflts', initial_config['num.flts'],
                        '--nrows', initial_config['nrows'],
                        '--ncols', initial_config['ncols']
                    ]
    t4.upload_input_data = ['./evaluation.py', './evaluation.R']
    t4.link_input_data = ['$Pipeline_%s_$Stage_%s_$Task_%s/%s'%(
                                                                p.uid,
                                                                s2.uid,
                                                                t2.uid,
                                                                initial_config['output.AnEn']
                                                            )]
    

    s4.add_tasks(t4)
    p.add_stages(s4)
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

    except Exception, ex:

        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()

    finally:

        profs = glob('./*.prof')
        for f in profs:
            os.remove(f)

    '''
