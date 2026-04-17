#!/bin/bash

# input
variables=("stgm" "flom") # multiple values, "ffibs_score" "ffibs_coverage_ratio" "veg_species" "sal" "lnd_type"
file_type=("parquet") # single value
time_unit=("daily") # single value
model_groups=("G621") # multiple values
scenarios=("S08") # multiple values
username=("adoneff")

# model_groups=("G500" "G514" "G520" "G516" "G521" "G515" "G517" "G602" "G608") # multiple values
# scenarios=("S07" "S08") # multiple values

# generate strings for modelgroups and scenarios
modelgroupstring=$(IFS=, ; echo "${model_groups[*]}")
scenariostring=$(IFS=, ; echo "${scenarios[*]}")

# batching process
if [ "$file_type" == "parquet" ]; then
    if [ "$time_unit" == "daily" ]; then
        for variable_queue in "${variables[@]}"; do
            for model_group_id in "${model_groups[@]}"; do
                for scenario_id in "${scenarios[@]}"; do
                    echo "$model_group_id"
                    echo "$scenario_id"
                    echo "$variable_queue"
                    echo "$time_unit"
                    sbatch -N 1 -p RM-shared -t 00:59:00 --ntasks-per-node=4 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable_queue-$model_group_id-$scenario_id-%j.out \
                        /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                        /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable_queue --time_unit $time_unit --model_groups $model_group_id --scenarios $scenario_id 
                done
            done
        done
    elif [ "$time_unit" == "annual" ]; then
        for variable_queue in "${variables[@]}"; do
            echo "${model_groups[@]}"
            echo "${scenarios[@]}"
            echo "$variable_queue"
            echo "$time_unit"
            sbatch -N 1 -p RM-shared -t 00:30:00 --ntasks-per-node=4 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable_queue-$time_unit-%j.out \
                        /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                        /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable_queue --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
        done
    elif [ "$time_unit" == "monthly" ]; then
        for variable_queue in "${variables[@]}"; do
            echo "${model_groups[@]}"
            echo "${scenarios[@]}"
            echo "$variable_queue"
            echo "$time_unit"
            sbatch -N 1 -p RM-shared -t 00:20:00 --ntasks-per-node=3 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable_queue-$time_unit-%j.out \
                        /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                        /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable_queue  --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
        done
    else
        echo "Please supply either daily, monthly, or annual as an input."
    fi 
elif [ "$file_type" == "cog" ]; then
    for variable_queue in "${variables[@]}"; do
        for model_group_id in "${model_groups[@]}"; do
            for scenario_id in "${scenarios[@]}"; do
                echo "$model_group_id"
                echo "$scenario_id"
                echo "$variable_queue"
                sbatch -N 1 -p RM-shared -t 00:50:00 --ntasks-per-node=10 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable_queue-$model_group_id-$scenario_id-%j.out \
                    /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                    /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable_queue --time_unit $time_unit --model_groups $model_group_id --scenarios $scenario_id 
            done
        done
    done
elif [ "$file_type" == "clara" ]; then
    for variable_queue in "${variables[@]}"; do
        echo "$variable_queue"
        sbatch -N 1 -p RM-shared -t 02:00:00 --ntasks-per-node=64 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable_queue-$time_unit-%j.out \
                        /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                        /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable_queue --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
    done
else
    echo "Please supply either parquet or cog as an input."
fi