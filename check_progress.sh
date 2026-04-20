#!/bin/bash

parent_dir="/ocean/projects/bcs200002p/shared/data"
output_file="/ocean/projects/bcs200002p/shared/upload-tracker/log/data_summary.csv"

# Write CSV header
# Columns: Variable, Grid, Time Unit, Model Group, Scenario, Number of Files, Sum of File Sizes (MB)
echo "Variable,Grid,Time Unit,Model Group,Scenario,Number of Files,Sum of File Sizes (MB)" > "$output_file"

# Print CSV header to command line
echo "Variable,Grid,Time Unit,Model Group,Scenario,Number of Files,Sum of File Sizes (MB)"

for variable_dir in "$parent_dir"/variable=*/; do
    variable=$(basename "$variable_dir" | cut -d'=' -f2)

    for grid_dir in "$variable_dir"/grid=*/; do
        grid=$(basename "$grid_dir" | cut -d'=' -f2)

        for time_dir in "$grid_dir"/time_unit=*/; do
            time_unit=$(basename "$time_dir" | cut -d'=' -f2)

            # Initialize associative arrays for counts and sizes
            declare -A bucket_counts
            declare -A bucket_sizes

            accumulate() {
                local file_path="$1"
                local key="$2"

                if [[ -f "$file_path" ]]; then
                    local fsize
                    fsize=$(stat --format="%s" "$file_path" 2>/dev/null)
                    if [[ -n "$fsize" ]]; then
                        bucket_counts["$key"]=$(( ${bucket_counts["$key"]:-0} + 1 ))
                        bucket_sizes["$key"]=$(( ${bucket_sizes["$key"]:-0} + fsize ))
                    fi
                fi
            }

            # Walk files under time_dir
            while IFS= read -r -d '' fpath; do
                mgid=""
                sid=""

                # Split path into components and search from innermost component outward
                IFS='/' read -ra parts <<< "$fpath"
                for (( idx=${#parts[@]}-1 ; idx>=0 ; idx-- )); do
                    part="${parts[idx]}"
                    if [[ "$part" == model_group_id=* ]]; then
                        mgid="${part#model_group_id=}"
                        break
                    fi
                done
                for (( idx=${#parts[@]}-1 ; idx>=0 ; idx-- )); do
                    part="${parts[idx]}"
                    if [[ "$part" == scenario_id=* ]]; then
                        sid="${part#scenario_id=}"
                        break
                    fi
                done

                # If still empty, do a parent climb (robust fallback)
                if [[ -z "$mgid" ]]; then
                    parent="${fpath%/*}"
                    while [[ "$parent" != "/" && -n "$parent" ]]; do
                        seg="${parent##*/}"
                        if [[ "$seg" == model_group_id=* ]]; then
                            mgid="${seg#model_group_id=}"
                            break
                        fi
                        parent="${parent%/*}"
                    done
                fi
                if [[ -z "$sid" ]]; then
                    parent="${fpath%/*}"
                    while [[ "$parent" != "/" && -n "$parent" ]]; do
                        seg="${parent##*/}"
                        if [[ "$seg" == scenario_id=* ]]; then
                            sid="${seg#scenario_id=}"
                            break
                        fi
                        parent="${parent%/*}"
                    done
                fi

                # Build internal key
                if [[ -n "$mgid" || -n "$sid" ]]; then
                    key="mg=${mgid:-misc}|sc=${sid:-misc}"
                else
                    key="mg=misc|sc=misc"
                fi

                accumulate "$fpath" "$key"
            done < <(find "$time_dir" -type f -print0)

            # Emit per-bucket summary lines
            for key in "${!bucket_counts[@]}"; do
                count="${bucket_counts[$key]}"
                bytes="${bucket_sizes[$key]}"
                # Convert bytes to MB with 2 decimals
                sum_mb=$(awk -v b="$bytes" 'BEGIN {printf "%.2f", b/1024/1024}')

                # Extract raw mgid and sid values (no mg= or sc= prefixes)
                mgid="${key#mg=}"
                mgid="${mgid%%|*}"
                sid="${key#*|sc=}"

                # Normalize empty to misc (shouldn't happen, but safe)
                if [[ -z "$mgid" ]]; then mgid="misc"; fi
                if [[ -z "$sid" ]]; then sid="misc"; fi

                line="$variable,$grid,$time_unit,$mgid,$sid,$count,$sum_mb"
                echo "$line"
                echo "$line" >> "$output_file"
            done

            # Cleanup for next iteration
            unset bucket_counts
            unset bucket_sizes
        done
    done
done

echo "Check complete"