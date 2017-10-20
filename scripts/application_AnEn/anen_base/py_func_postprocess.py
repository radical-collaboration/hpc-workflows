'''
File: py_func_postprocess.py
Author: Weiming Hu
Created: Sep 2017

Interpolate rasters for AnEn. This will make the visualization of
AnEn output easier 
'''
import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

def postprocess (configs, pre_exec):

    # set up
    str_folder_accumulate = configs['folder.accumulate']
    str_folder_raster_anen = configs['folder.raster.anen']
    str_file_pixels_computed = configs['file.pixels.computed']
    str_folder_local = configs['folder.local']
    verbose = configs['verbose']

    if verbose > 0:
        print "Start postprocessing"

    # get number of iterations
    with open('func_get_list_length.R', 'r') as f:
        R_code = f.read()
    get_list_length = STAP(R_code, 'get_list_length')
    num_iterations = get_list_length.get_list_length(
        str_file_pixels_computed)
    num_iterations = num_iterations[0]

    if num_iterations == -1:
        print "Error while getting list length of " + str_file_pixels_computed
        sys.exit(1)

    with open('func_read_pixels_computed.R', 'r') as f:
        R_code = f.read()
    read_pixels_computed = STAP(R_code, 'read_pixels_computed')

    p = Pipeline()


    # -------------------------- Stage 1 ---------------------------------------
    s = Stage()

    for ind in range(num_iterations):

        str_iteration = str(ind+1).zfill(4)

        # define the file name of the accumulated AnEn output file
        # which will be used to interpolate the raster
        #
        file_anen_accumulate_iteration = '%siteration%s.nc' % (
                str_folder_accumulate, str_iteration)

        # define the prefix of raster output files
        prefix_anen_raster = '%siteration%s' % (
                str_folder_raster_anen, str_iteration)

        # get pixels computed
        str_file_pixels_accumulated = '%s/pixels_accumulated_for_iteration%s.txt' % (
                configs['folder.local'], str_iteration)

        if not os.path.exists(str_file_pixels_accumulated):
            print "File %s can't be found. Create it." % str_file_pixels_accumulated

            pixels_accumulated = read_pixels_computed.read_pixels_computed(
                    str_file_pixels_computed, str_iteration)
            str_pixels_accumulated = ' '.join([str(int(k)) for k in pixels_accumulated])
            with open(str_file_pixels_accumulated, 'w') as f:
                f.write(str_pixels_accumulated)

        t = Task()
        t.cores = 1
        t.pre_exec = pre_exec
        t.executable = ['python']
	t.upload_input_data = [str_file_pixels_accumulated]
        t.copy_input_data = [
                '%s/script_interpolate_anen.py' % configs['folder.scripts'],
                '%s/func_interpolate_anen.R' % configs['folder.scripts']]
        t.arguments = [
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
                '--ygrids_total', configs['ygrids.total'],
                '--interpolation_method', configs['interpolation.method']]

        if configs['verbose'] > 1:
            print "Create a task for postprocessing %d / %d" % (
                    ind+1, num_iterations)

        if configs['download.AnEn.rasters'] and configs['interpolate.AnEn.rasters']:
            print "Download AnEn interpolated rasters for iteration %s" % str_iteration
            t.download_output_data = []
            for time in range(configs['num.times.to.compute']):
                for flt in range(configs['num.flts']):
                    t.download_output_data.append(
                            "%s_time%d_flt%d.rdata > %sraster_AnEn_iteration%s_time%d_flt%d.rdata" % (
                                prefix_anen_raster, time+1, flt+1,
                                str_folder_local, str_iteration, time+1, flt+1))

            if configs['verbose'] > 1:
                print "Files to download for this task:"
                print t.download_output_data

        s.add_tasks(t)

    p.add_stages(s)
    # -------------------------- End of Stage 1 --------------------------------

    return p
