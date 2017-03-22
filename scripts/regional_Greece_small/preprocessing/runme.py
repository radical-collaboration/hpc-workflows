__author__    = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__   = "MIT"

from radical.entk import EoP, AppManager, Kernel, ResourceHandle, PoE
import argparse
from pypaw_process_asdf import pypaw_process_asdf_kernel
from pypaw_process import pypaw_process_kernel
from pypaw_window_selection import pypaw_window_selection_kernel
from pypaw_measure_adjoint import pypaw_measure_adjoint_kernel
from pypaw_filter_windows import pypaw_filter_windows_kernel
from pypaw_window_weights import pypaw_window_weight_kernel
from pypaw_adjoint_asdf import pypaw_adjoint_asdf_kernel
from pypaw_sum_adjoint_asdf import pypaw_sum_adjoint_asdf_kernel


ENSEMBLE_SIZE=4


class Seisflow(PoE):

    def __init__(self, ensemble_size, pipeline_size):
        super(Test,self).__init__(ensemble_size, pipeline_size)

    def stage_1(self, instance):

        if instance==1:

            # Substage 1: Processing raw observed data

            k1 = Kernel(name="pypaw_process_asdf")
            k1.arguments = ["--observed=","--path=","--param="]
            k1.link_input_data = ['','path.json','param.yml']
            k1.cores = 16
            k1.mpi = True

            return k1

        else:

            # Substage 2: Process raw synthetic data

            k1 = Kernel(name="pypaw_process")
            k1.arguments = ["--synthetic=","--path=","--param="]
            k1.link_input_data = ['','path.json','param.yml']
            k1.cores = 16
            k1.mpi = True

            return k1



    def stage_2(self, instance):

        # Substage 3: Select time windows

        k2 = Kernel(name="pypaw_window_selection")
        k2.arguments = ["--observed=","--synthetic=","--path=","--param="]
        k2.link_input_data = ['$STAGE_1_TASK_1/observed.asdf','$STAGE_1_TASK_2/synthetic.asdf',
                            'path.json','param.yml']
        k2.cores = 16
        k2.mpi = True

        return k2


    def stage_3(self, instance):

        # Substage 4: Make measurements

        k3 = Kernel(name="pypaw_measure_adjoint")
        k3.arguments = ["--observed=","--synthetic=","--window=","--path=","--param="]
        k3.link_input_data = ['$STAGE_1_TASK_1/observed.asdf','$STAGE_1_TASK_2/synthetic.asdf',
                            '$STAGE_2_TASK_1/window.json','path.json','param.yml']
        k3.cores = 16
        k3.mpi = True

        return k3


    def stage_4(self, instance):

        # Substage 5: Filtering windows based on measurements

        k4 = Kernel(name="pypaw_filter_windows")
        k4.arguments = ["--window=",'--measurements=','--stations=']
        k4.link_input_data = ['$STAGE_2_TASK_1/window.json','$STAGE_3_TASK_1/measurements.json',
                            'path.json','param.yml','stations.json']
        k4.cores = 1
        k4.mpi = True

        return k4


    def stage_5(self, instance):

        if instance==1:

            # Substage 6: Calculate weights for each measurements (window?)

            k5 = Kernel(name="pypaw_window_weights")
            k5.arguments = ["--filtered_window=","--stations=",'path.json','param.yml']
            k5.link_input_data = ['$STAGE_4_TASK_1/filtered_window.json','path.json',
                            'param.yml','stations.json']
            k5.cores = 1
            k5.mpi = True

            return k5

        else:

            # Substage 7: Calculate adjoint sources

            k5 = Kernel(name="pypaw_adjoint_asdf")
            k5.arguments = ["--observed=","--synthetic=","--filtered_window=","--path=","--param="]
            k5.link_input_data = ['$STAGE_1_TASK_1/observed.asdf','$STAGE_1_TASK_2/synthetic.asdf',
                            '$STAGE_4_TASK_1/filtered_window.json','path.json','param.yml']
            k5.cores = 16
            k5.mpi = True

            return k5


    def stage_6(self, instance):

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

    # Register kernels to be used
    app.register_kernels(meshfem_kernel)
    app.register_kernels(specfem_kernel)

    parser = argparse.ArgumentParser()
    parser.add_argument('--resource', help='target resource label')
    args = parser.parse_args()
    
    if args.resource != None:
        resource = args.resource
    else:
        resource = 'local.localhost'



    res_dict = {
                    'ornl.titan': { 'cores': '16', 
                                        # 'username': 'vivek91', 
                                        'username': 'tg838801', 
                                        'project': 'TG-MCB090174',
                                        'queue': 'development', 
                                        'walltime': '40', 
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
                database_url='mongodb://rp:rp@ds015335.mlab.com:15335/rp',
                access_schema = res_dict[resource]['schema']                
)

    res.shared_data = [ './input_data/ipdata.tar']

    try:

        # Submit request for resources + wait till job becomes Active
        res.allocate(wait=True)

        # Create pattern object with desired ensemble size, pipeline size
        pipe = Test(ensemble_size=[2,1,1,1,2,1], pipeline_size=6)

        # Add workload to the application manager
        app.add_workload(pipe)

        # Run the given workload
        res.run(app)

        

    except Exception, ex:
        print 'Application failed, error: ', ex


    finally:
        # Deallocate the resource
        res.deallocate()
    
