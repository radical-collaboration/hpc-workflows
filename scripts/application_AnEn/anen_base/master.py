import os, sys
import rpy2
import rpy2.robjects as robjects
import traceback

from rpy2.robjects.packages import importr

from glob import glob
from rpy2.robjects.packages import STAP
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

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
                                        'module load r']
                                

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

    initial_config['pixels.compute'] = [int(k) for k in list(initial_config['pixels.compute'])]
    initial_config['weights'] = [int(k) for k in list(initial_config['weights'])]
    initial_config['ycuts'] = [int(k) for k in list(initial_config['ycuts'])]

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
                        'num.flts',
                        'num.times',
                        'num.times.to.compute',
                        'num.parameters',
                        'ygrids.total',
                        'xgrids.total',
                        'grids.total',
                        'init.num.pixels.compute',
                        'yinterval',
                        'quick',
                        'cores',
                        'rolling',
                        'observation.ID',
                        'train.ID.start',
                        'train.ID.end',
                        'test.ID.start',
                        'test.ID.end',
                        'members.size',
                        'num.neighbors',
                        'iteration',
                        'threshold.triangle',
                        'num.pixels.increase',
                        'debug',
                    ]

    for keys in possible_keys:
        initial_config[keys] = initial_config[keys][0]


    for key, val in initial_config.iteritems():
        if type(val) not in [str, int, float, list, bool]:
            sys.exit(1)


    return initial_config


if __name__ == '__main__':



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

    #from pprint import pprint
    #pprint(initial_config)


    #except Exception as ex:
    #    print 'Error: %s'%ex
    #    print traceback.format_exc()


    #################################################
    # additional conversion from for the dictionary #
    #################################################

    # Our application currently will contain only one pipeline
    p = Pipeline()


    # First stage corresponds to rasterizing the observation data

    s1 = Stage()

    t1 =  Task()
    t1.pre_exec = [    'module load python/2.7.7/GCC-4.9.0',
                       #'source $HOME/ve_rpy2/bin/activate',
                       'module load r',
                       'module load netcdf']

    t1.executable = ['python']

    t1.arguments = [
                        'generate_observation_rasters.py',
                        '--folder_prefix', initial_config['folder.prefix'],
                        '--folder_accumulate', initial_config['folder.accumulate'],
                        '--folder_output', initial_config['folder.output'],
                        '--folder_raster_anen', initial_config['folder.raster.anen'],
                        '--folder_raster_obs', initial_config['folder.raster.obs'],
                        '--num_times_to_compute', initial_config['num.times.to.compute'],
                        '--num_flts', initial_config['num.flts'],
                        '--file_observations', initial_config['file.observations'],
                        '--test_ID_start', initial_config['test.ID.start'],
                        '--xgrids_total', initial_config['xgrids.total'],
                        '--ygrids_total', initial_config['ygrids.total']

                    ]

    t1.copy_input_data = ['$SHARED/generate_observation_rasters.py','$SHARED/generate_observation_rasters.R']
    # not needed in the first iteration
    #t1.download_output_data = ['%s/pixels_computed_list.rdata'%initial_config['folder.prefix']] 

    t1.cores = 1

    s1.add_tasks(t1)

    p.add_stages(s1)


    # Call R function locally on pixels_computed_list.rdata

    with open('cut_pixels_along_y.R', 'r') as f:
        R_code = f.read()
    cut_pixels_along_y = STAP(R_code, 'cut_pixels_along_y')
    pixels_list = cut_pixels_along_y.cut_pixels_along_y(
                                        initial_config['pixels.compute'],
                                        # TODO: how does the program know where to separate the string into numbers
                                        [str(k) for k in initial_config['ycuts']],
                                        initial_config['xgrids.total'],
                                        initial_config['ygrids.total']
                                    )

    # Second stage corresponds to the AnEn computation
    s2 = Stage()

    # List to catch all the uids of the AnEn tasks
    anen_task_uids = list()

    stations_subset = list()

    # define weights string
    #weights_string = ''
    #for w in initial_config['weights']:
    #    weights_string += w + ' '

    for ind in range(len(pixels_list)):

        # Create a new task
        t2 = Task()
        # task executable
        t2.executable    = [initial_config['command.exe']]       
        # All modules to be loaded for the executable to be detected
        t2.pre_exec      = resource_key['xsede.supermic']
        # Number of cores for this task
        t2.cores         = int(initial_config['cores'])
        # List of arguments to the executable      

        # define the chunk to read
        subregion_pixel_start = (initial_config['ycuts'][ind] - initial_config['ycuts'][0]) * initial_config['xgrids.total']
        subregion_pixel_count = initial_config['yinterval'] * initial_config['xgrids.total']
        if ind == len(pixels_list)-1:
            subregion_pixel_count = initial_config['grids.total'] - subregion_pixel_start
        

        # define output anen
        file_output_anen = initial_config['folder.tmp'] + 'iteration' + initial_config['iteration'] + '_chunk' + str(ind) + '.nc'

        t2.arguments     = [ '-N','-p',
                '--forecast-nc', initial_config['file.forecasts'],
                '--observation-nc', initial_config['file.observations'],
                '--test-ID-start', int(initial_config['test.ID.start']),
                '--test-ID-end', int(initial_config['test.ID.end']),
                '--train-ID-start', int(initial_config['train.ID.start']),
                '--train-ID-end', int(initial_config['train.ID.end']),
                '--observation-ID', int(initial_config['observation.ID']),
                '--members-size', int(initial_config['members.size']),
                '--rolling', int(initial_config['rolling']),
                '--quick', int(initial_config['quick']),
                '--number-of-cores', int(initial_config['cores']),
                '-o', file_output_anen
                ]

        t2.arguments.append('--weights')
        t2.arugments.extend(initial_config['weights'])

        t2.arguments.append('--stations-ID')
        t2.arugments.extend(initial_config['pixels.compute'])


        t2.arguments.extend([
            '--start-forecasts','0','%s'%subregion_pixel_start, '0', '0',
            '--count-forecasts','%s'%initial_config['num.parameters'], 
                                '%s'%subregion_pixel_count,
                                '%s'%initial_config['num.times'],
                                '%s'%initial_config['num.flts'],  
            '--start-observations','0', '%s'%subregion_pixel_start, '0', '0',
            '--count-observations','1', '%s'%subregion_pixel_count, 
                                    '%s'%initial_config['num.times'], 
                                    '%s'%initial_config['num.flts']])

        #print t2.arguments


        anen_task_uids.append(t2.uid)

        # Add this task to our stage
        s2.add_tasks(t2)
    
    # Add the stage to our pipeline
    p.add_stages(s2)
    # --------------------------------------------------------------------------

    
    '''
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

    '''
    # Create a dictionary to describe our resource request
    res_dict = {

            'resource': 'xsede.supermic',
            'walltime': 10,
            'cores': 20,
            'project': 'TG-MCB090174',
            #'queue': 'development',
            'schema': 'gsissh'

    }
    

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        rman.shared_data = ['./generate_observation_rasters.py', './generate_observation_rasters.R']

        # Create an Application Manager for our application
        appman = AppManager(port = 32769)

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

