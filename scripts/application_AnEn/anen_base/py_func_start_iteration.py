import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

'''
function start_iteration

start one iteration to compute Analog Ensemble for the specified pixels on 
supercomputers and evaluate the results
'''

def start_iteration (
        iteration, configs, pre_exec,
        pixels_to_compute, files_output):

    # setup
    ycuts = configs['ycuts']
    yinterval = configs['yinterval']
    xgrids_total = configs['xgrids.total']
    ygrids_total = configs['ygrids.total']
    grids_total = configs['grids.total']
    num_parameters = configs['num.parameters']
    num_times = configs['num.times']
    num_flts = configs['num.flts']
    num_times_to_compute = configs['num.times.to.compute']
    num_pixels_increase = configs['num.pixels.increase']
    threashold_triangle = configs['threshold.triangle']
    test_ID_start = configs['test.ID.start']
    test_ID_end = configs['test.ID.end']
    train_ID_start = configs['train.ID.start']
    train_ID_end = configs['train.ID.end']
    observation_ID = configs['observation.ID']
    members_size = configs['members.size']
    rolling = configs['rolling']
    quick = configs['quick']
    cores = configs['cores']
    weights = configs['weights']
    verbose = configs['verbose']

    str_iteration = str(iteration).zfill(4)
    str_folder_output = configs['folder.output']
    str_folder_accumulate = configs['folder.accumulate']
    str_folder_raster_obs = configs['folder.raster.obs']
    str_folder_triangles = configs['folder.triangles']
    str_file_forecasts = configs['file.forecasts']
    str_file_observations = configs['file.observations']
    str_folder_local = configs['folder.local']
    str_file_pixels_computed = configs['file.pixels.computed']
    str_command_exe = configs['command.exe']

    p = Pipeline()


    # -------------------------- Stage 1 ---------------------------------------
    # compute AnEn for each subregion 
    s2 = Stage()

    # get the pixels to cmpute for each subregion
    with open('func_cut_pixels_along_y.R', 'r') as f:
        R_code = f.read()
    cut_pixels_along_y = STAP(R_code, 'cut_pixels_along_y')
    pixels_list = cut_pixels_along_y.cut_pixels_along_y(
            [str(k) for k in pixels_to_compute],
            [str(k) for k in ycuts],
            xgrids_total, ygrids_total)

    # save the pixels to be computed for the 1st iteration
    with open('func_save_pixels_computed.R', 'r') as f:
        R_code = f.read()
    save_pixels_computed = STAP(R_code, 'save_pixels_computed')
    save_pixels_computed.save_pixels_computed(  
            [str(int(k)) for sublist in pixels_list for k in sublist],
            str_file_pixels_computed)

    # create tasks for each subregion and 
    # each subregion will generate one subregion file
    #
    files_subregion = list()

    for ind in range(len(pixels_list)):
        
        # create task
        t2 = Task()
        t2.cores = int(cores)
        t2.pre_exec = pre_exec
        t2.executable = [str_command_exe]

        # define the chunk to read
        subregion_pixel_start = ((ycuts[ind] - ycuts[0]) * xgrids_total)
        subregion_pixel_count = yinterval * xgrids_total
        if ind == len(pixels_list)-1:
            subregion_pixel_count = grids_total - subregion_pixel_start

        # define output anen
        file_subregion = (
                str_folder_output + 'iteration' + str_iteration +
                '_chunk' + str(ind).zfill(4) + '.nc')

        # check whether there are pixels lying within this subregion
        pixels_to_compute = pixels_list[ind]
        pixels_to_compute = [int(val - subregion_pixel_start) for val in pixels_to_compute]
        
        if len(pixels_to_compute) == 0:
            continue
        
        # define arguments for calling the CAnEn program
        t2.arguments = ['-N','-p',
                '--forecast-nc', str_file_forecasts,
                '--observation-nc', str_file_observations,
                '--test-ID-start', test_ID_start,
                '--test-ID-end', test_ID_end,
                '--train-ID-start', train_ID_start,
                '--train-ID-end', train_ID_end,
                '--observation-ID', observation_ID,
                '--members-size', members_size,
                '--rolling', rolling,
                '--cores', cores,
                '-o', file_subregion,
                '--verbose', verbose]

        if quick:
            t2.arguments.append('--quick')

        t2.arguments.append('--weights')
        t2.arguments.extend(weights)

        t2.arguments.append('--stations-ID')
        t2.arguments.extend(pixels_to_compute)

        t2.arguments.extend([
            '--start-forecasts','0','%s'%int(subregion_pixel_start), '0', '0',
            '--count-forecasts','%s'%int(num_parameters), 
            '%s'%int(subregion_pixel_count),
            '%s'%int(num_times), '%s'%int(num_flts),  
            '--start-observations','0', '%s'%int(subregion_pixel_start), '0', '0',
            '--count-observations','1', '%s'%int(subregion_pixel_count), 
            '%s'%int(num_times), '%s'%int(num_flts)])

        # Add this task to our stage
        s2.add_tasks(t2)

        # record the subregion output file
        files_subregion.append(file_subregion)

    # Add the stage to our pipeline
    p.add_stages(s2)

    # -------------------------- End of Stage 1 --------------------------------

    # -------------------------- Stage 2 ---------------------------------------
    # combine the AnEn output files for different subregions from the current iteration
    # and the AnEn output files from the previous iterations
    #
    s3 = Stage()
    t3 = Task()
    t3.pre_exec = pre_exec
    t3.executable = [str_command_exe]

    file_output = '%siteration%s.nc' % (str_folder_accumulate, str_iteration)

    t3.arguments = ['-C', '--file-new', file_output,
                '--verbose', verbose]

    # combine files from previous iterations
    t3.arguments.append('--files-from')
    t3.arguments.extend([k for k in files_output])

    # combine files from subregions of the current iteration
    t3.arguments.extend([k for k in files_subregion])

    # add the output file of this stage to the tracking list
    files_output.append(file_output)

    s3.add_tasks(t3)
    p.add_stages(s3)
    # -------------------------- End of Stage 2 --------------------------------

    # -------------------------- Stage 3 ---------------------------------------
    # define triangles and evaluate the errors of the triangle vertices;
    # then define the pixels to compute for the next iteration
    #
    # read accumulated pixels computed
    with open('func_read_pixels_computed.R', 'r') as f:
        R_code = f.read()
    read_pixels_computed = STAP(R_code, 'read_pixels_computed')
    pixels_accumulated = read_pixels_computed.read_pixels_computed(
            str_file_pixels_computed, str_iteration)
    str_pixels_accumulated = ' '.join([str(int(k)) for k in pixels_accumulated])

    with open('%s/pixels_accumulated.txt' % configs['folder.local'], 'w') as f:        
        f.write(str_pixels_accumulated)
    
    # define pixels for the next iteration
    t4 = Task()
    t4.cores = 1
    t4.pre_exec = pre_exec
    t4.executable = ['python']
    t4.upload_input_data = ['%s/pixels_accumulated.txt' % configs['folder.local']]
    t4.copy_input_data = [
            '%s/script_define_pixels.py' % configs['folder.scripts'],
            '%s/func_define_pixels.R' % configs['folder.scripts']]
    t4.arguments = [
            'script_define_pixels.py', 
            '--iteration', str_iteration,
            '--folder_raster_obs', str_folder_raster_obs,
            '--folder_accumulate', str_folder_accumulate,
            '--folder_triangles', str_folder_triangles,
            '--xgrids_total', xgrids_total,
            '--ygrids_total', ygrids_total,
            '--num_flts', num_flts,
            '--num_pixels_increase', num_pixels_increase,
            '--num_times_to_compute', num_times_to_compute,
            '--members_size', members_size,
            '--threshold_triangle', threashold_triangle,
            '--file_pixels_accumulated', 'pixels_accumulated.txt',
            '--verbose', verbose]
    t4.download_output_data = [
            'pixels_next_iteration.txt > %spixels_defined_after_iteration%s.txt' % (
                str_folder_local, str_iteration)]

    s4 = Stage()
    s4.add_tasks(t4)
    p.add_stages(s4)
    # -------------------------- End of Stage 3 --------------------------------

    return p
