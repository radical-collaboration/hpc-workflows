from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

NUM_SIMS = 3

shared_env = [  'export PATH=/ccs/proj/bip149/miniconda2/bin:$PATH',
                'source activate pypaw_env',
                'module load PE-intel/14.0.4',
                'module load openmpi',
                'module load mxml git vim szip',
                'module load hdf5-parallel/1.8.11_shared'
            ]


args = {

            'stage_1':[  {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.17_40.param.yml',
                                'executable': 'pypaw-process_asdf'
                            }, 
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.40_100.param.yml',
                                'executable': 'pypaw-process_asdf'
                            }, 
                            {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessObserved/C201002060444A.proc_obsd_90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessObserved/proc_obsd.90_250.param.yml',
                                'executable': 'pypaw-process_asdf'
                            },
                            {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.17_40.param.yml',
                                'executable': 'pypaw-process_asdf'
                            }, 
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.40_100.param.yml',
                                'executable': 'pypaw-process_asdf'
                            }, 
                            {   
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/ProcessSynthetic/C201002060444A.proc_synt_90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/ProcessSynthetic/proc_synt.90_250.param.yml',
                                'executable': 'pypaw-process_asdf'
                            }
                        ],

            'stage_2':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.17_40.param.yml',
                                'executable': 'pypaw-window_selection_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.40_100.param.yml',
                                'executable': 'pypaw-window_selection_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWindows/C201002060444A.window.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWindows/window.90_250.param.yml',
                                'executable': 'pypaw-window_selection_asdf'
                            }
                                
                        ],

            'stage_3':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.17_40.param.yml',
                                'executable': 'pypaw-measure_adjoint_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.40_100.param.yml',
                                'executable': 'pypaw-measure_adjoint_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/MeasureAdjoint/C201002060444A.measure_adj.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/MeasureAdjoint/adjoint.90_250.param.yml',
                                'executable': 'pypaw-measure_adjoint_asdf'
                            }

                        ],

            'stage_4':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.17_40.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.17_40.param.yml',
                                'executable': 'pypaw-filter_windows'
                                
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.40_100.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.40_100.param.yml',
                                'executable': 'pypaw-filter_windows'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/FilterWindows/C201002060444A.90_250.sensors.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/FilterWindows/filter_window.90_250.param.yml',
                                'executable': 'pypaw-filter_windows'
                            }

                        ],

            'stage_5':[
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateWeights/C201002060444A.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateWeights/window_weights.param.yml',
                                'executable': 'pypaw-window_weights'
                                
                            },
                        ],


            'stage_6':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.17_40.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.17_40.param.yml',
                                'executable': 'pypaw-adjoint_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.40_100.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.40_100.param.yml',
                                'executable': 'pypaw-adjoint_asdf'
                            },
                            {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/CreateAdjointSource/C201002060444A.adjoint.90_250.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/CreateAdjointSource/adjoint.90_250.param.yml',
                                'executable': 'pypaw-adjoint_asdf'
                            }

                        ],


            'stage_7':[  {
                                'path':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/paths/SumAdjoint/C201002060444A.path.json',
                                'param':'/work/02734/vivek91/modules/simpy/examples/titan_global_inv/params/SumAdjoint/sum_adjoint.param.yml',
                                'executable': 'pypaw-sum_adjoint_asdf'
                            },
                        ]

            
        }

if __name__ == '__main__':

    p = Pipeline()

    # First stage to process synthetic and observed data
    s1 = Stage()

    for t_args in args['stage_1']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s1.add_tasks(t)

    p.add_stages(s1)


    # Second stage to select windows
    s2 = Stage()

    for t_args in args['stage_2']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s2.add_tasks(t)

    p.add_stages(s2)

    # Third stage to measure adjoint
    s3 = Stage()

    for t_args in args['stage_3']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s3.add_tasks(t)

    p.add_stages(s3)

    # Fourth stage to filter windows
    s4 = Stage()

    for t_args in args['stage_4']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s4.add_tasks(t)

    p.add_stages(s4)

    # Fifth stage to generate window weights
    s5 = Stage()

    for t_args in args['stage_5']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s5.add_tasks(t)

    p.add_stages(s5)

    # Sixth stage to generate adjoint
    s6 = Stage()

    for t_args in args['stage_6']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s6.add_tasks(t)

    p.add_stages(s6)

    # Seventh stage to sum adjoint
    s7 = Stage()

    for t_args in args['stage_7']:

        t = Task()

        t.pre_exec = shared_env
        t.executable = t_args['executable']
        t.arguments = ['-f', t_args['path'],
                        '-p',t_args['param']]
        t.cpu_reqs = {'process': 16, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}

        s7.add_tasks(t)

    p.add_stages(s7)


    # Create a dictionary to describe our resource request
    res_dict = {

            'resource': 'ornl.titan_aprun',
            'walltime': 10,
            'cores': 400,
            'project': 'BIP149',
            #'queue': 'development',
            'schema': 'local'

    }
    

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        # Create an Application Manager for our application
        appman = AppManager()

        # Assign the resource manager to be used by the application manager
        appman.resource_manager = rman

        # Assign the workflow to be executed by the application manager
        appman.assign_workflow(set([p]))

        # Run the application manager -- blocking call
        appman.run()        

    except Exception, ex:

        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()

    