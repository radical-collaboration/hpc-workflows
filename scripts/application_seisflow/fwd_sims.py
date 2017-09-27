from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager

NUM_SPECFEM_TASKS = 4

if __name__ == '__main__':

    p = Pipeline()

    # First stage to perform one meshfem task
    s1 = Stage()

    t1 = Task()

    t1.pre_exec = [     # Modules to be loaded
                        'module swap PrgEnv-pgi/5.2.82 PrgEnv-gnu/5.2.82',
                        'module load cudatoolkit/7.5.18-1.0502.10743.2.1 ',
                        'module load cray-netcdf-hdf5parallel/4.3.3.1 ',
                        'module load cray-hdf5-parallel/1.8.14 ',
                        'module load szip/2.1 ',
                        'module load mxml/2.9',
                        'module load adios/1.9.0',
                        'module load cmake/2.8.10.2',
                        'module load boost/1.57.0 ',
                        'module load vim/7.4',

                        # Preprocessing
                        'mkdir DATABASES_MPI',
                        'mkdir OUTPUT_FILES'
                        'cp DATA/Par_file OUTPUT_FILES/',
                        'cp DATA/CMTSOLUTION OUTPUT_FILES/'
                        'cp DATA/STATIONS OUTPUT_FILES/',
                        
                ]
    t1.executable = ['./bin/xmeshfem3D']
    t2.cpu_reqs = {'process': 24, 'process_type': 'MPI', 'threads_per_process': 0, 'thread_type': 'OpenMP'}
    #t2.gpu_reqs = {'process': 24, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
    #t1.cores = 4
    #t1.mpi = True
    t1.copy_input_data = ['/lustre/atlas/scratch/vivekb/bip149/specfem3d_globe_gpu/DATA']

    s1.add_tasks(t1)

    p.add_stages(s1)


    # Second stage to perform multiple specfem tasks
    s2 = Stage()

    t2_uids = []

    for ind in range(len(NUM_SPECFEM_TASKS)):

        t2 = Task()
        t2.pre_exec = [

                        # Modules to be loaded
                        'module swap PrgEnv-pgi/5.2.82 PrgEnv-gnu/5.2.82',
                        'module load cudatoolkit/7.5.18-1.0502.10743.2.1 ',
                        'module load cray-netcdf-hdf5parallel/4.3.3.1 ',
                        'module load cray-hdf5-parallel/1.8.14 ',
                        'module load szip/2.1 ',
                        'module load mxml/2.9',
                        'module load adios/1.9.0',
                        'module load cmake/2.8.10.2',
                        'module load boost/1.57.0 ',
                        'module load vim/7.4',

                    ]
        t2.executable = ['./bin/specfem3D']
        #t2.cpu_reqs = {'process': 0, 'process_type': 'MPI', 'threads_per_process': 0, 'thread_type': 'OpenMP'}
        t2.gpu_reqs = {'process': 24, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
        #t2.cores = 8
        #t2.mpi = True
        t2.post_exec = []
        t2.copy_input_data = [  '$Pipeline_%s_Stage_%s_Task_%s/DATA'%(p.uid, s1.uid, t1.uid),
                                '$Pipeline_%s_Stage_%s_Task_%s/OUTPUT_FILES'%(p.uid, s1.uid, t1.uid),
                                '$Pipeline_%s_Stage_%s_Task_%s/DATABASES_MPI'%(p.uid, s1.uid, t1.uid)]

        s2.add_tasks(t2)

        t2_uids.append(t2.uid)

    p.add_stages(s2)


    # Create a dictionary to describe our resource request
    res_dict = {

            'resource': 'ornl.titan_aprun',
            'walltime': 10,
            'cores': 400,
            'gpus':  25,
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

    