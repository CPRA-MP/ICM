import pandas as pd
import polars as pl
import polars.selectors as cs
import rasterio
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
import zipfile
import sqlalchemy
import psycopg2
import rasterio as rio
from cpra.mp.data import write_data, read_fortran_array
from cpra.mp.data.variables import VARIABLES
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# for connection and paths
username = r'hjaehn'
password = ''

# filepaths
api_variables = fr"/ocean/projects/bcs200002p/{username}/cpra.mp.data/cpra/mp/data/structure/variables.csv"
api_grids = fr"/ocean/projects/bcs200002p/{username}/cpra.mp.data/cpra/mp/data/structure/grids.csv"
api_dimensions = fr"/ocean/projects/bcs200002p/{username}/cpra.mp.data/cpra/mp/data/structure/dimensions.csv"
api_dimension_mapping = r"/ocean/projects/bcs200002p/shared/upload-tracker/CPRA MP29 Model Data Structure Upload Tracker.xlsx"
api_variable_tracker = r"/ocean/projects/bcs200002p/shared/upload-tracker/CPRA MP29 Model Data Structure Upload Tracker.xlsx"
local_storage = fr"/ocean/projects/bcs200002p/{username}/testing"
veg_grid_path = r"/ocean/projects/bcs200002p/hjaehn/testing/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_V_grid480.tif" # [ ] move to the shared folder

# constants
# [ ] need to call these as variables instead of hard coding
model_version ='_v2023.0.0'
grid_version = '_v001'

# NOTE To Run on PSC:
# NOTE change your filepath by typing in the command >>> cd /ocean/projects/bcs200002p/hjaehn/mp29_pct/data_processing
# NOTE run the file >>> ./batch_queue.sh

def find_variable_files(variable_metadata_series, convert_list):
    if convert_list == [("S00","G000")]:
        convert_dict = {('S00', 'G000'): [variable_metadata_series['path']]} 
    else:
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
    start = dt.date(int(os.path.basename(filepath)[-12:-8]),1,1) # NOTE reads year after .csv.zip
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
    # [ ] change this to the handler dictionary method
    if filepath.endswith('.asc+.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["CELLID"], index_col='CELLID', compression='zip', skiprows=371, sep=', ', engine='python')
    elif filepath.endswith('.asc+'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["CELLID"], index_col='CELLID', skiprows=371, sep=', ', engine='python')
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
    df['grid'] = variable_metadata_series['geographic_units'] + "_v001"

    # Sort the dataframe so that the veg cells are in the correct order for creating the raster
    int_columns = [col for col in df.columns if isinstance(col, int)]
    non_int_columns = [col for col in df.columns if not isinstance(col, int)]
    sorted_int_columns = sorted(int_columns)
    sorted_columns = sorted_int_columns + non_int_columns
    df = df[sorted_columns]
    return df

def format_icm_ecoregion_annual_output(filepath, variable_metadata_series):
    dimensions = read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list()
    print(dimensions)
    if filepath.endswith('.zip'):
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["er_n"], index_col='er_n', compression='zip')
    else:
        df = pd.read_csv(filepath, dtype=variable_metadata_series['dtype'], usecols=dimensions+["er_n"], index_col='er_n')
    df = df[df.index < 33] # NOTE this drops the -9999 no data value
    df = df.set_index(df.index.astype(int)) 
    df = df.rename(columns={old_col: new_col for old_col, new_col in zip(read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list(), 
                                                                         read_variable_dimensions(variable_metadata_series)['Dimension Value'].to_list())})
    df = df.transpose().reset_index().rename(columns={'index':variable_metadata_series['required_dimensions']}) # [ ] right now this pulls the first value from the list, need to make it more robust
    print(df)
    # [ ] this works but needs to be improved for readability
    if 'percentile' in variable_metadata_series['required_dimensions']:
        df['percentile'] = df[f'{variable_metadata_series['required_dimensions']}'].apply(lambda x: int(x[-2:])) # NOTE this splits out the variable name from the percentile, assumes percentile is last two digits in column
        df[f'{read_variable_dimensions(variable_metadata_series)['Required Dimension'][0]}'] = df[f'{variable_metadata_series['required_dimensions']}'].str[:5] # NOTE drops the percentile from the string
        df.drop(columns=[f'{variable_metadata_series['required_dimensions']}'], inplace=True) # NOTE drop the column once you create the other two
        print(df['percentile'])
        print(df[f'{read_variable_dimensions(variable_metadata_series)['Required Dimension'][0]}'])
    df['calendar_year'] = 2018 # NOTE this only is needed for inputs right now so not a problem, but could be one later...
    df['scenario_id'] = np.int32(int(filepath.split(os.path.sep)[7][-2:]))
    df['model_group_id'] = np.int32(int(filepath.split(os.path.sep)[8][-3:]))
    df['variable'] = variable_metadata_series['name']
    df['time_unit'] = variable_metadata_series['time_units']
    df['model'] = variable_metadata_series['model'] + "_v2023.0.0"
    df = check_dtype_conversions(df)
    return df

