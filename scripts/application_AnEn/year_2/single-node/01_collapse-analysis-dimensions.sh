#!/usr/bin/env bash

originFolder="/media/wuh20/ExFat-Hu/Data/NCEI/analysis_reformat"
outputFolder="/media/wuh20/ExFat-Hu/Data/NCEI/analysis_yearly"

cd $originFolder
for file in $( ls *.nc )
do
    echo forecastsToObservations -i $originFolder/$file -o $outputFolder/$file --time-match-mode 0
done
