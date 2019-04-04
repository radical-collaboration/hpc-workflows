#!/bin/bash

# Define the total number of jobs to create.
totalJobs=365
# totalJobs=601

# Define the job file
# jobFile="/glade/u/home/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/multi-node/experiment-configs/analog_generation.pbs"
jobFile="/glade/u/home/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/multi-node/experiment-configs/day_analog_reshape.pbs"
# jobFile="/glade/u/home/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/multi-node/experiment-configs/generateMetrics.pbs"
# jobFile="/glade/u/home/wuh20/github/hpc-workflows/scripts/application_AnEn/year_2/multi-node/experiment-configs/analog_selection.pbs"

# Define the counter start.
#submittedJobs=0

#signalFile='signalFile'
#if [ ! -f $signalFile ]; then
#    touch $signalFile
#fi

for i in $(seq 0 $(($totalJobs-1))); do
    echo qsub -v index=$i $jobFile
    qsub -v index=$i $jobFile
done

#while true; do
#    # Get the number of queued jobs by looking at the queue status looking for the symbols
#    number=`qstat | grep "Q regular" | wc -l`
#    
#    echo Queued jobs: $number, Submitted jobs: $submittedJobs
#
#    if (( number == 0  )); then
#        #if [ -f $signalFile ]; then
#
#            echo All jobs are currently running. Signal file is found. Submit a new one.
#            qsub $jobFile
#            submittedJobs=$((submittedJobs + 1))
#
#			#rm $signalFile
#
#            if (( submittedJobs == totalJobs  )); then
#                echo $submittedJobs jobs submitted. Done!
#                exit 0
#            fi
#
#        #else
#        #    echo No jobs are waiting but the signal file is not found. Wait for 5 seconds.
#        #    sleep 5
#        #fi
#
#    else
#		sleep 5
#    fi
#
#done


