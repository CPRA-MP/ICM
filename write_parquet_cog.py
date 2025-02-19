import pandas as pd
import polars as pl
import subprocess
import argparse
import getpass as gp
import datetime as dt
import glob
import numpy as np
import sys
import os
import itertools
import time

from cpra.mp.data import write_data, read_fortran_array

# filepaths
api_variables = r"/ocean/projects/bcs200002p/hjaehn/cpra.mp.data/cpra/mp/data/structure/variables.csv"
api_dimension_mapping = r"/ocean/projects/bcs200002p/shared/upload-tracker/CPRA MP29 Model Data Structure Upload Tracker.xlsx"
api_variable_tracker = r"/ocean/projects/bcs200002p/shared/upload-tracker/CPRA MP29 Model Data Structure Upload Tracker.xlsx"

# To Run on PSC:
# change your filepath by typing in the command >>> cd /ocean/projects/bcs200002p/hjaehn/mp29_pct/data_processing
# run the file >>> ./batch_queue.sh

def find_variable_files(variable_metadata_series, convert_list):
    convert_dict = {} 
    path = variable_metadata_series['path']
    for filepath in glob.iglob(path, recursive = True):
        scenario = filepath.split(os.path.sep)[7]
        model_group = filepath.split(os.path.sep)[8]
        if (scenario, model_group) not in convert_dict.keys():
            convert_dict[(scenario, model_group)] = [filepath]
        else:
            convert_dict[(scenario, model_group)] = convert_dict[(scenario, model_group)] + [filepath]
    convert_dict = {key: convert_dict[key] for key in convert_list if key in convert_dict}
    return convert_dict

def read_variable_metadata(variable_name):
    df = pd.read_csv(api_variables)
    series = df[df['name'] == variable_name].T.iloc[:,0]
    return series

def read_variable_dimensions(variable_metadata_series):
    df = pd.read_excel(api_dimension_mapping, sheet_name="_Dimension Mapping")
    df = df[(df['name'] == variable_metadata_series['name']) & (df['time_units'] == variable_metadata_series['time_units'])]
    return df

def format_icm_hydro_annual_output(filepath, variable_metadata_series):
    dimensions = read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list()
    if filepath.endswith('.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["ICM_ID"], index_col='ICM_ID', compression='zip')
    else:
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["ICM_ID"], index_col='ICM_ID')
    df = df[df.index < 1658]
    df = df.set_index(df.index.astype(int)) 
    df = df.rename(columns={old_col: new_col for old_col, new_col in zip(read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list(), 
                                                                         read_variable_dimensions(variable_metadata_series)['Dimension Value'].to_list())})
    df = df.transpose().reset_index().rename(columns={'index':variable_metadata_series['required_dimensions']})
    df['calendar_year'] = np.int32(int(filepath.split(os.path.sep)[-1].split(".")[0][-4:]))
    df['scenario_id'] = np.int32(int(filepath.split(os.path.sep)[7][-2:]))
    df['model_group_id'] = np.int32(int(filepath.split(os.path.sep)[8][-3:]))
    df['variable'] = variable_metadata_series['name']
    df['time_unit'] = variable_metadata_series['time_units']
    df['model'] = variable_metadata_series['model'] + "_v2023.0.0"
    return df

