__author__    = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__   = "MIT"

from radical.entk import EoP, AppManager, Kernel, ResourceHandle, PoE
import argparse

pypaw_env = ['export PATH=/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin:$PATH',
             'source activate pypaw_env']

config = {

            'substage_1':[  {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.17_40.param.yml'
                            }, 
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.40_100.param.yml'
                            }, 
                            {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.90_250.param.yml'
                            }
                        ],

            'substage_2':[  {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.17_40.param.yml'
                            }, 
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.40_100.param.yml'
                            }, 
                            {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.90_250.param.yml'
                            }
                        ],

            'substage_3':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.17_40.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.40_100.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.90_250.param.yml'
                            }
                                
                        ],

            'substage_4':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.17_40.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.40_100.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.90_250.param.yml'
                            }

                        ],

            'substage_5':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.17_40.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.17_40.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.40_100.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.40_100.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.90_250.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.90_250.param.yml'
                            }

                        ],

            'substage_6':[
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWeights/C201002060444A.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWeights/window_weights.param.yml'
                            },
                        ],


            'substage_7':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.17_40.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.40_100.param.yml'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.90_250.param.yml'
                            }

                        ],


            'substage_8':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/SumAdjoint/C201002060444A.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/SumAdjoint/sum_adjoint.param.yml'
                            },
                        ]

            
        }


class Seisflow(PoE):

    def __init__(self, ensemble_size, pipeline_size):
        super(Seisflow,self).__init__(ensemble_size, pipeline_size)

    def stage_1(self, instance):

        #print instance, type(instance)

        if instance%2==0:

            # Substage 1: Processing raw observed data

            k1 = Kernel(name="pypaw_process_asdf")
            k1.pre_exec = pypaw_env
            k1.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-process_asdf"
            k1.arguments = [
                                '-f',config['substage_1'][(instance-1)/2]['path'],
                                '-p',config['substage_1'][(instance-1)/2]['param']
                            ]
            k1.cores = 16
            k1.mpi = True

            return k1

        else:

            # Substage 2: Process raw synthetic data

            k1 = Kernel(name="pypaw_process_asdf")
            k1.pre_exec = pypaw_env
            k1.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-process_asdf"
            k1.arguments = [
                                '-f',config['substage_2'][(instance-1)/2]['path'],
                                '-p',config['substage_2'][(instance-1)/2]['param']
                            ]
            k1.cores = 16
            k1.mpi = True

            return k1


    def stage_2(self, instance):

        # Substage 3: Select time windows

        k2 = Kernel(name="pypaw_window_selection")
        k2.pre_exec = pypaw_env
        k2.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-window_selection_asdf"
        k2.arguments = [
                            '-f',config['substage_3'][instance-1]['path'],
                            '-p',config['substage_3'][instance-1]['param']
                        ]
        k2.cores = 16
        k2.mpi = True

        return k2


    def stage_3(self, instance):

        # Substage 4: Make measurements

        k3 = Kernel(name="pypaw_measure_adjoint")
        k3.pre_exec = pypaw_env
        k3.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-measure_adjoint_asdf"
        k3.arguments = [
                            '-f',config['substage_4'][instance-1]['path'],
                            '-p',config['substage_4'][instance-1]['param']
                        ]
        k3.cores = 16
        k3.mpi = True

        return k3


    def stage_4(self, instance):

        # Substage 5: Filtering windows based on measurements

        k4 = Kernel(name="pypaw_filter_windows")
        k4.pre_exec = pypaw_env
        k4.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-filter_windows"
        k4.arguments = [
                            '-f',config['substage_5'][instance-1]['path'],
                            '-p',config['substage_5'][instance-1]['param']
                        ]
        k4.cores = 1
        k4.mpi = True

        return k4


    def stage_5(self, instance):

        # Substage 6: Calculate weights for each measurements (window?)

        k5 = Kernel(name="pypaw_window_weights")
        k5.pre_exec = pypaw_env
        k5.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-window_weights"
        k5.arguments = [
                            '-f',config['substage_6'][instance-1]['path'],
                            '-p',config['substage_6'][instance-1]['param']
                        ]
        k5.cores = 1
        k5.mpi = True

        return k5


    def stage_6(self, instance):

        # Substage 7: Calculate adjoint sources

        k5 = Kernel(name="pypaw_adjoint_asdf")
        k5.pre_exec = pypaw_env
        k5.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-adjoint_asdf"
        k5.arguments = [
                            '-f',config['substage_7'][instance-1]['path'],
                            '-p',config['substage_7'][instance-1]['param'],
                        ]
        
        k5.cores = 16
        k5.mpi = True

        return k5


    def stage_7(self, instance):

        # Substage 8: Combine weights and adjoint sources

        k6 = Kernel(name="pypaw_sum_adjoint_asdf")
        k6.pre_exec = pypaw_env
        k6.executable = "/work/02734/vivek91/modules/miniconda2/envs/pypaw_env/bin/pypaw-sum_adjoint_asdf"
        k6.arguments = [
                            '-f',config['substage_8'][instance-1]['path'],
                            '-p',config['substage_8'][instance-1]['param'],
                        ]
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
                    'xsede.stampede': { 'cores': '64', 
                                        'username': 'vivek91', 
                                        #'username': 'tg838801', 
                                        'project': 'TG-MCB090174',
                                        'queue': 'development', 
                                        'walltime': '120', 
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
        pipe = Seisflow(ensemble_size=[6,3,3,3,1,3,1], pipeline_size=7)

        # Add workload to the application manager
        app.add_workload(pipe)

        # Run the given workload
        res.run(app)

        

    except Exception, ex:
        print 'Application failed, error: ', ex


    finally:
        # Deallocate the resource
        res.deallocate()
    
