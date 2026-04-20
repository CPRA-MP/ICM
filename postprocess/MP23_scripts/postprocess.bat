#!/bin/bash
for s in 6 7 8 9
do
    for g in 500
    do
        echo 'post processing: S0$s G$g'
        echo 'plotting Hydro timeseries'
        python ICM-Hydro_plotting_noCRMS.py $s $g
       
        echo 'plotting Veg timeseries'
        python ICM-Veg_timeseries_plotting.py $s $g 2040
        
        for y in 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032 2033 2034 2035 2036 2037 2038 2039 2040 2041 2042 2043 2044 2045 2046 2047 2048 2049 2050
#       for y in           2051 2052 2053 2054 2055 2056 2057 2058 2059 2060 2061 2062 2063 2064 2065 2066 2067 2068 2069 2070
        do 
            echo 'mapping morph outputs: ' $y & $y &
            python ICM_tif_mapping.py $s $g $y 2019 &
        done
        wait
        do 
            echo 'mapping FFIBS outupts: ' $y &
            python ICM_FFIBS_mapping.py $s $g $y 2019 &
        done
        wait
        
        mkdir -p /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/geomorph/output
        echo 'copying Morph TIF rasters to public directory'
        cp -r S0$s/G$g/geomorph/output/tif /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/geomorph/output/tif
        echo 'copying Morph PNG figures to public directory'
        cp -r S0$s/G$g/geomorph/output/png /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/geomorph/output/png
        echo 'copying Morph QAQC csv files to public directory'
        cp -r S0$s/G$g/geomorph/output_qaqc /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/geomorph/output_qaqc

        echo 'copying Hydro timeseries plots to public directory'
        mkdir -p /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/hydro
        cp -r S0$s/G$g/hydro/timeseries /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/hydro/timeseries
        
        echo 'copying LAVegMod barplots to public directory'
        mkdir -p /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/veg
        cp -r S0$s/G$g/veg/coverage_timeseries /ocean/projects/bcs200002p/ewhite12/public/MP2023_production_runs/ICM/S0$s/G$g/veg/coverage_timeseries
    done
done

