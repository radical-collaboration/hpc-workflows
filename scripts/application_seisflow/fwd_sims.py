from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager
import traceback

NUM_SPECFEM_TASKS = 1

if __name__ == '__main__':

    p = Pipeline()

    # First stage to perform one meshfem task
    s1 = Stage()

    t1 = Task()

    t1.pre_exec = [     # Modules to be loaded
                        'module swap PrgEnv-pgi/5.2.82 PrgEnv-gnu/5.2.82',
                        'module load cudatoolkit/7.5.18-1.0502.10743.2.1',
                        'module load cray-netcdf-hdf5parallel/4.3.3.1',
                        'module load cray-hdf5-parallel/1.8.14',
                        'module load szip/2.1',
                        'module load mxml/2.9',
                        'module load adios/1.9.0',
                        'module load cmake/2.8.10.2',
                        'module load boost/1.57.0',
                        'module load vim/7.4',

                        # Untar the input data
                        'tar xf meshfem_data.tar',

                        # Preprocessing
                        'mkdir DATABASES_MPI',
                        'mkdir OUTPUT_FILES',
                        'cp DATA/Par_file OUTPUT_FILES/',
                        'cp DATA/CMTSOLUTION OUTPUT_FILES/',
                        'cp DATA/STATIONS OUTPUT_FILES/',
                        
                ]
    t1.executable = ['./bin/xmeshfem3D']
    t1.cpu_reqs = {'processes': 4, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
<<<<<<< HEAD
    #t1.gpu_reqs = {'process': 24, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
=======
>>>>>>> a2a76828685e68c7397071c009cb6acd69462c29
    t1.copy_input_data = ['/ccs/proj/bip149/specfem-test.small/data.tar > meshfem_data.tar']
    t1.post_exec = ['tar cfz specfem_data.tar bin DATA DATABASES_MPI OUTPUT_FILES']

    s1.add_tasks(t1)

    p.add_stages(s1)


    # Second stage to perform multiple specfem tasks
    s2 = Stage()

    t2_uids = []

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

                        # Untar the input data
                        'tar xf specfem_data.tar'    

                    ]
<<<<<<< HEAD
        t2.executable = ['./bin/xspecfem3D']
        #t2.cpu_reqs = {'process': 0, 'process_type': 'MPI', 'threads_per_process': 0, 'thread_type': 'OpenMP'}
        t2.gpu_reqs = {'processes': 4, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
        t2.copy_input_data = [  '$Pipeline_%s_Stage_%s_Task_%s/specfem_data.tar'%(p.uid,s1.uid,t1.uid),
                                '$SHARED/specfem_validator.py'
                            ]
        t2.post_exec = ['python specfem_validator.py']
=======
    t2.executable = ['./bin/xspecfem3D']
    t2.cpu_reqs = {'processes': 0, 'process_type': 'MPI', 'threads_per_process': 0, 'thread_type': 'OpenMP'}
    t2.gpu_reqs = {'processes': 4, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
    t2.copy_input_data = ['$Pipeline_%s_Stage_%s_Task_%s/specfem_data.tar'%(p.uid,s1.uid,t1.uid)]

    s2.add_tasks(t2)
>>>>>>> a2a76828685e68c7397071c009cb6acd69462c29

    #t2_uids.append(t2.uid)


    #print t2.to_dict()
    p.add_stages(s2)


    # Create a dictionary to describe our resource request
    res_dict = {

            'resource': 'ornl.titan_aprun',
            'walltime': 30,
            'cpus': 80,
            'gpus':  5,
            'project': 'BIP149',
            #'queue': 'development',
            'schema': 'local'

    }
    

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        rman.shared_data = ['./specfem_validator.py']

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

    