def apply_formatting(variable_metadata_series, filepath, time_unit, geographic_unit):
       
    ecoregion_format_functions = {'annual': format_icm_ecoregion_annual_output} # [ ] need to add ecoregion functions when available
    
    veg_format_functions = {'annual': format_icm_veg_annual_output}

    hydro_format_functions = {'daily': format_icm_hydro_daily_output, 
                              'annual': format_icm_hydro_annual_output,
                              'monthly': format_icm_hydro_monthly_ouput} 
    
    geographic_functions = {'ecoregion': ecoregion_format_functions,
                            'hydro_compartment': hydro_format_functions,
                            'veg_pixel': veg_format_functions}

    df = geographic_functions[geographic_unit][time_unit](filepath=filepath, variable_metadata_series=variable_metadata_series)
    return df

def upload_parquet_annual(variable_metadata_series, convert_list):
    geo_check = read_variable_metadata(variable_metadata_series['name']).loc['geographic_units']
    # NOTE the below checks to make sure that we have tested that grid
    if geo_check == 'hydro_compartment': 
        pass
    elif geo_check == 'ecoregion':
        pass 
    else:
        print(f"Geographic unit {geo_check} has not been tested, please check you result.")
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
    print(f"Elapsed time: {elapsed_time} seconds")

def upload_parquet_daily(variable_metadata_series, convert_list):
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
    print(f"Elapsed time: {elapsed_time} seconds")

def upload_parquet_monthly(variable_metadata_series, convert_list):
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
    print(f"Elapsed time: {elapsed_time} seconds")

def convert_veg_to_raster(data, variable_name):
    # NOTE primarily pulled using matt's script in the cpra.mp.data repo
    """Convert vegetation grid data to raster images."""
    variable = VARIABLES[variable_name]
    numpy_dtype = pl.Series(dtype=variable.dtype).to_numpy().dtype
    
    with rio.open(veg_grid_path
    ) as dataset:
        mask = dataset.dataset_mask().astype(numpy_dtype)
        mask[mask == 0] = -9999
        # The veg cell are numbered from bottom to top, left to right.
        flipped_mask = np.flip(mask, 0)

    lf = pl.LazyFrame(data) # convert DataFrame to polars LazyFrame
    dims = lf.select(cs.matches(r"^[a-z]")).collect()

    for i, row in enumerate(lf.select(cs.digit()).collect().iter_rows()):
        flipped_data = flipped_mask.copy()
        flipped_data[flipped_data == 255] = row
        row_dims = dims[i].to_dicts()[0]

        print(f"Writing data for: {row_dims!s}...")
        write_data(np.flip(flipped_data, 0), validate=False, **row_dims)

