#launch apptainer with cpra api:
#/ocean/projects/bcs200002p/shared/python/cpra-python3

from cpra.mp.data.config import BASE_PATH
from cpra.mp.data.grids import GRIDS
from cpra.mp.data.variables import VARIABLES
from cpra.mp.data.raster import cog_path_expression
from cpra.mp.data.utils import cast_columns, validate_data_frame

import argparse
import numpy as np
import os
import pandas as pd
from pathlib import Path
import polars as pl
import rasterio as rio
from rasterio.transform import from_bounds, rowcol

script_name = os.path.basename(__file__)

# columns from output file: 
# WeigtedFFIBS | pct_vglnd_BLHF | pct_vglnd_SWF | pct_vglnd_FM | pct_vglnd_IM | pct_vglnd_BM | pct_vglnd_SM

# api variable = ffibs_score 
# output column = WeigtedFFIBS

vars_to_process= ['ffibs_score']
validate=True

def kwargs_function(**kwargs):
    return kwargs

def postprocess_ffibs_scr(year,base_icm,model,grid_version,start_year,sterm,gterm):

    var = vars_to_process[0]

    print(f"Begin processing {var}")

    var_properties = VARIABLES[var]
    var_dtype = var_properties.dtype
    var_time_unit = var_properties.time_units[0]
    geographic_units = var_properties.geographic_units[0]
    grid_str = f'{geographic_units}{grid_version}'

    filename = f'MP2029_{sterm}_{gterm}_C000_U00_V00_SLA_O_{year}_V_vegsm.csv'
    centers = 'MP2029_S00_G700_C000_U00_V00_SLA_I_00_00_V_grid_XYAreaComp.csv'

    filepath = f'{base_icm}/{filename}'
    centers_filepath = f'{base_icm}/{centers}'

    centers_df = pd.read_csv(centers_filepath)
    centers_df.columns = centers_df.columns.str.lower()
    centers_df = centers_df.rename(columns={centers_df.columns[0]: "cellid"}) #rename first col for later
    
    sterm_str = sterm[1:]
    gterm_str = gterm[1:]

    kwargs = kwargs_function(variable=var,
                            time_unit=var_time_unit,
                            grid=grid_str,
                            model=model,
                            scenario_id=sterm_str,
                            model_group_id=gterm_str,
                            calendar_year=year)

    df = cast_columns(pl.DataFrame(kwargs))

    if validate:
        validate_data_frame(df)

    # create the path for the COG.
    df = df.with_columns(cog_path=cog_path_expression(df, base_path=BASE_PATH))
    cog_path = Path(df.select("cog_path").item())

    output_df = pd.read_csv(f'{filepath}')
    output_df.columns = output_df.columns.str.lower()
    output_df = output_df.rename(columns={output_df.columns[0]: "cellid"})

    spec_coords = centers_df.merge(output_df, on="cellid")

    x = spec_coords["X_UTM15N_meters".lower()].values
    y = spec_coords["Y_UTM15N_meters".lower()].values
    species_values = spec_coords['WeigtedFFIBS'.lower()].values
    
    # raster grid info
    grid = GRIDS[kwargs["grid"]]
    dst_transform = from_bounds(*grid.bounds, width=grid.width, height=grid.height)
    
    #create empty raster
    raster = np.full((grid.height, grid.width),-9999,dtype=np.float32)

    #populate with data
    for easting, northing, value in zip(x, y, species_values):
        row, col = rowcol(dst_transform, easting, northing)
        raster[row, col] = value
    
    compression="zstd"
    compression_level=6

    dst_profile = {
        "compress": compression.upper(),
        "compression_level": compression_level,
        "count": 1,
        "crs": grid.crs,
        "driver": "COG",
        "dtype": np.float32, #data.dtype,
        "height": grid.height,
        "nodata": -9999,
        "resampling": "NEAREST",
        "transform": dst_transform,
        "width": grid.width
    }

    cog_path.parent.mkdir(parents=True, exist_ok=True)

    #write data to view in mpdp
    with rio.open(cog_path, "w", **dst_profile) as dst:
        dst.update_tags(**kwargs)
        dst.write(raster, 1)

    os.chmod(cog_path,0o667) #change permissions -rw-rw-rwx

    print(f"Complete processing for {var}")

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

    postprocess_ffibs_scr(
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
    #run main
    main() 