import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
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
        'xsede.stampede': [
            'module load netcdf',
            'export PATH=/home1/04672/tg839717/git/CAnalogsV2/build:$PATH'],

        'xsede.supermic': [
            'module load netcdf',
            'module load gcc',
            'module load r']
        }


def generate_pipeline(iteration, pixels_compute=None):

    # Our application currently will contain only one pipeline
    p = Pipeline()
    # -------------------------- End of Setup ----------------------------------


    if not pixels_compute:

        # -------------------------- Stage 1 ---------------------------------------
        s1 = Stage()

        for ind in range(initial_config['num.times.to.compute']):
            # rasterize the observation data for each test day and flt
            t1 = Task()
            t1.cores = 1
            t1.executable = ['python']
            t1.pre_exec = [
                    'module load r', 'module load netcdf',
                    'module load python/2.7.7/GCC-4.9.0']
            t1.copy_input_data = [
                    '/home/vivek91/work/chunk_NAM/script_generate_observation_rasters.py',
                    '/home/vivek91/work/chunk_NAM/func_generate_observation_rasters.R']
            t1.arguments = [
                    'script_generate_observation_rasters.py',
                    '--test_ID_index', ind+1,
                    '--test_ID_start', initial_config['test.ID.start'],
                    '--folder_prefix', initial_config['folder.prefix'],
                    '--folder_accumulate', initial_config['folder.accumulate'],
                    '--folder_output', initial_config['folder.output'],
                    '--folder_raster_anen', initial_config['folder.raster.anen'],
                    '--folder_raster_obs', initial_config['folder.raster.obs'],
                    '--folder_triangles', initial_config['folder.triangles'],
                    '--num_times_to_compute', initial_config['num.times.to.compute'],
                    '--num_flts', initial_config['num.flts'],
                    '--file_observations', initial_config['file.observations'],
                    '--xgrids_total', initial_config['xgrids.total'],
                    '--ygrids_total', initial_config['ygrids.total']]

            s1.add_tasks(t1)

        p.add_stages(s1)
        # -------------------------- End of Stage 1 --------------------------------

        # -------------------------- Stage 2 ---------------------------------------
        # compute AnEn for each subregion 

        # get the pixels to compute for each subregion
        with open('func_cut_pixels_along_y.R', 'r') as f:
            R_code = f.read()
        cut_pixels_along_y = STAP(R_code, 'cut_pixels_along_y')
        pixels_list = cut_pixels_along_y.cut_pixels_along_y(
                initial_config['pixels.compute'],
                [str(k) for k in initial_config['ycuts']],
                initial_config['xgrids.total'],
                initial_config['ygrids.total'])
    else:

        # get the pixels to compute for each subregion
        with open('func_cut_pixels_along_y.R', 'r') as f:
            R_code = f.read()
        cut_pixels_along_y = STAP(R_code, 'cut_pixels_along_y')
        pixels_list = cut_pixels_along_y.cut_pixels_along_y(
                pixels_compute,
                [str(k) for k in initial_config['ycuts']],
                initial_config['xgrids.total'],
                initial_config['ygrids.total'])

    # save the pixels to be computed for the 1st iteration
    with open('func_save_pixels_computed.R', 'r') as f:
        R_code = f.read()
    save_pixels_computed = STAP(R_code, 'save_pixels_computed')
    save_pixels_computed.save_pixels_computed(  
            [str(int(k)) for sublist in pixels_list for k in sublist],
            initial_config['file.pixels.computed'])

    # Second stage corresponds to the AnEn computation
    s2 = Stage()

    # list to keep track of the AnEn subregion output files
    files_subregion = list()

    for ind in range(len(pixels_list)):

        # Create a new task
        t2 = Task()
        # task executable
        t2.executable = [initial_config['command.exe']]
        # All modules to be loaded for the executable to be detected
        t2.pre_exec = resource_key['xsede.supermic']
        # Number of cores for this task
        t2.cores = int(initial_config['cores'])
        # List of arguments to the executable      

        # define the chunk to read
        subregion_pixel_start = (
                (initial_config['ycuts'][ind] - initial_config['ycuts'][0])
                * initial_config['xgrids.total'])
        subregion_pixel_count = (
                initial_config['yinterval'] * initial_config['xgrids.total'])
        if ind == len(pixels_list)-1:
            subregion_pixel_count = initial_config['grids.total'] - subregion_pixel_start

        # define output anen
        file_subregion = (
                initial_config['folder.output'] +
                'iteration' + str(iteration).zfill(4) +
                '_chunk' + str(ind).zfill(4) + '.nc')

        t2.arguments = ['-N','-p',
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
                '--cores', int(initial_config['cores']),
                '-o', file_subregion]

        files_subregion.append(file_subregion)

        t2.arguments.append('--weights')
        t2.arguments.extend(initial_config['weights'])

        pixels_compute = pixels_list[ind]
        pixels_compute = [int(val - subregion_pixel_start) for val in pixels_compute]
        t2.arguments.append('--stations-ID')
        t2.arguments.extend(pixels_compute)

        t2.arguments.extend([
            '--start-forecasts','0','%s'%int(subregion_pixel_start), '0', '0',
            '--count-forecasts','%s'%int(initial_config['num.parameters']), 
            '%s'%int(subregion_pixel_count),
            '%s'%int(initial_config['num.times']),
            '%s'%int(initial_config['num.flts']),  
            '--start-observations','0', '%s'%int(subregion_pixel_start), '0', '0',
            '--count-observations','1', '%s'%int(subregion_pixel_count), 
            '%s'%int(initial_config['num.times']), 
            '%s'%int(initial_config['num.flts'])])

        # Add this task to our stage
        s2.add_tasks(t2)

    # Add the stage to our pipeline
    p.add_stages(s2)
    # -------------------------- End of Stage 2 --------------------------------

    # -------------------------- Stage 3 ---------------------------------------
    # combine the AnEn output files for different subregions from the current iteration
    # and the AnEn output files from the previous iterations
    #
    s3 = Stage()
    t3 = Task()
    t3.executable = [initial_config['command.exe']]
    t3.pre_exec = resource_key['xsede.supermic']

    file_output = '%siteration%s.nc' % (initial_config['folder.accumulate'], str(iteration).zfill(4))

    t3.arguments = ['-C', '--file-new', file_output]
    t3.arguments.append('--files-from')

    # combine files from previous iterations
    t3.arguments.extend([k for k in files_output])

    # combine files from subregions of the current iteration
    t3.arguments.extend([k for k in files_subregion])

    # add the output file of this stage to the tracking list
    files_output.append(file_output)

    s3.add_tasks(t3)
    p.add_stages(s3)
    # -------------------------- End of Stage 3 --------------------------------

    # -------------------------- Stage 4 ---------------------------------------
    # define triangles and evaluate the errors of the triangle vertices;
    # then define the pixels to compute for the next iteration
    #
    # read accumulated pixels computed
    with open('func_read_pixels_computed.R', 'r') as f:
        R_code = f.read()
    read_pixels_computed = STAP(R_code, 'read_pixels_computed')
    pixels_accumulated = read_pixels_computed.read_pixels_computed(
            initial_config['file.pixels.computed'], str(iteration).zfill(4))
    pixels_accumulated_str = ' '.join([str(int(k)) for k in pixels_accumulated])

    # define pixels for the next iteration
    t4 = Task()
    t4.cores = 1
    t4.executable = ['python']
    t4.pre_exec = [
            'module load python/2.7.7/GCC-4.9.0',
            'module load netcdf', 'module load r']
    t4.copy_input_data= [
            '/home/vivek91/work/chunk_NAM/script_define_pixels.py',
            '/home/vivek91/work/chunk_NAM/func_define_pixels.R']
    t4.arguments = [
            'script_define_pixels.py', 
            '--iteration', iteration,
            '--folder_raster_obs', initial_config['folder.raster.obs'],
            '--folder_accumulate', initial_config['folder.accumulate'],
            '--folder_triangles', initial_config['folder.triangles'],
            '--xgrids_total', int(initial_config['xgrids.total']),
            '--ygrids_total', int(initial_config['ygrids.total']),
            '--num_flts', int(initial_config['num.flts']),
            '--num_pixels_increase', int(initial_config['num.pixels.increase']),
            '--num_times_to_compute', int(initial_config['num.times.to.compute']),
            '--members_size', int(initial_config['members.size']),
            '--threshold_triangle', initial_config['threshold.triangle'],
            '--pixels_computed', pixels_accumulated_str]
    t4.download_output_data = [
            'pixels_next_iteration.txt > %spixels_defined_after_iteration%s.txt' % (
                initial_config['folder.local'], iteration)]

    s4 = Stage()
    s4.add_tasks(t4)
    p.add_stages(s4)
    # -------------------------- End of Stage 4 --------------------------------

    return p


