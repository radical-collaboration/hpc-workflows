import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from py_func_preprocess import preprocess
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
        'walltime': 60,
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
    config = initial_config.initial_config()
    initial_config = dict(zip(config.names, list(config)))

    if not test_initial_config(initial_config):
        sys.exit(1)

    initial_config = process_initial_config(initial_config)

    iteration = initial_config['init.iteration']
    
    # list to keep track of the combined output AnEn files to be accumulated
    files_output = list()

    # -------------------------- End of Setup ----------------------------------

    # -------------------------- Preprocess  -----------------------------------
    # generate observation raster files and create required folders
    flag = preprocess(initial_config, res_dict, resource_key['xsede.supermic'])
    
    if not flag:
        sys.exit(1)
    # -------------------------- End of Preprocess  ----------------------------

    # -------------------------- Iteration  ------------------------------------
    iteration = int(initial_config['init.iteration'])
    pixels_compute = initial_config['pixels.compute']

    # a list to keep track of the AnEn combined output files
    files_output = list()

    flag = start_iteration(
            iteration, initial_config, resource_key['xsede.supermic'],
            res_dict, pixels_compute, files_output)

    if not flag:
        sys.exit(1)
    # -------------------------- End of Iteration  -----------------------------
