#launch apptainer with cpra api:
#/ocean/projects/bcs200002p/shared/python/cpra-python3

from cpra.mp.data import write_data
from cpra.mp.data.variables import VARIABLES

import argparse
from datetime import date
import os
import pandas as pd
import time

script_name = os.path.basename(__file__)

#api var name: hydro file name
hydro_var_lookup = {
    "flom": "FLOm.out",
    "sal": "SAL.out",
    "sedacc": "SedAcc.out",
    "sedacc_marshedge": "SedAcc_MarshEdge.out",
    "sedacc_marshint": "SedAcc_MarshInt.out",
    "stg": "STG.out",
    "tmp": "TMP.out",
    "trg": "TRG.out",
    "tss": "TSS.out",
    "stgm": "STGm.out" 
    }

aggregate_type='mean'

#change file access for files created within a window
def chmod_recent_files(directory_path, octal_mode=0o667, minutes=1):

    cutoff_time = time.time() - (minutes * 60) #time in seconds

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isfile(file_path):
            #file metadata
            file_stat = os.stat(file_path)
            
            #check file mod time
            if file_stat.st_mtime >= cutoff_time:
                os.chmod(file_path, octal_mode)

#only read what you need to minimize memory requirement
def read_single_year(csv_path, start_year, target_year):

    model_start_date = date(start_year, 1, 1)
    target_start_date = date(target_year, 1, 1)
    target_end_date = date(target_year + 1, 1, 1)

    #number of daily rows before the requested year.
    rows_to_skip = (target_start_date - model_start_date).days

    #number of rows in the requested year, 365 or 366.
    rows_to_read = (target_end_date - target_start_date).days

    df = pd.read_csv(
        csv_path,
        header=None,
        names=None,
        skiprows=rows_to_skip,
        nrows=rows_to_read,
    )

    df.columns = (df.columns + 1).astype("int32")

    df.insert(
        0,
        "calendar_day",
        pd.date_range(
        start=f"{target_year}-01-01",
        periods=rows_to_read,
        freq="D"
        )
    )

    #for verification only, not used in calculations or write_data
    date_min = df["calendar_day"].min().date()
    date_max = df["calendar_day"].max().date()

    print(f"Read CSV Output Complete\n\
          start_year: {start_year} target_year: {target_year}\n\
          rows_to_skip: {rows_to_skip} rows_to_read: {rows_to_read}\n\
          date_min: {date_min} date_max: {date_max}")

    return df

def postprocess_hydro(year,base_icm,model,grid_version,start_year,sterm,gterm):

    scenario_id = int(sterm[1:])
    model_group_id = int(gterm[1:])

    for var, file in hydro_var_lookup.items():

        print(f"Begin processing {var}")
        
        var_properties = VARIABLES[var]
        var_dtype = str(var_properties.dtype)

        geographic_units = var_properties.geographic_units[0]
        grid_str = f'{geographic_units}{grid_version}'

        filepath = f'{base_icm}/{file}'

        #read dataframe here
        df = read_single_year(filepath, start_year, year)

        #select columns for compartments only, use this for averaging
        numeric_cols = df.select_dtypes(include="number").columns
        
        if 'daily' in var_properties.time_units:
            time_unit='daily'
        
            df_daily = df.copy() # create a copy of df, need df with pandas-type dates for later

            # after filtering we need to convert pandas date to python date for final write_data
            df_daily["calendar_day"] = df_daily["calendar_day"].dt.date

            # convert results datatype
            df_daily[numeric_cols] = df_daily[numeric_cols].astype(var_dtype)

            #write data to view in mpdp
            write_data(data=df_daily,
                        variable=var,
                        time_unit=time_unit,
                        grid=grid_str,
                        model=model,
                        scenario_id=scenario_id,
                        model_group_id=model_group_id,
                        aggregate_type=aggregate_type
                        )

            print(f"Daily processing for {var} complete")

            directory_path = f"/ocean/projects/bcs200002p/shared/data/variable={var}/grid={grid_str}/time_unit={time_unit}/model_group_id={model_group_id}/scenario_id={scenario_id}/aggregate_type={aggregate_type}"
            chmod_recent_files(directory_path)

        if 'monthly' in var_properties.time_units:
            time_unit='monthly'

            # calculate monthly average
            df_monthly = (
                df
                .groupby(df["calendar_day"].dt.to_period("M"))[numeric_cols]
                .mean()
                .reset_index()
            )
            
            df_monthly["calendar_day"] = df_monthly["calendar_day"].dt.to_timestamp().dt.date
            df_monthly[numeric_cols] = df_monthly[numeric_cols].astype(var_dtype)

            #write data to view in mpdp
            write_data(data=df_monthly,
                        variable=var,
                        time_unit=time_unit,
                        grid=grid_str,
                        model=model,
                        scenario_id=scenario_id,
                        model_group_id=model_group_id,
                        aggregate_type=aggregate_type
                        )

            print(f"Monthly processing for {var} complete")

            directory_path = f"/ocean/projects/bcs200002p/shared/data/variable={var}/grid={grid_str}/time_unit={time_unit}"
            chmod_recent_files(directory_path)

        if 'annual' in var_properties.time_units:
            time_unit='annual'

            # calculate annual average
            df_annual = (
                df
                .groupby(df["calendar_day"].dt.to_period("Y"))[numeric_cols]
                .mean()
                .reset_index()
            )

            # convert calendar_day to calendar_year and assign datatype for year values
            df_annual["calendar_year"] = (
                df_annual.pop("calendar_day")
                .dt.year
                .astype("int32")
            )

            df_annual[numeric_cols] = df_annual[numeric_cols].astype(var_dtype)

            #write data to view in mpdp
            write_data(data=df_annual,
                        variable=var,
                        time_unit='annual',
                        grid=grid_str,
                        model=model,
                        scenario_id=scenario_id,
                        model_group_id=model_group_id,
                        aggregate_type='mean'
                        )

            print(f"Annual processing for {var} complete")

            directory_path = f"/ocean/projects/bcs200002p/shared/data/variable={var}/grid={grid_str}/time_unit={time_unit}"
            chmod_recent_files(directory_path)

def main():
    #Expected values to be read in from ICM_control.csv
    # base_icm = '/ocean/projects/bcs200002p/ewhite12/MP2029/ICMv26/S##/G###/[hydro,geomorph,veg]'
    # model = 'icm_v26.0.0'
    # grid_version = '_v002'
    # start_year = 2025
    
    parser = argparse.ArgumentParser()
    #yearly value from ICM.py iterations
    parser.add_argument("--year", required=True, type=int)

    #static values read from ICM_control.csv
    parser.add_argument("--base_icm", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--grid_version", required=True)
    parser.add_argument("--start_year", required=True, type=int)
    parser.add_argument("--sterm", required=True)
    parser.add_argument("--gterm", required=True)

    args = parser.parse_args()

    postprocess_hydro(
        year=args.year,
        base_icm=args.base_icm,
        model=args.model,
        grid_version=args.grid_version,
        start_year=args.start_year,
        sterm=args.sterm,
        gterm=args.gterm
        )

    print(f"{script_name} completed for year {args.year}")

if __name__ == "__main__":
    main() 
