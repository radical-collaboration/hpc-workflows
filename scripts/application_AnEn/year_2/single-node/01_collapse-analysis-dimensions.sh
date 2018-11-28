#!/usr/bin/env bash

originFolder="/media/wuh20/ExFat-Hu/Data/NCEI/analysis_reformat"
outputFolder="/media/wuh20/ExFat-Hu/Data/NCEI/analysis_collapsed"

cd $originFolder
for file in $( ls *.nc )
do
    if [ -f $outputFolder/$file ]
    then
        echo File exists $outputFolder/$file 
    else
        echo Generating $outputFolder/$file 
        forecastsToObservations -i $originFolder/$file -o $outputFolder/$file --time-match-mode 0
    fi
done
