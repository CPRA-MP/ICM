#!/bin/bash

for S in S06 S07 S08 S09
do
    for G in G501 G502 G503 G504 G505
    do
        echo $S $G
        cp surge_filtered_new3.csv ./$S/$G/hydro/surge_filtered_new3.csv
        rm ./$S/$G/hydro/surge.csv
	cp ./$S/$G/hydro/surge_filtered_new3.csv  ./$S/$G/hydro/surge.csv
    done
done
