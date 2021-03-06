'''
File: py_func_start_iteration.py
Author: Weiming Hu
Created: Sep 2017

start one iteration to compute Analog Ensemble for the specified pixels on 
supercomputers and evaluate the results
'''
import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

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
    tournament_size = configs['tournament.size']
    num_champions = configs['num.champions']
    num_error_pixels = configs['num.error.pixels']
    num_triangles_from_tournament = configs['num.triangles.from.tournament']
    evaluation_method = configs['evaluation.method']
    interpolation_method = configs['interpolation.method']
    triangle_center = configs['triangle.center']
    verbose = configs['verbose']

    str_iteration = str(iteration).zfill(4)
    str_folder_output = configs['folder.output']
    str_folder_accumulate = configs['folder.accumulate']
    str_folder_raster_obs = configs['folder.raster.obs']
    str_folder_raster_anen = configs['folder.raster.anen']
    str_folder_triangles = configs['folder.triangles']
    str_file_forecasts = configs['file.forecasts']
    str_file_observations = configs['file.observations']
    str_folder_local = configs['folder.local']
    str_file_pixels_computed = configs['file.pixels.computed']
    str_command_exe = configs['command.exe']

    p = Pipeline()


    # -------------------------- Stage 1 ---------------------------------------
    # compute AnEn for each subregion 
    s1 = Stage()

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
        t1 = Task()
        t1.cores = int(cores)
        t1.pre_exec = pre_exec
        t1.executable = [str_command_exe]

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
        t1.arguments = ['-N','-p',
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
            t1.arguments.append('--quick')

        t1.arguments.append('--weights')
        t1.arguments.extend(weights)

        t1.arguments.append('--stations-ID')
        t1.arguments.extend(pixels_to_compute)

        t1.arguments.extend([
            '--start-forecasts','0','%s'%int(subregion_pixel_start), '0', '0',
            '--count-forecasts','%s'%int(num_parameters), 
            '%s'%int(subregion_pixel_count),
            '%s'%int(num_times), '%s'%int(num_flts),  
            '--start-observations','0', '%s'%int(subregion_pixel_start), '0', '0',
            '--count-observations','1', '%s'%int(subregion_pixel_count), 
            '%s'%int(num_times), '%s'%int(num_flts)])

        # Add this task to our stage
        s1.add_tasks(t1)
        if configs['verbose'] > 1:
            print "Create a task for subregion %d" % ind

        # record the subregion output file
        files_subregion.append(file_subregion)

    # Add the stage to our pipeline
    p.add_stages(s1)

    # -------------------------- End of Stage 1 --------------------------------

    # -------------------------- Stage 2 ---------------------------------------
    # combine the AnEn output files for different subregions from the current iteration
    # and the AnEn output files from the previous iterations
    #
    s2 = Stage()
    t2 = Task()
    t2.pre_exec = pre_exec
    t2.executable = [str_command_exe]

    file_output = '%siteration%s.nc' % (str_folder_accumulate, str_iteration)

    t2.arguments = ['-C', '--file-new', file_output,
                '--verbose', verbose]

    # combine files from previous iterations
    t2.arguments.append('--files-from')
    if len(files_output) != 0:
        t2.arguments.append(files_output[len(files_output)-1])


    # combine files from subregions of the current iteration
    t2.arguments.extend([k for k in files_subregion])

    # add the output file of this stage to the tracking list
    files_output.append(file_output)

    s2.add_tasks(t2)
    if configs['verbose'] > 1:
        print "Create a task for combining AnEn output files"

    p.add_stages(s2)
    # -------------------------- End of Stage 2 --------------------------------

    # -------------------------- Optional stage --------------------------------
    prefix_anen_raster = '%siteration%s' % (
        str_folder_raster_anen, str_iteration)
    if not configs['evaluation.method'] == 2:
        # evaluate the interpolated raster
        file_anen_accumulate_iteration = '%siteration%s.nc' % (
                str_folder_accumulate, str_iteration)
        str_file_pixels_accumulated = '%s/pixels_accumulated_for_iteration%s.txt' % (
                configs['folder.local'], str_iteration)

        if not os.path.exists(str_file_pixels_accumulated):
            with open('func_read_pixels_computed.R', 'r') as f:
                R_code = f.read()
            read_pixels_computed = STAP(R_code, 'read_pixels_computed')

            pixels_accumulated = read_pixels_computed.read_pixels_computed(
                    str_file_pixels_computed, str_iteration)
            str_pixels_accumulated = ' '.join([str(int(k)) for k in pixels_accumulated])
            with open(str_file_pixels_accumulated, 'w') as f:
                f.write(str_pixels_accumulated)

        t_opt = Task()
        t_opt.cores = 1
        t_opt.pre_exec = pre_exec
        t_opt.executable = ['python']
        t_opt.upload_input_data = [str_file_pixels_accumulated]
        t_opt.copy_input_data = [
                '%s/script_interpolate_anen.py' % configs['folder.scripts'],
                '%s/func_interpolate_anen.R' % configs['folder.scripts']]
        t_opt.arguments = [
                'script_interpolate_anen.py',
                '--file_anen_accumulate_iteration', file_anen_accumulate_iteration,
                '--prefix_anen_raster', prefix_anen_raster,
                '--file_pixels_accumulated',
                'pixels_accumulated_for_iteration%s.txt' % str_iteration,
                '--num_flts', configs['num.flts'],
                '--num_times_to_compute', configs['num.times.to.compute'],
                '--members_size', configs['members.size'],
                '--num_neighbors', configs['num.neighbors'],
                '--xgrids_total', configs['xgrids.total'],
                '--ygrids_total', configs['ygrids.total']]
    # -------------------------- End of optional stage -------------------------

    # -------------------------- Stage 3 ---------------------------------------
    # define triangles and evaluate the errors of the triangle vertices;
    # then define the pixels to compute for the next iteration
    #
    # read accumulated pixels computed
    str_file_pixels_accumulated = '%s/pixels_accumulated_for_iteration%s.txt' % (
            configs['folder.local'], str_iteration)
    if not os.path.exists(str_file_pixels_accumulated):
        with open('func_read_pixels_computed.R', 'r') as f:
            R_code = f.read()
        read_pixels_computed = STAP(R_code, 'read_pixels_computed')
        pixels_accumulated = read_pixels_computed.read_pixels_computed(
                str_file_pixels_computed, str_iteration)
        str_pixels_accumulated = ' '.join([str(int(k)) for k in pixels_accumulated])

        with open(str_file_pixels_accumulated, 'w') as f:
            f.write(str_pixels_accumulated)

    # define pixels for the next iteration
    t3 = Task()
    t3.cores = 1
    t3.pre_exec = pre_exec
    t3.executable = ['python']
    t3.upload_input_data = ['%s/pixels_accumulated_for_iteration%s.txt' % (
        configs['folder.local'], str_iteration)]
    t3.copy_input_data = [
            '%s/script_define_pixels.py' % configs['folder.scripts'],
            '%s/func_define_pixels.R' % configs['folder.scripts']]
    t3.arguments = [
            'script_define_pixels.py', 
            '--iteration', str_iteration,
            '--folder_raster_obs', str_folder_raster_obs,
            '--prefix_anen_raster', prefix_anen_raster,
            '--folder_accumulate', str_folder_accumulate,
            '--folder_triangles', str_folder_triangles,
            '--xgrids_total', xgrids_total,
            '--ygrids_total', ygrids_total,
            '--num_flts', num_flts,
            '--num_pixels_increase', num_pixels_increase,
            '--num_times_to_compute', num_times_to_compute,
            '--members_size', members_size,
            '--threshold_triangle', threashold_triangle,
            '--file_pixels_accumulated',
            'pixels_accumulated_for_iteration%s.txt' % str_iteration,
            '--tournament_size', tournament_size,
            '--num_champions', num_champions,
            '--num_error_pixels', num_error_pixels,
            '--num_triangles_from_tournament', num_triangles_from_tournament,
            '--evaluation_method', evaluation_method,
            '--interpolation_method', interpolation_method,
            '--triangle_center', triangle_center,
            '--verbose', verbose]
    t3.download_output_data = [
            'pixels_next_iteration.txt > %spixels_defined_after_iteration%s.txt' % (
                str_folder_local, str_iteration)]
    if configs['verbose'] > 0:
        t3.download_output_data.append('evaluation_log.txt > %sevaluation_log_after_iteration%s.txt' % (
                    str_folder_local, str_iteration))

    s3 = Stage()

    s3.add_tasks(t3)
    if configs['verbose'] > 1:
        print "Create a task for evaluation"

    p.add_stages(s3)
    # -------------------------- End of Stage 3 --------------------------------

    return p
