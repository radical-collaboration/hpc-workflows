#!/bin/bash

echo "Profile AnEn"

declare -a arr=("element1" "element2" "element3")

for i in {1..10}
exit 0

rm log.txt || true
rm analogs.nc || true
OMP_NUM_THREADS=1 analogGenerator --config config.cfg >> log.txt
rm analogs.nc || true
OMP_NUM_THREADS=2 analogGenerator --config config.cfg >> log.txt
rm analogs.nc || true
OMP_NUM_THREADS=4 analogGenerator --config config.cfg >> log.txt
rm analogs.nc || true
OMP_NUM_THREADS=8 analogGenerator --config config.cfg >> log.txt
rm analogs.nc || true
OMP_NUM_THREADS=16 analogGenerator --config config.cfg >> log.txt
rm analogs.nc || true