def format_icm_hydro_monthly_ouput(filepath, variable_metadata_series):
    start = dt.date(int(os.path.basename(filepath)[-12:-8]),1,1) # reads year after .csv.zip
    dates = [dt.date(start.year + (start.month + i - 1) // 12, ((start.month + i - 1) % 12) + 1, 1) for i in range(12)]
    if filepath.endswith('.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], index_col='comp', compression='zip')
    else: 
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], index_col='comp')
    df.index = df.index.astype(int)
    df = df.rename(columns={old_col: new_col for old_col, new_col in zip(df.columns.to_list(), dates)})
    df = df.transpose().reset_index().rename(columns={'index':'calendar_day'})
    df = df[[col for col in df.columns if col == 'calendar_day' or col < 1658]]
    df['scenario_id'] = np.int32(int(filepath.split(os.path.sep)[7][-2:]))
    df['model_group_id'] = np.int32(int(filepath.split(os.path.sep)[8][-3:]))
    df['variable'] = variable_metadata_series['name']
    df['time_unit'] = variable_metadata_series['time_units']
    df['model'] = variable_metadata_series['model'] + "_v2023.0.0"
    if "mean" in filepath:
        df[f'{variable_metadata_series['required_dimensions']}'] = read_variable_dimensions(variable_metadata_series)['Dimension Value'].values[0]
    elif "max" in filepath:
        df[f'{variable_metadata_series['required_dimensions']}'] = read_variable_dimensions(variable_metadata_series)['Dimension Value'].values[1]
    else:
        df[f'{variable_metadata_series['required_dimensions']}'] = read_variable_dimensions(variable_metadata_series)['Dimension Value'].values[0]
    return df

def format_icm_hydro_daily_output(filepath, variable_metadata_series): 
    hydrocomp = [x for x in range(1,1788)]
    start = dt.date(2019,1,1)
    end = start + dt.timedelta(days=52*365.25)
    dates = [start + dt.timedelta(days=x) for x in range((end - start).days)] 
    if filepath.endswith('.zip'):
        df = pd.read_csv(filepath, names=hydrocomp, dtype=variable_metadata_series['dtype'], compression='zip')
    else:
        df = pd.read_csv(filepath, names=hydrocomp, dtype=variable_metadata_series['dtype'])
    df = df[df.columns[df.columns.astype(int) < 1658]]
    df['calendar_day'] = pd.Series(dates)
    df['scenario_id'] = np.int32(int(os.path.basename(filepath)[8:10])) 
    df['model_group_id'] = np.int32(int(os.path.basename(filepath)[12:15])) 
    df['variable'] = variable_metadata_series['name']
    df['time_unit'] = variable_metadata_series['time_units']
    df['model'] = variable_metadata_series['model'] + "_v2023.0.0"
    df[f'{variable_metadata_series['required_dimensions']}'] = read_variable_dimensions(variable_metadata_series)['Dimension Value'].values[0]
    return df

def format_icm_veg_annual_output(filepath, variable_metadata_series):
    dimensions = read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list()
    if filepath.endswith('.asc+.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["CELLID"], index_col='CELLID', compression='zip', skiprows=371, sep=', ', engine='python')
    elif filepath.endswith('.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["CELLID"], index_col='CELLID', compression='zip') # confirm index column
    else:
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["CELLID"], index_col='CELLID') # confirm index column
    df = df.rename(columns={old_col: new_col for old_col, new_col in zip(read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list(), 
                                                                         read_variable_dimensions(variable_metadata_series)['Dimension Value'].to_list())})
    df = df.transpose().reset_index().rename(columns={'index':variable_metadata_series['required_dimensions']})
    df['calendar_year'] = np.int32(int(os.path.basename(filepath).split("_")[8])) + 2018 
    df['scenario_id'] = np.int32(int(filepath.split(os.path.sep)[7][-2:]))
    df['model_group_id'] = np.int32(int(filepath.split(os.path.sep)[8][-3:]))
    df['variable'] = variable_metadata_series['name']
    df['time_unit'] = variable_metadata_series['time_units']
    df['model'] = variable_metadata_series['model'] + "_v2023.0.0"
    return df

def apply_formatting(variable_metadata_series, filepath, time_unit, geographic_unit):
       
    veg_format_functions = {'annual': format_icm_veg_annual_output}

    hydro_format_functions = {'daily': format_icm_hydro_daily_output, 
                              'annual': format_icm_hydro_annual_output,
                              'monthly': format_icm_hydro_monthly_ouput} 
    
    geographic_functions = {'hydro_compartment': hydro_format_functions,
                            'veg_grid_cell': veg_format_functions}

    df = geographic_functions[geographic_unit][time_unit](filepath=filepath, variable_metadata_series=variable_metadata_series)
    return df

def upload_icm_annual(variable_metadata_series, convert_list):
    start_time = time.time()
    convert_dict = find_variable_files(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units','required_dimensions']]])
    upload_df = pd.DataFrame()
    for k, v in convert_dict.items():
        print(k, v)
        for path in v:
            upload_df = pd.concat([upload_df, apply_formatting(variable_metadata_series=variable_metadata_series, filepath=path, time_unit=variable_metadata_series['time_units'], geographic_unit=variable_metadata_series['geographic_units'])])
    data = pl.from_pandas(upload_df)
    print(data)
    write_data(data=data, grid=variable_metadata_series['geographic_units'] + '_v001')
    print(variable_metadata_series['name'] + " was saved in oceans!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    return print(f"Elapsed time: {elapsed_time} seconds")

def upload_icm_daily(variable_metadata_series, convert_list):
    start_time = time.time()
    convert_dict = find_variable_files(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units','required_dimensions']]])
    for k, v in convert_dict.items():
        print(k, v)
        upload_df = pd.DataFrame()
        for path in v:
            upload_df = pd.concat([upload_df, apply_formatting(variable_metadata_series=variable_metadata_series, filepath=path, time_unit=variable_metadata_series['time_units'], geographic_unit=variable_metadata_series['geographic_units']) ]) 
        data = pl.from_pandas(upload_df)
        print(data)
        write_data(data=data, grid=variable_metadata_series['geographic_units'] + '_v001')
    print(variable_metadata_series['name'] + " was saved in oceans!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    return print(f"Elapsed time: {elapsed_time} seconds")

def upload_icm_monthly(variable_metadata_series, convert_list):
    start_time = time.time()
    convert_dict = find_variable_files(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units','required_dimensions']]])
    upload_df = pd.DataFrame()
    for k, v in convert_dict.items():
        print(k, v)
        for path in v:
            upload_df = pd.concat([upload_df, apply_formatting(variable_metadata_series=variable_metadata_series, filepath=path, time_unit=variable_metadata_series['time_units'], geographic_unit=variable_metadata_series['geographic_units']) ]) 
    data = pl.from_pandas(upload_df)
    print(data)
    write_data(data=data, grid=variable_metadata_series['geographic_units'] + '_v001')
    print(variable_metadata_series['name'] + " was saved in oceans!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    return print(f"Elapsed time: {elapsed_time} seconds")

def upload_cog(variable_metadata_series, convert_list):
    start_time = time.time()
    convert_dict = find_variable_files(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units']]])
    for k, v in convert_dict.items():              
        print(f'the rasters for {k} are being uploaded:')
        for path in v:
            print(f'    calendar year: {np.int32(int(os.path.basename(path).split("_")[8]))+2018}')
            print(f'    {path} is uploading!')
            write_data(data=read_fortran_array(filename=path, variable=variable_metadata_series['name']),
                        dtype=variable_metadata_series['dtype'],
                        variable=variable_metadata_series['name'],
                        time_unit = 'annual', #all rasters are annual
                        grid=variable_metadata_series['geographic_units'] + '_v001', #all mp23 data is v001
                        model=variable_metadata_series['model'] + "_v2023.0.0", #all mp23 icm outputs are v2023.0.0
                        scenario_id=k[0][1:],
                        model_group_id=k[1][1:],
                        calendar_year=np.int32(int(os.path.basename(path).split("_")[8]))+2018)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return print(f"Elapsed time: {elapsed_time} seconds")

def upload_icm(time_unit):
    upload_functions = {'daily': upload_icm_daily,
                        'annual': upload_icm_annual,
                        'monthly': upload_icm_monthly}
    return upload_functions[time_unit]

def read_upload_tracker(variable_queue):
    df = pd.read_excel(api_variable_tracker, sheet_name="_Upload Tracker", header=0)
    df = df[df['name'] == variable_queue]
    return df 

def upload_files(modelgroups, scenarios, variable_queue):
    convert_list = list(itertools.product(scenarios, modelgroups)) 
    print(convert_list)
    variables_upload_tracker = read_upload_tracker(variable_queue)
    for variable_metadata_series in [row for index, row in variables_upload_tracker.iterrows() if 'in-progress' in row['status'] and 'parquet' in row['type']]:
        upload_icm(time_unit=variable_metadata_series['time_units'])(variable_metadata_series, convert_list)
    for variable_metadata_series in [row for index, row in variables_upload_tracker.iterrows() if 'in-progress' in row['status'] and 'cog' in row['type']]:
        upload_cog(variable_metadata_series, convert_list)
    return print('Done')

def list_of_strs(arg):
    return list(map(str, arg.split(',')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variable_queue", type=str, dest="variable_queue", help="Job specific variables to be uploaded")
    parser.add_argument("--model_groups", type=list_of_strs, dest="modelgroups", help="Job specific modelgroups to be uploaded")
    parser.add_argument("--scenarios", type=list_of_strs, dest="scenarios", help="Job specific scenarios to be uploaded")
    args = parser.parse_args()

    upload_files(modelgroups=args.modelgroups,
                 scenarios=args.scenarios,
                 variable_queue=args.variable_queue)
    