def upload_veg_annual(variable_metadata_series, convert_list):
    start_time = time.time()
    convert_dict = find_variable_files(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    # NOTE removed the required dimensions - manually added for veg pixel data
    # [ ] rewrite the note above
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units','required_dimensions']]]) 
    for k, v in convert_dict.items():
        print(f'the rasters for {k} are being uploaded:')
        for path in v:
            if check_filepath(path, k[0], k[1], variable_metadata_series):
                print(f'    {path} is uploading!')
                print(f'        calendar year: {np.int32(int(os.path.basename(path).split("_")[8]))+2018}')
                data = apply_formatting(variable_metadata_series=variable_metadata_series, filepath=path, time_unit=variable_metadata_series['time_units'], geographic_unit=variable_metadata_series['geographic_units'])
                convert_veg_to_raster(data=data, variable_name=variable_metadata_series['name']) # convert the parquet file to a raster
            else:
                print(f'    {path} is not needed, skipped!\n')
    print(variable_metadata_series['name'] + " was saved in oceans!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

def upload_cog(variable_metadata_series, convert_list, storage):
    geo_check = read_variable_metadata(variable_metadata_series['name']).loc['geographic_units']
    if geo_check == 'veg_grid_cell': # NOTE veg grid cell data gets treated differently...
        upload_veg_annual(variable_metadata_series=variable_metadata_series, convert_list=convert_list)
    else:
        start_time = time.time()
        convert_dict = find_variable_files(variable_metadata_series, convert_list)
        variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units']]])

        os.makedirs(storage, exist_ok=True)
        for k, v in convert_dict.items():
            print(f'The rasters for {k} are being uploaded:')
            for path in v:
                if check_filepath(path, k[0], k[1], variable_metadata_series): # NOTE this checks to see if the file has already been uploaded
                    process_path(path, k, variable_metadata_series, storage)
                else:
                    print(f'    {path} is not needed, skipped!\n')
                    
        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time} seconds")

def process_path(path, k, variable_metadata_series, storage):
    print(f'    {path} is uploading!')
    calendar_year = extract_calendar_year(path)
    print(f'        calendar year: {calendar_year}')

    # File extension to handler function map
    ext = os.path.splitext(path)[1].lower()
    handlers = {
        '.zip': lambda: process_zip(path, k, variable_metadata_series, storage, calendar_year),
        '.asc': lambda: process_asc(path, k, variable_metadata_series, calendar_year),
        '.tif': lambda: process_tif(path, k, variable_metadata_series, calendar_year),
    }
    # Use the fortran binary handler as the default since it handles multiple file types (.xyz, .bin, etc.)
    handler = handlers.get(ext, lambda: process_binary(path, k, variable_metadata_series, calendar_year)) # NOTE see process zip for todo
    handler()

def process_zip(path, k, variable_metadata_series, storage, calendar_year):
    # NOTE need to look a recursive function to see if we can call the previous handler
    # NOTE also need to look at the default 
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(storage)
        for file_name in zip_ref.namelist():
            unzipped_path = os.path.join(storage, file_name)
            print(f'        extracted: {unzipped_path}')
            if os.path.isfile(unzipped_path):
                ext = os.path.splitext(unzipped_path)[1].lower()
                handlers = {
                    '.asc': lambda: process_asc(unzipped_path, k, variable_metadata_series, calendar_year),
                    '.tif': lambda: process_tif(unzipped_path, k, variable_metadata_series, calendar_year),
                }
                handlers.get(ext, lambda: process_binary(unzipped_path, k, variable_metadata_series, calendar_year))() # [ ] this will move up to the dictionary, then use handlers[ext]()
                os.remove(unzipped_path)
                print(f'        deleted unzipped file...\n')

def process_asc(path, k, variable_metadata_series, calendar_year):
    data = np.loadtxt(path, skiprows=6)
    write_cog(data, k, variable_metadata_series, calendar_year)

def process_tif(path, k, variable_metadata_series, calendar_year):
    with rasterio.open(path) as src:
        data = src.read(1)
        write_cog(data, k, variable_metadata_series, calendar_year)

def process_binary(path, k, variable_metadata_series, calendar_year):
    data = read_fortran_array(filename=path, variable=variable_metadata_series['name'])
    data = check_null_rows(data, variable_metadata_series)
    write_cog(data, k, variable_metadata_series, calendar_year)
    print(f'        uploaded: {path}')

def check_null_rows(data, variable_metadata_series):
    # NOTE this is a fix for the morph pixel binary outputs to make sure we are reshaping the data correctly
    # NOTE this will need to be used to post process outputs
    grids = pd.read_csv(api_grids)
    expected_rows = int(grids.loc[grids["name"] == variable_metadata_series['geographic_units'] + '_v001', "height"].values[0])
    expected_cols = int(grids.loc[grids["name"] == variable_metadata_series['geographic_units'] + '_v001', "width"].values[0])
    try:
        data = data.reshape((expected_rows, expected_cols))
    except Exception as e:
        print(f'        could not reshape to grid: {e}')
        data = data.reshape((expected_rows + 20, expected_cols)) # [ ] need to change this logic to be better
    if data.shape[0] > expected_rows: # NOTE checks to see if we have the right amount of rows
        data = data[:expected_rows] # [ ] add additional checks to make sure we are trimming the right rows
        print(f'        trimmed to expected rows: {expected_rows}')
    return data

def extract_calendar_year(path):
    # NOTE this only works for MP23 data
    try:
        return np.int32(int(os.path.basename(path).split("_")[8])) + 2018
    except Exception:
        return 2018 # for inputs we have to hard code it to be 2018 since the basename is different

def write_cog(data, k, variable_metadata_series, calendar_year):
    write_data(
        data=data,
        dtype=variable_metadata_series['dtype'],
        variable=variable_metadata_series['name'],
        time_unit='annual',
        grid=variable_metadata_series['geographic_units'] + '_v001',
        model=variable_metadata_series['model'] + "_v2023.0.0",
        scenario_id=k[0][1:],
        model_group_id=k[1][1:],
        calendar_year=calendar_year)

def upload_parquet(time_unit):
    upload_functions = {'daily': upload_parquet_daily,
                        'annual': upload_parquet_annual,
                        'monthly': upload_parquet_monthly}
    return upload_functions[time_unit]

def create_pdd_connection(user, password):
    port = '5432'
    host = 'vm007.bridges2.psc.edu'
    db_name = 'mp23_pdd'
    connection_string = f'postgresql+psycopg2://{user}:%s@{host}:{port}/{db_name}' % quote_plus(password)
    engine = create_engine(connection_string)
    connection_info = {'host': host,
                    'dbname': db_name,
                    'user': user,
                    'password': password}
    connection_string = ' '.join([key + "='" + value + "'" for key, value in connection_info.items()])
    pdd_conn = psycopg2.connect(connection_string)
    return pdd_conn

def process_sql_statement(pdd_conn, path):
    sql_statement_full = f'SELECT * FROM {path}' 
    df = pd.read_sql_query(sql_statement_full, pdd_conn)
    return df

def clara_dtype_conversions(df, variable_metadata_series): 
    # todo: we can probably update this to be read from the csv's but this is okay for now
    # set the dtypes for the clara specific dimensions
    column_dtype_mapping = { # [ ]  bring this in from the structure csv
    'scenario_id': np.int32,
    'model_group_id': np.int32,
    'geographic_unit': str,
    'fragility_scenario': np.int8,
    'pumping_id': np.float32,
    'asset_type': np.int8,
    'calendar_year': np.int32,
    'variable': str,
    'percentile': np.int8,
    'population_variant':  np.int8,
    'clara_variant' : np.int8,
    'aep': np.float32
    }
    
    # Create the geographies list
    grids = pd.read_csv(api_grids)
    max_geographies = grids.loc[grids["name"] == (variable_metadata_series["geographic_units"] + "_v001"), 'id_count'].tolist()
    geographies = range(1, int(max_geographies[0]) + 1)

    # Assign dtypes to the dimensions in the DataFrame
    for column, dtype in column_dtype_mapping.items():
        if column in df.columns:
            df[column] = df[column].astype(dtype)

    # Assign dtypes to the output geographies
    for geography in geographies:
        if geography in df.columns:
            df[geography] = df[geography].astype(variable_metadata_series['dtype'])
    return df

def check_dtype_conversions(df):
    dimensions = pd.read_csv(api_dimensions)
    names = dimensions['name'].tolist()
    dtypes = dimensions['dtype'].tolist()
    dtypes = [dt.lower() for dt in dtypes] # NOTE this is annoying but it cant parse the capitalized versions
    column_dtype_mapping = dict(zip(names, dtypes))
    
    # Assign dtypes to the dimensions in the DataFrame
    for column, dtype in column_dtype_mapping.items():
        if column in df.columns:
            df[column] = df[column].astype(dtype)
    return df

def check_grid_geographies(df, variable_metadata_series):
    # Create the appropriate misssing geographies list
    grids = pd.read_csv(api_grids)
    max_geographies = grids.loc[grids["name"] == (variable_metadata_series["geographic_units"] + "_v001"), 'id_count'].tolist()
    geographies = range(1, int(max_geographies[0]) + 1)
    missing_geographies = [geography for geography in geographies if geography not in df.columns]
    
    # Create a DataFrame for missing geographies (batch insert)
    if missing_geographies:
        new_geographies = pd.DataFrame(
            {geography: None for geography in missing_geographies},
            index=df.index).astype(variable_metadata_series['dtype'])
        # Add all missing geographies to the main DataFrame at once
        df = pd.concat([df, new_geographies], axis=1)
        print(f'{len(missing_geographies)} null geographies were added to the {variable_metadata_series["name"]} table.')
    else:
        print(f'No new geographies were added to the {variable_metadata_series["name"]} table.')
    return df

def format_clara_outputs(df, variable_metadata_series):
    
    required_clara_dimensions = read_variable_dimensions(variable_metadata_series)
    
    # Create conditions to update SQL table
    condition_0 = (df['ModelGroup'] == 0)
    condition_1 = (df['ModelGroup'] == 500) & (df['Year_FWOA'] == 1)
    condition_2 = (df['ModelGroup'] == 500) & (df['Year_FWOA'] != 1)
    condition_3 = (df['ModelGroup'].isin([515, 516]))

    # Update the 'model_group_id' based on the conditions
    df.loc[condition_0, 'ModelGroup'] = 400
    df.loc[condition_1, 'ModelGroup'] = 401
    df.loc[condition_2, 'ModelGroup'] = 402
    df.loc[condition_3, 'ModelGroup'] = 403

    # Change the year to the correct value
    df['calendar_year'] =np.int32((df['Year_ICM'] + 2018) // 1)
    df['calendar_year'] = df['calendar_year'].apply(lambda x: 2020 if x == 2021 else x)

    # drop all columns that are not in the tracker sheet    
    df = df.drop(columns=[col for col in df.columns if col not in required_clara_dimensions['MP23 Dimension Value'].to_list()+['calendar_year']])

    # Update AEP if needed 
    if 'AEP' in df.columns:
        df['AEP'] = df['AEP'] * 100

    # melt the dataframe into its new format
    df = df.melt(id_vars=[col for col in df.columns if col not in required_clara_dimensions[required_clara_dimensions['Notes'] == "Output"]['MP23 Dimension Value'].to_list()],
                 value_vars=[col for col in df.columns if col in required_clara_dimensions[required_clara_dimensions['Notes'] == "Output"]['MP23 Dimension Value'].to_list()], 
                 var_name='variable',
                 value_name='value')

    # pivot the table to get the grid cells as columns
    df = df.pivot(index=[col for col in df.columns if col not in ['PointID', 'value']],  # Exclude 'PointID' from the index
                  columns='PointID',  
                  values='value')  

    df.columns.name=None
    df = df.reset_index()

    # Rename columns
    df = df.rename(columns={old_col: new_col for old_col, new_col in zip(read_variable_dimensions(variable_metadata_series)['MP23 Dimension Value'].to_list(), 
                                                                         read_variable_dimensions(variable_metadata_series)['Dimension Value'].to_list())}) # this will rename all the columns, need to add to the excel 

    # update percentile OR update exposure (this is a painful way to handle this)
    if 'percentile' in read_variable_metadata(variable_metadata_series['name'])['required_dimensions']:
        df['percentile'] = df['variable'].apply(lambda x: int(x[-2:])) # split out the variable name from the percentile
        df['variable'] = variable_metadata_series['name'] 
    if 'exposure_type' in read_variable_metadata(variable_metadata_series['name'])['required_dimensions']:
        df['exposure_type'] = df['variable'].replace({old_value: new_value for old_value, new_value in zip(required_clara_dimensions[required_clara_dimensions['Notes'] == "Output"]['MP23 Dimension Value'].to_list(), 
                                                                                                          required_clara_dimensions[required_clara_dimensions['Notes'] == "Output"]['Dimension Value'].to_list())})
        df['variable'] = variable_metadata_series['name']
    # add more elif's for our other use cases

    # create the new dimensions
    df['grid'] = variable_metadata_series['geographic_units'] + '_v001'
    df['time_unit'] = 'decadal' # standard value
    df['population_variant'] = 0 # set as a zero value
    df['clara_variant'] = 0 # set as a zero value
    df['model'] = 'clara_v2023.0.0' # standard value
    
    # update the dtypes
    df = clara_dtype_conversions(df, variable_metadata_series)

    return df

def upload_clara(variable_metadata_series):
    start_time = time.time()
    variable_metadata_series = pd.concat([variable_metadata_series, read_variable_metadata(variable_metadata_series['name']).loc[['dtype','geographic_units']]])
    print(f"Loading data for {variable_metadata_series['name']} from the PDD...")
    load_start = time.time()
    df = process_sql_statement(create_pdd_connection(username, password), variable_metadata_series['path'])
    load_end = time.time()
    print(f"Data loaded in {load_end-load_start} seconds")
    df = format_clara_outputs(df, variable_metadata_series)
    df = check_grid_geographies(df, variable_metadata_series)
    data = pl.from_pandas(df)
    print(data)
    write_data(data=data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

def read_upload_tracker(variable_queue):
    df = pd.read_excel(api_variable_tracker, sheet_name="_Upload Tracker", header=0)
    df = df[df['name'] == variable_queue]
    return df 

def upload_files(modelgroups, scenarios, variable_queue, storage):
    convert_list = list(itertools.product(scenarios, modelgroups)) 
    print(convert_list)
    variables_upload_tracker = read_upload_tracker(variable_queue)
    for variable_metadata_series in [row for index, row in variables_upload_tracker.iterrows() if 'in-progress' in row['status'] and 'parquet' in row['type']]:
        upload_parquet(time_unit=variable_metadata_series['time_units'])(variable_metadata_series, convert_list)
    for variable_metadata_series in [row for index, row in variables_upload_tracker.iterrows() if 'in-progress' in row['status'] and 'cog' in row['type']]:
        upload_cog(variable_metadata_series, convert_list, storage)
    for variable_metadata_series in [row for index, row in variables_upload_tracker.iterrows() if 'in-progress' in row['status'] and 'clara' in row['type']]:
        upload_clara(variable_metadata_series)

def check_filepath(filepath, scenario_str, model_group_str, variable_metadata_series):  
    scenario_match = scenario_str in os.path.basename(filepath)
    model_group_match = model_group_str in os.path.basename(filepath)
    try:
        year_check = np.int32(int(os.path.basename(filepath).split("_")[8])) < 53 # NOTE only relevant for converting MP23, will need to be updated to use calendar_year for future model versions
    except:
        year_check = True # for inputs we have to hard code it to be 2018 since the basename is different
    # [ ] create a new line that creates glob list, then new line "if length of glob list > 1 then true"
    file_check = not glob.glob(f'/ocean/projects/bcs200002p/shared/data/variable={variable_metadata_series["name"]}/grid={variable_metadata_series["geographic_units"] + "_v001"}/time_unit=annual/model_group_id={model_group_str[1:]}/scenario_id={scenario_str[2:]}/**/{int(os.path.basename(filepath).split("_")[8]) + 2018}.tif', recursive=True)
    final_flag = scenario_match and model_group_match and year_check and file_check
    return final_flag

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
                 variable_queue=args.variable_queue,
                 storage=local_storage)
