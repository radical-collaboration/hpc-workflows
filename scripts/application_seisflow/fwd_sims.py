from radical.entk import Pipeline, Stage, Task, AppManager, ResourceManager
import traceback, sys

if __name__ == '__main__':

    if len(sys.argv)!=2:
        print 'Execution cmd: python fwd_sims.py <number of events>'
        sys.exit(1)

    num_events = sys.argv[1]

    event_names = [ 'C201303130312A', 'C200904210526A', 'C200809291519A', 'C201404240310A', 
                    'C201309251642A', 'C201004112208A', 'C201002180113A', 'C200802080938A', 
                    'C200806011431A', 'C201305110208A', 'C200807190239A', 'C201305270336A',
                    'C201403100518A', 'C200908100406A', 'C201405240925A', 'C200909122006A',
                    'C200904181917A', 'C200805291546A', 'C200912192319A', 'C200910270004A',
                    'C200810221255A', 'C200910291744A', 'C200909031326A', 'C200903061050A',
                    'C201308211238A', 'C201411150231A', 'C201101010956A', 'C201310191754A',
                    'C201211122042A', 'C200804140945A', 'C201108231751A', 'C201201010527A',
                    'C201407270128A', 'C200707211534A', 'C200803222124A', 'C200808281522A',
                    'C201408232232A', 'C200906231419A', 'C201008121154A', 'C201107290742A']

    random.shuffle(event_names)

    selected_events = event_names[:num_events]


    p = Pipeline()

    '''

    # First stage to perform one meshfem task
    meshfem_stage = Stage()

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
    t1.cpu_reqs = {'processes': 384, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
    t1.copy_input_data = ['/ccs/proj/bip149/ssflow-1-event/data.tar > meshfem_data.tar']
    t1.post_exec = ['tar cfz specfem_data.tar bin DATA DATABASES_MPI OUTPUT_FILES']

    meshfem_stage.add_tasks(t1)

    p.add_stages(meshfem_stage)

    '''

    # Second stage to perform multiple specfem tasks
    specfem_stage = Stage()

    for event in selected_events:

        t = Task()
        t.pre_exec = [

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

                        # Untar the specfem input data
                        'tar xf specfem_data_event_%s.tar'%event,

                        # Link to common DATABASES_MPI containing mesh files (~55GB)
                        'ln -s /lustre/atlas/scratch/vivekb/bip149/ssflow-N-seq-events/DATABASES_MPI DATABASES_MPI'

                    ]
        t.executable = ['./bin/xspecfem3D']
        t.cpu_reqs = {'processes': 0, 'process_type': 'MPI', 'threads_per_process': 0, 'thread_type': 'OpenMP'}
        t.gpu_reqs = {'processes': 384, 'process_type': 'MPI', 'threads_per_process': 1, 'thread_type': 'OpenMP'}
        t.copy_input_data = ['/lustre/atlas/scratch/vivekb/bip149/ssflow-N-seq-events/specfem_data_event_%s.tar'%event,
                             '/lustre/atlas/scratch/vivekb/bip149/ssflow-N-seq-events/specfem_validator.py'
                            ]
        t.post_exec = ['python specfem_validator.py OUTPUT_FILES/output_solver.txt']
        specfem_stage.add_tasks(t2)

    p.add_stages(specfem_stage)


    res_dict = {
                'resource': 'ornl.titan_aprun',
                'walltime': 8*num_events,
                'cpus': 385,
                'gpus':  385,
                'project': 'BIP149',
                'schema': 'local'
            }
    if num_events<=16:
        # Fits in debug queue
        res_dict['queue'] = 'debug'
    else:
        res_dict['queue'] = 'batch'
    

    try:

        # Create a Resource Manager using the above description
        rman = ResourceManager(res_dict)

        # Create an Application Manager for our application
        appman = AppManager(resubmit_failed=False)

        # Assign the resource manager to be used by the application manager
        appman.resource_manager = rman

        # Assign the workflow to be executed by the application manager
        appman.assign_workflow(set([p]))

        # Run the application manager -- blocking call
        appman.run()        

    except Exception, ex:

        print 'Execution failed, error: %s'%ex
        print traceback.format_exc()

    
