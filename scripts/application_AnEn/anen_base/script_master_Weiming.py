import os, sys, traceback, rpy2, shutil
import rpy2.robjects as robjects

from glob import glob
from py_func_preprocess import preprocess
from py_func_postprocess import postprocess
from rpy2.robjects.packages import STAP, importr
from py_func_start_iteration import start_iteration
from py_func_initial_config import test_initial_config
from py_func_initial_config import process_initial_config
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

'''
EnTK 0.6 script - Analog Ensemble application

In this example, we intend to execute 32 canalogs tasks each using 4 cores and different
station IDs on Stampede with a total resource reservation of 32 cores. Once completed,
we determine the execution time of the tasks using the EnTK profiler.
'''


resource_key = {
        'xsede.supermic': [
            'module load r',
            'module load gcc',
            'module load netcdf',
            'module load python/2.7.7/GCC-4.9.0']
        }


res_dict = {
        'resource': 'xsede.supermic',
        'walltime': 3000,
        'cores': 40,
        'project': 'TG-MCB090174',
        #'queue': 'development',
        'schema': 'gsissh'}


if __name__ == '__main__':

    # -------------------------- Setup -----------------------------------------
    # ENTK and AnEn parameters setup

    # Read initial configuration from R function
    with open('func_setup.R', 'r') as f:
        R_code = f.read()
    RAnEnExtra = importr("RAnEnExtra")
    initial_config = STAP(R_code, 'initial_config')
    config = initial_config.initial_config(user = os.environ.get('USER_NAME','Weiming'))
    initial_config = dict(zip(config.names, list(config)))

    if not test_initial_config(initial_config):
        sys.exit(1)

    initial_config = process_initial_config(initial_config)

    iteration = initial_config['init.iteration']
    
    # a list to keep track of the combined output AnEn files to be accumulated
    files_output = list()

    # Create the Manager for our application
    rman = ResourceManager(res_dict)
    appman = AppManager(port = initial_config['docker_port'], autoterminate = False)


    # -------------------------- End of Setup ----------------------------------

    # -------------------------- Preprocess  -----------------------------------
    # generate observation raster files and create required folders
    pipeline_preprocess = preprocess(initial_config, resource_key['xsede.supermic'])
    
    try:
        appman.resource_manager = rman
        appman.assign_workflow(set([pipeline_preprocess]))

        if initial_config['debug']:
            print "preprocess debug mode ..."
        else:
            appman.run()

    except Exception, ex:
        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()
        appman.resource_terminate()
        sys.exit(1)

    finally:
        profs = glob('./*.prof')
        for f in profs:
            shutil.move(f, "./%s/%s"%(initial_config['folder.local'], os.path.basename(f)))
    # -------------------------- End of Preprocess  ----------------------------

    # -------------------------- Iteration  ------------------------------------
    iteration = int(initial_config['init.iteration'])
    str_iteration = str(iteration).zfill(4)
    pixels_to_compute = initial_config['pixels.compute']
    max_iterations = initial_config['max.iterations']
    iteration_count = 0


    while iteration_count < max_iterations:

        print "Iteration %s" % str_iteration

        pipeline_iteration = start_iteration(
                iteration, initial_config, resource_key['xsede.supermic'],
                pixels_to_compute, files_output)

        try:
            appman.resource_manager = rman
            appman.assign_workflow(set([pipeline_iteration]))

            if initial_config['debug']:
                print "Iteration debug mode ..."
            else:
                appman.run()

        except Exception, ex:
            print 'Execution failed, error: %s'%ex
            print traceback.format_exc()
            appman.resource_terminate()
            sys.exit(1)

        finally:
            profs = glob('./*.prof')
            for f in profs:
                shutil.move(f, "./%s/%s"%(initial_config['folder.local'], os.path.basename(f)))

        if initial_config['debug']:
            print("No pixel information in debug mode")

        else:
            with open('%spixels_defined_after_iteration%s.txt' % (
                initial_config['folder.local'], str_iteration), 'r') as f:
                line = f.readlines()

            pixels_to_compute = [int(float(k)) for k in line[0].split(' ')]
            
            if initial_config['verbose'] > 0:
                print ("the number of pixels to compute for the next iteration %d"
                        % len(pixels_to_compute))

        if len(pixels_to_compute) == 0:
            print "No more pixels to compute for the next iteration."
            print "Terminate the process!"
            break

        iteration_count += 1
        iteration = int(str_iteration) + 1
        str_iteration = str(iteration).zfill(4)

    # -------------------------- End of Iteration  -----------------------------

    # -------------------------- Post Processing -------------------------------
    if not initial_config['interpolate.AnEn.rasters']:
        # exit the process if AnEn ouput raster interpolation is not needed
        sys.exit(0)

    pipeline_postprocess = postprocess(initial_config, resource_key['xsede.supermic'])

    try:
        appman.resource_manager = rman
        appman.assign_workflow(set([pipeline_postprocess]))

        if initial_config['debug']:
            print "Postprocess debug mode ..."
        else:
            appman.run()

    except Exception, ex:
        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()
        appman.resource_terminate()
        sys.exit(1)

    finally:
        if not initial_config['debug']:
            appman.resource_terminate()
        profs = glob('./*.prof')
        for f in profs:
            shutil.move(f, "./%s/%s"%(initial_config['folder.local'], os.path.basename(f)))
    # -------------------------- End of Post Processing ------------------------
