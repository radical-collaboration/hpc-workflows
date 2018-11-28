#!/usr/bin/env bash

forecastFolder="/home/graduate/wuh20/ExFat-Hu/Data/NCEI/forecasts_reformat"

for file in $( ls $forecastFolder | grep nc )
do
    echo processing $forecastFolder/$file
    windFieldCalculator --file-in $forecastFolder/$file --file-type Forecasts --file-out $forecastFolder/with-wind_$file -U TropoWindU -V TropoWindV --dir-name TropoWindDir --speed-name TropoWindSpeed -v 3
done

echo Done!
