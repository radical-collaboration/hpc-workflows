#!/bin/bash

# Define the total number of jobs to create.
totalJobs=65

# Define the job file
jobFile="analog_generation.pbs"

# Define the counter start.
submittedJobs=0

while true; do
    # Get the number of queued jobs by looking at the queue status looking for the symbols
    number=`qstat | grep "Q regular" | wc -l`
    
    echo The number of queued jobs: $number
    echo The number of submitted jobs: $submittedJobs
    if (( number == 0  )); then
        echo There is no queued jobs. Submit a new one.
        qsub $jobFile
        submittedJobs=$((submittedJobs + 1))
        if (( submittedJobs == totalJobs  )); then
            echo $submittedJobs jobs submitted. Done!
            exit 0
        fi
    fi
    sleep 10
done
