__author__    = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__   = "MIT"

from radical.entk import EoP, AppManager, Kernel, ResourceHandle, PoE
import argparse
#from pypaw_process_asdf import pypaw_process_asdf_kernel
#from pypaw_process import pypaw_process_kernel
#from pypaw_window_selection import pypaw_window_selection_kernel
#from pypaw_measure_adjoint import pypaw_measure_adjoint_kernel
#from pypaw_filter_windows import pypaw_filter_windows_kernel
#from pypaw_window_weights import pypaw_window_weight_kernel
#from pypaw_adjoint_asdf import pypaw_adjoint_asdf_kernel
#from pypaw_sum_adjoint_asdf import pypaw_sum_adjoint_asdf_kernel

pypaw_env = ['export PATH=/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin:$PATH',
             'source activate pypaw_env']

ENSEMBLE_SIZE=2

class Seisflow(PoE):

    def __init__(self, ensemble_size, pipeline_size):
        super(Seisflow,self).__init__(ensemble_size, pipeline_size)

    def stage_1(self, instance):

        #print instance, type(instance)

        if instance==1:

            # Substage 1: Processing raw observed data

            print '1:',instance

            k1 = Kernel(name="pypaw_process_asdf")
            k1.pre_exec = pypaw_env
            k1.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-process_asdf"
            k1.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_17_40.path.json',
                            '-p', '/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.17_40.param.yml']
            k1.cores = 16
            k1.mpi = True

            return k1

        elif instance==2:

            # Substage 2: Process raw synthetic data

            print instance

            k1 = Kernel(name="pypaw_process_asdf")
            k1.pre_exec = pypaw_env
            k1.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-process_asdf"
            k1.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_17_40.path.json',
                            '-p','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.17_40.param.yml']
            k1.cores = 16
            k1.mpi = True

            return k1


    def stage_2(self, instance):

        # Substage 3: Select time windows

        k2 = Kernel(name="pypaw_window_selection")
        k2.pre_exec = pypaw_env
        k2.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-window_selection_asdf"
        k2.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.17_40.path.json',
                        '-p', '/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.17_40.param.yml']
        k2.cores = 16
        k2.mpi = True

        return k2


    def stage_3(self, instance):

        # Substage 4: Make measurements

        k3 = Kernel(name="pypaw_measure_adjoint")
        k3.pre_exec = pypaw_env
        k3.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-measure_adjoint_asdf"
        k3.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.17_40.path.json',
                        '-p','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.17_40.param.yml']
        k3.cores = 16
        k3.mpi = True

        return k3


    def stage_4(self, instance):

        # Substage 5: Filtering windows based on measurements

        k4 = Kernel(name="pypaw_filter_windows")
        k4.pre_exec = pypaw_env
        k4.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-filter_windows"
        k4.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.17_40.sensors.path.json',
                        '-p','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.17_40.param.yml']
        k4.cores = 1
        k4.mpi = True

        return k4


    def stage_5(self, instance):

        # Substage 6: Calculate weights for each measurements (window?)

        k5 = Kernel(name="pypaw_window_weights")
        k5.pre_exec = pypaw_env
        k5.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-window_weights"
        k5.arguments = ['-f','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWeights/C201002060444A.path.json',
                        '-p','/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWeights/window_weights.param.yml']
        k5.cores = 1
        k5.mpi = True

        return k5


    def stage_6(self, instance):

        # Substage 7: Calculate adjoint sources

        k5 = Kernel(name="pypaw_adjoint_asdf")
        k5.arguments = ["--observed=","--synthetic=","--filtered_window=","--path=","--param="]
        
        k5.cores = 16
        k5.mpi = True

        return k5


    def stage_7(self, instance):

        # Substage 8: Combine weights and adjoint sources

        k6 = Kernel(name="pypaw_sum_adjoint_asdf")
        k6.arguments = ["--adjoint_asdf=","--window_weight="]
        k6.link_input_data = ['$STAGE_6_TASK_1/adoint.asdf','$STAGE_5_TASK_1/weighted_window.json',
                            'path.json','param.yml']
        k6.cores = 1
        k6.mpi = True

        return k6


  

if __name__ == '__main__':

    # Create an application manager
    app = AppManager(name='preprocessing')

    parser = argparse.ArgumentParser()
    parser.add_argument('--resource', help='target resource label')
    args = parser.parse_args()
    
    if args.resource != None:
        resource = args.resource
    else:
        resource = 'local.localhost'



    res_dict = {
                    'xsede.stampede': { 'cores': '48', 
                                        'username': 'vivek91', 
                                        #'username': 'tg838801', 
                                        'project': 'TG-MCB090174',
                                        'queue': 'development', 
                                        'walltime': '60', 
                                        'schema': 'gsissh'
                                    }
            }

    # Create a resource handle for target machine
    res = ResourceHandle(resource=resource,
                cores=res_dict[resource]['cores'],
                username=res_dict[resource]['username'],
                project =res_dict[resource]['project'] ,
                queue=res_dict[resource]['queue'],
                walltime=res_dict[resource]['walltime'],
                database_url='mongodb://138.201.86.166:27017/simpy',
                access_schema = res_dict[resource]['schema']                
)

    try:

        # Submit request for resources + wait till job becomes Active
        res.allocate(wait=True)

        # Create pattern object with desired ensemble size, pipeline size
        pipe = Seisflow(ensemble_size=[2,1,1,1,1], pipeline_size=5)

        # Add workload to the application manager
        app.add_workload(pipe)

        # Run the given workload
        res.run(app)

        

    except Exception, ex:
        print 'Application failed, error: ', ex


    finally:
        # Deallocate the resource
        res.deallocate()
    
