#!/bin/bash

echo "Profile AnEn ..."

rm analogs.nc || true
rm log* || true

for ((r=100; r <= 1000; r=r+100))
do
    echo "Using $r years of serach data ..."
    rm log_rep-$r.txt || true

    days=$(( r * 365 ))

    for ((i=1; i <= 16 ; i=i*2))
    do
        echo "-- Profiling with $i threads ..." 
        OMP_NUM_THREADS=$i analogGenerator --config config-profiling.cfg --test-start 0 0 109499 0 --test-count 10 1 1 1 --search-start 0 0 0 0 --search-count 10 1 $days 1

        rm analogs.nc || true
    done
done
