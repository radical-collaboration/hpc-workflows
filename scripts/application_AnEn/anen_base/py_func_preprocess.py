import os, sys, traceback

from glob import glob
from radical.entk import Pipeline, Stage, Task
from radical.entk import AppManager, ResourceManager

'''
function preprocess contains one pipeline with only one stage
to generate the observation rasters and prepare the working
environment for the subsequent pipelines
'''


def preprocess (configs, res_dict, pre_exec):
    p = Pipeline()

    # -------------------------- Stage 1 ---------------------------------------
    t = Task()
    t.cores = 1
    t.pre_exec = pre_exec
    t.executable = ['python']
    t.copy_input_data = [
            '$SHARED/script_generate_observation_rasters.py',
            '$SHARED/func_generate_observation_rasters.R']
    t.arguments = [
            'script_generate_observation_rasters.py',
            '--folder_prefix', configs['folder.prefix'],
            '--folder_accumulate', configs['folder.accumulate'],
            '--folder_output', configs['folder.output'],
            '--folder_raster_anen', configs['folder.raster.anen'],
            '--folder_raster_obs', configs['folder.raster.obs'],
            '--folder_triangles', configs['folder.triangles'],
            '--num_times_to_compute', configs['num.times.to.compute'],
            '--num_flts', configs['num.flts'],
            '--file_observations', configs['file.observations'],
            '--test_ID_start', configs['test.ID.start'],
            '--xgrids_total', configs['xgrids.total'],
            '--ygrids_total', configs['ygrids.total']]

    s = Stage()
    s.add_tasks(t)
    p.add_stages(s)
    # -------------------------- End of Stage 1 --------------------------------

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        rman.shared_data = [
                './script_generate_observation_rasters.py',
                './func_generate_observation_rasters.R']

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

        return False

    finally:

        profs = glob('./*.prof')
        for f in profs:
            os.remove(f)

    return True