def read_pixels(pixel_file):
    with open(pixel_file, 'r') as fh:
        lines = fh.readlines()
    pixels_compute = [int(val) for val in lines[0].strip().split(' ')]
    return pixels_compute


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

    # Create a dictionary to describe our resource request
    res_dict = {
            'resource': 'xsede.supermic',
            'walltime': 60,
            'cores': 40,
            'project': 'TG-MCB090174',
            #'queue': 'development',
            'schema': 'gsissh'}

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        # rman.shared_data = [
        #         './script_generate_observation_rasters.py',
        #         './func_generate_observation_rasters.R',
        #         './script_define_pixels.py',
        #         './func_define_pixels.R']

        # Create an Application Manager for our application
        appman = AppManager(port = 32769)

        # Assign the resource manager to be used by the application manager
        appman.resource_manager = rman

        iter_cnt = 1
        pixels_compute = None
        while len(pixels_compute) != 0:

            p = generate_pipeline(iter_cnt, pixels_compute)

            # Assign the workflow to be executed by the application manager
            appman.assign_workflow(set([p]))

            # Run the application manager -- blocking call
            appman.run()

            # Process pixels_defined_after_iteration%s.txt to get new list of 
            # pixels. Generate new pipeline with this new list.

            pixels_compute = read_pixels('%spixels_defined_after_iteration%s.txt'%(
                                                            initial_config['folder.local'],
                                                            iter_cnt))

    except Exception, ex:

        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()

    finally:

        profs = glob('./*.prof')
        for f in profs:
            os.remove(f)
