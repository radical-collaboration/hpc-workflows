import os, sys, traceback

from glob import glob
from radical.entk import Pipeline, Stage, Task
from radical.entk import AppManager, ResourceManager

'''
function preprocess contains one pipeline with only one stage
to generate the observation rasters and prepare the working
environment for the subsequent pipelines
'''


def preprocess (configs, pre_exec):
    p = Pipeline()

    # -------------------------- Stage 1 ---------------------------------------
    s = Stage()

    for time in range(configs['num.times.to.compute']):
        for flt in range(configs['num.flts']):
            t = Task()
            t.cores = 1
            t.pre_exec = pre_exec
            t.executable = ['python']
            t.copy_input_data = [
                    '%s/script_generate_observation_rasters.py' % configs['folder.scripts'],
                    '%s/func_generate_observation_rasters.R' % configs['folder.scripts']]
            t.arguments = [
                    'script_generate_observation_rasters.py',
                    '--test_ID_index', time+1,
                    '--test_ID_start', configs['test.ID.start'],
                    '--flt', flt+1,
                    '--folder_prefix', configs['folder.prefix'],
                    '--folder_accumulate', configs['folder.accumulate'],
                    '--folder_output', configs['folder.output'],
                    '--folder_raster_anen', configs['folder.raster.anen'],
                    '--folder_raster_obs', configs['folder.raster.obs'],
                    '--folder_triangles', configs['folder.triangles'],
                    '--num_times_to_compute', configs['num.times.to.compute'],
                    '--num_flts', configs['num.flts'],
                    '--file_observations', configs['file.observations'],
                    '--xgrids_total', configs['xgrids.total'],
                    '--ygrids_total', configs['ygrids.total']]

            s.add_tasks(t)
            if configs['verbose'] > 1:
                print "Create a task for generating observation raster at time %d flt %d" % (
                        time+1, flt+1)

    p.add_stages(s)
    # -------------------------- End of Stage 1 --------------------------------

    return p
