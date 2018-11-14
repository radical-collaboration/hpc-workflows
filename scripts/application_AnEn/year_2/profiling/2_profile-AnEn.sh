#!/bin/bash

echo "Profile AnEn ..."

rm analogs.nc || true
rm log* || true

for ((r=10000; r <= 20000; r=r+5000))
do
    echo "Using $r years of serach data ..."
    rm log_rep-$r.txt || true

    days=$(( r * 365 ))

    for ((i=1; i <= 16 ; i=i*2))
    do
        echo "-- Profiling with $i threads ..." 

        echo OMP_NUM_THREADS=$i analogGenerator --config config-profiling.cfg --test-start 0 0 109499 0 --test-count 10 1 1 1 --search-start 0 0 0 0 --search-count 10 1 $days 1
        OMP_NUM_THREADS=$i analogGenerator --config config-profiling.cfg --test-start 0 0 109499 0 --test-count 10 1 1 1 --search-start 0 0 0 0 --search-count 10 1 $days 1 >> log_rep-$r.txt 

        rm analogs.nc || true
    done
done
