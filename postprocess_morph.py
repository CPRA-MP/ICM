#launch apptainer with cpra api:
#/ocean/projects/bcs200002p/shared/python/cpra-python3

from cpra.mp.data import write_data, read_fortran_array
from cpra.mp.data.variables import VARIABLES

import argparse
import os

script_name = os.path.basename(__file__)

#api var name: morph file name
morph_var_lookup = {
    "inun": "inun",             #| Inundation Depth | inun | icm | morph | Float32 | morph_pixel | annual | m | .2f | inun |  | 1 |
    "elev": "dem",              #| Topobathymetric Elevation | elev | icm | morph | Float32 | morph_pixel | annual | NAVD88 m | .2f | elev |  | 1 |
    "lnd_type": "lndtyp"        #| Land Type | lnd_type | icm | morph | Int32 | morph_pixel | annual |  | d | lnd_type |  | 1 |
    }
vars_to_process = ['inun', 'elev', 'lnd_type']
validate=True

def postprocess_morph(year,base_icm,model,grid_version,start_year,sterm,gterm):
    for var in vars_to_process:
        file_var = morph_var_lookup.get(var)

        print(f"Begin processing {var}")
        
        var_properties = VARIABLES[var]
        var_dtype = var_properties.dtype
        var_time_unit = var_properties.time_units[0]
        geographic_units = var_properties.geographic_units[0]
        grid_str = f'{geographic_units}{grid_version}'

        file_year = f"{year - start_year + 1:02d}"
        
        filename = f'MP2029_{sterm}_{gterm}_C000_U00_V00_SLA_N_{file_year}_{file_year}_W_{file_var}30.xyz.b'
        outpath = f'{base_icm}/{sterm}/{gterm}/geomorph/output'
        sterm_str = sterm[1:]
        gterm_str = gterm[1:]
        
        filepath = f'{outpath}/{filename}'

        data = read_fortran_array(filename=filepath, variable=var)

        #write data to view in mpdp
        write_data(data=data,
                    dtype=var_dtype,
                    variable=var,
                    time_unit=var_time_unit,
                    grid=grid_str,
                    model=model,
                    scenario_id=sterm_str,
                    model_group_id=gterm_str,
                    calendar_year=year
                    )

        print(f"Complete processing for {var}")

def main():
    #Expected values to be read in from ICM_control.csv
    # base_icm = '/ocean/projects/bcs200002p/ewhite12/MP2029/ICMv26'
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

    postprocess_morph(
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
    
    
                




