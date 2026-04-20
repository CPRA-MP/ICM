#!/bin/bash

# Path to your table
table_file="/ocean/projects/bcs200002p/shared/upload-tracker/variable_list.csv"
has_header=true   # Change to false if your CSV has no header

model_group_list=$(seq 600 650) # 655 is last run type = restoration; 656 to 690 are FWIP2
for group in $model_group_list
do
    model_groups+=("G$group")   
done
# model_groups=("G621") # or set as needed
scenarios=("S07" "S08") # or set as needed
username=("adoneff") 

# Function to trim whitespace (safe for variables from CSV)
trim() { local var="$*"; var="${var#"${var%%[![:space:]]*}"}"; echo -n "${var%"${var##*[![:space:]]}"}"; }

# Read the CSV file line by line (skip header if present)
first_line=true
while IFS=, read -r variable time_unit file_type; do
    if $has_header && $first_line; then first_line=false; continue; fi

    # Trim just in case
    variable=$(trim "$variable")
    time_unit=$(trim "$time_unit")
    file_type=$(trim "$file_type")

    modelgroupstring=$(IFS=, ; echo "${model_groups[*]}")
    scenariostring=$(IFS=, ; echo "${scenarios[*]}")
    echo "Processing variable: $variable, file_type: $file_type, time_unit: $time_unit"
  
    # Now branch as before
    if [ "$file_type" == "parquet" ]; then
        if [ "$time_unit" == "daily" ]; then
            for model_group_id in "${model_groups[@]}"; do
                for scenario_id in "${scenarios[@]}"; do
                    echo "$model_group_id"
                    echo "$scenario_id"
                    echo "$variable"
                    echo "$time_unit"
                    sbatch -N 1 -p RM-shared -t 00:59:00 --ntasks-per-node=4 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable-$model_group_id-$scenario_id-%j.out \
                        /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                        /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable --time_unit $time_unit --model_groups $model_group_id --scenarios $scenario_id
                done
            done
        elif [ "$time_unit" == "annual" ]; then
            echo "${model_groups[@]}"
            echo "${scenarios[@]}"
            echo "$variable"
            echo "$time_unit"
            sbatch -N 1 -p RM-shared -t 00:30:00 --ntasks-per-node=4 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable-$time_unit-%j.out \
                /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
        elif [ "$time_unit" == "monthly" ]; then
            echo "${model_groups[@]}"
            echo "${scenarios[@]}"
            echo "$variable"
            echo "$time_unit"
            sbatch -N 1 -p RM-shared -t 00:20:00 --ntasks-per-node=3 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable-$time_unit-%j.out \
                /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
        else
            echo "Please supply either daily, monthly, or annual as an input."
        fi
    elif [ "$file_type" == "cog" ]; then
        for model_group_id in "${model_groups[@]}"; do
            for scenario_id in "${scenarios[@]}"; do
                echo "$model_group_id"
                echo "$scenario_id"
                echo "$variable"
                sbatch -N 1 -p RM-shared -t 00:50:00 --ntasks-per-node=10 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable-$model_group_id-$scenario_id-%j.out \
                    /ocean/projects/bcs200002p/shared/python/cpra-python3 \
                    /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable --time_unit $time_unit --model_groups $model_group_id --scenarios $scenario_id
            done
        done
    elif [ "$file_type" == "clara" ]; then
        echo "$variable"
        sbatch -N 1 -p RM-shared -t 02:00:00 --ntasks-per-node=64 -o /ocean/projects/bcs200002p/shared/upload-tracker/log/slurm-$variable-$time_unit-%j.out \
            /ocean/projects/bcs200002p/shared/python/cpra-python3 \
            /ocean/projects/bcs200002p/$username/mp29_pct/data_conversion/mpd_conversion/write_parquet_cog.py --variable_queue $variable --time_unit $time_unit --model_groups $modelgroupstring --scenarios $scenariostring
    else
        echo "Please supply either parquet, cog, or clara as file_type."
    fi
done < "$table_file"