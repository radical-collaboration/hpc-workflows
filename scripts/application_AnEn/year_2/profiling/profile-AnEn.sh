#!/bin/bash

echo "Profile AnEn"

rm analogs.nc || true
rm log* || true

for r in {1..5}
do
    echo "Repetition #$r"
    rm log_rep-$r.txt || true

    for ((i=1; i <= 16 ; i=i*2))
    do
        echo "Profiling with $i threads ..." 
        OMP_NUM_THREADS=$i analogGenerator --config config.cfg >> log_rep-$r.txt
        rm analogs.nc || true
    done
done
