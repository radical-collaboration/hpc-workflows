import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
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


def test_initial_config(d):

    possible_keys = [
            'command.exe', 'command.verbose', 'file.forecasts',
            'file.observations', 'file.pixels.computed', 'folder.prefix',
            'folder.accumulate', 'folder.output', 'folder.raster.anen',
            'folder.raster.obs', 'folder.local', 'folder.triangles',
            'num.flts', 'num.times', 'num.times.to.compute',
            'num.parameters', 'ygrids.total', 'xgrids.total',
            'grids.total', 'init.num.pixels.compute',
            'yinterval', 'ycuts', 'quick', 'cores', 'rolling',
            'observation.ID', 'train.ID.start', 'train.ID.end',
            'test.ID.start', 'test.ID.end', 'weights', 'members.size',
            'num.neighbors', 'init.iteration', 'threshold.triangle',
            'num.pixels.increase', 'debug', 'pixels.compute']

    all_ok = True

    for keys in possible_keys:

        if keys not in d:

            print 'Expected key %s not in initial_config dictionary'%keys
            all_ok = False

    return all_ok


def process_initial_config(initial_config):

    # arguments treated as lists
    initial_config['pixels.compute'] = \
            [int(k) for k in list(initial_config['pixels.compute'])]
    initial_config['weights'] = [int(k) for k in list(initial_config['weights'])]
    initial_config['ycuts'] = [int(k) for k in list(initial_config['ycuts'])]

    # arguments treated as numeric 
    possible_keys = [
            'command.exe', 'command.verbose', 'file.forecasts',
            'file.observations', 'file.pixels.computed', 'folder.prefix',
            'folder.accumulate', 'folder.output', 'folder.raster.anen',
            'folder.raster.obs', 'folder.local', 'folder.triangles',
            'num.flts', 'num.times', 'num.times.to.compute', 'num.parameters',
            'ygrids.total', 'xgrids.total', 'grids.total', 'init.num.pixels.compute',
            'yinterval', 'quick', 'cores', 'rolling', 'observation.ID',
            'train.ID.start', 'train.ID.end', 'test.ID.start', 'test.ID.end',
            'members.size', 'num.neighbors', 'init.iteration', 'threshold.triangle',
            'num.pixels.increase', 'debug']

    for keys in possible_keys:
        initial_config[keys] = initial_config[keys][0]

    for key, val in initial_config.iteritems():
        if type(val) not in [str, int, float, list, bool]:
            sys.exit(1)

    return initial_config


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

    # Our application currently will contain only one pipeline
    p = Pipeline()
    # -------------------------- End of Setup ----------------------------------

    # -------------------------- Stage 1 ---------------------------------------
    # rasterize the observation data for each test day and flt
    t1 = Task()
    t1.cores = 1
    t1.executable = ['python']
    t1.pre_exec = [
            'module load r', 'module load netcdf',
            'module load python/2.7.7/GCC-4.9.0']
    t1.copy_input_data = [
            '$SHARED/generate_observation_rasters.py',
            '$SHARED/func_generate_observation_rasters.R']
    t1.arguments = [
            'generate_observation_rasters.py',
            '--folder_prefix', initial_config['folder.prefix'],
            '--folder_accumulate', initial_config['folder.accumulate'],
            '--folder_output', initial_config['folder.output'],
            '--folder_raster_anen', initial_config['folder.raster.anen'],
            '--folder_raster_obs', initial_config['folder.raster.obs'],
            '--folder_triangles', initial_config['folder.triangles'],
            '--num_times_to_compute', initial_config['num.times.to.compute'],
            '--num_flts', initial_config['num.flts'],
            '--file_observations', initial_config['file.observations'],
            '--test_ID_start', initial_config['test.ID.start'],
            '--xgrids_total', initial_config['xgrids.total'],
            '--ygrids_total', initial_config['ygrids.total']]

    s1 = Stage()
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

    # save the pixels to be computed for the 1st iteration
    with open('func_save_pixels_computed.R', 'r') as f:
        R_code = f.read()
    save_pixels_computed = STAP(R_code, 'save_pixels_computed')
    save_pixels_computed.save_pixels_computed(  
            [str(int(k)) for sublist in pixels_list for k in sublist],
            initial_config['file.pixels.computed'])

    # Second stage corresponds to the AnEn computation
    s2 = Stage()

    # List to catch all the uids of the AnEn tasks
    anen_task_uids = list()
    stations_subset = list()

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
                'iteration' + iteration +
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

        anen_task_uids.append(t2.uid)

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

    file_output = '%siteration%s.nc' % (initial_config['folder.accumulate'], iteration)

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
            initial_config['file.pixels.computed'], iteration)

    # define pixels for the next iteration
    t4 = Task()
    t4.cores = 1
    t4.executable = ['python']
    t4.pre_exec = [
            'module load python/2.7.7/GCC-4.9.0',
            'module load netcdf', 'module load r']
    t4.copy_input_data= [
            '$SHARED/define_pixels.py',
            '$SHARED/func_define_pixels.R']
    t4.arguments = [
            'define_pixels.py', 
            '--iteration', iteration,
            '--folder_raster_obs', initial_config['folder.raster.obs'],
            '--folder_accumulate', initial_config['folder.accumulate'],
            '--folder_triangles', initial_config['folder.triangles'],
            '--xgrids_total', initial_config['xgrids.total'],
            '--ygrids_total', initial_config['ygrids.total'],
            '--test_ID_start', initial_config['test.ID.start'],
            '--num_flts', initial_config['num.flts'],
            '--num_pixels_increase', initial_config['num.pixels.increase'],
            '--num_times_to_compute', initial_config['num.times.to.compute'],
            '--members_size', initial_config['members.size'],
            '--threshold_triangle', initial_config['threshold.triangle'],
            '--pixels_computed', [str(int(k)) for k in pixels_accumulated]]

    s4 = Stage()
    s4.add_tasks(t4)
    p.add_stages(s4)
    sys.exit()
    # -------------------------- End of Stage 4 --------------------------------


    # Create a dictionary to describe our resource request
    res_dict = {
            'resource': 'xsede.supermic',
            'walltime': 10,
            'cores': 20,
            'project': 'TG-MCB090174',
            #'queue': 'development',
            'schema': 'gsissh'}

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        rman.shared_data = [
                './generate_observation_rasters.py',
                './func_generate_observation_rasters.R',
                './define_pixels.py',
                './func_define_pixels.R']

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
