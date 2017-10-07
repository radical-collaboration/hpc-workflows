import os, sys, traceback, rpy2
import rpy2.robjects as robjects

from glob import glob
from rpy2.robjects.packages import STAP, importr
from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

'''
function postprocess

Interpolate rasters for AnEn. This will make the visualization of
AnEn output easier 
'''

def postprocess (configs, pre_exec):

    # set up
    str_folder_accumulate = configs['folder.accumulate']
    str_folder_raster_anen = configs['folder.raster.anen']
    str_file_pixels_computed = configs['file.pixels.computed']

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
        pixels_accumulated = read_pixels_computed.read_pixels_computed(
                str_file_pixels_computed, str_iteration)
        str_pixels_accumulated = ' '.join([str(int(k)) for k in pixels_accumulated])
        
	with open('pixels_accumulated.txt','w') as f:
            f.write(str_pixels_accumulated)

        t = Task()
        t.cores = 1
        t.pre_exec = pre_exec
        t.executable = ['python']
	t.upload_input_data = ['pixels_accumulated.txt']
        t.copy_input_data = [
                '%s/script_interpolate_anen.py' % configs['folder.scripts'],
                '%s/func_interpolate_anen.R' % configs['folder.scripts']]
        t.arguments = [
                'script_interpolate_anen.py',
                '--file_anen_accumulate_iteration', file_anen_accumulate_iteration,
                '--prefix_anen_raster', prefix_anen_raster,
                '--pixels_computed', 'pixels_accumulated.txt',
                '--num_flts', configs['num.flts'],
                '--num_times_to_compute', configs['num.times.to.compute'],
                '--members_size', configs['members.size'],
                '--num_neighbors', configs['num.neighbors'],
                '--xgrids_total', configs['xgrids.total'],
                '--ygrids_total', configs['ygrids.total']]

        s.add_tasks(t)

    p.add_stages(s)
    # -------------------------- End of Stage 1 --------------------------------

    return p
