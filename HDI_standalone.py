def Calc_Shannons(variables_to_use, type_dict, regions, veg_to_region): #Function to calculate the Shannon's index and richness for a given region

    types_by_cell = {}

    types_by_cell = {var: inner_dict for var, inner_dict in type_dict.items() if var in variables_to_use}


    region_types_by_area = {}
    region_types_by_pct = {}
    richness_by_region = {}
    shannons_index_by_region  = {}

    for region in regions:
        region_types_by_area[region] = {}
        region_types_by_pct[region] = {}
        cells_in_er = [key for key, value in veg_to_region.items() if value == region] 

        for var in variables_to_use:
            region_types_by_area[region][var] = 0

        for cell in cells_in_er:
            for var in variables_to_use:
                region_types_by_area[region][var] += types_by_cell[var][cell]
        
        modeled_region_area = sum(region_types_by_area[region].values())
    
        for var in variables_to_use:
            region_types_by_pct[region][var] = (region_types_by_area[region][var]/modeled_region_area) 


        richness_by_region[region] = len([key for key, value in region_types_by_area[region].items() if value >0])

        shannons_index_by_region[region] = 0

        for var in variables_to_use:
            
            if region_types_by_pct[region][var] > 0:
                
                PilnPi = region_types_by_pct[region][var]*np.log(region_types_by_pct[region][var])

                shannons_index_by_region[region] += abs(PilnPi)
    
    return shannons_index_by_region, richness_by_region, region_types_by_pct

def read_file_zip(file_path): #function to read csv files that are potentially zipped using pandas
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            file_zipped = f'{file_path}.zip'
            file_name = os.path.basename(file_path)
            extract_path = os.path.dirname(file_path)
            with zipfile.ZipFile(file_zipped, 'r') as zip_ref:
                zip_ref.extract(file_name, path=extract_path)
            imported = pd.read_csv(file_path)
            os.remove(file_path)
            return imported

def read_annual_run_data(project, s, g, runprefix, ey): #Reads all the annual run data from various ICM outputs
    
    try:
        veg_output_file = f'/ocean/projects/bcs200002p/ewhite12/{project}/ICM/S{s:02d}/G{g:03d}/veg/{runprefix}_O_{ey:02d}_{ey:02d}_V_vegty.asc+'
        #Reads how many line the ascii raster is at the start of the veg file
        if os.path.exists(veg_output_file):
            with open(veg_output_file, 'r') as file:
                rows_str = file.readline()
                num_rows_skip = int(rows_str.split()[1]) + 6
            veg_data = pd.read_csv(veg_output_file, skiprows=num_rows_skip, sep=',')
        else:
            file_zipped = f'{veg_output_file}.zip'
            file_name = os.path.basename(veg_output_file)
            extract_path = os.path.dirname(veg_output_file)
            with zipfile.ZipFile(file_zipped, 'r') as zip_ref:
                zip_ref.extract(file_name, path=extract_path)
            with open(veg_output_file, 'r') as file:
                rows_str = file.readline()
                num_rows_skip = int(rows_str.split()[1]) + 6
            veg_data = pd.read_csv(veg_output_file, skiprows=num_rows_skip, sep=',')
            os.remove(veg_output_file)

        #Import Veg data
        cell_dict = veg_data.set_index("CELLID").to_dict(orient="index")
    except:
        print("Error reading ICM-LAVegMod Output file")
        return None

    try:
        #Imnport Deep Water Data
        LTreclass_file = f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Deep_Water_Reclass/MP2023_LTreclass_G{g:03d}_{ey:02d}.csv'
        
        #Local Test
        LT_wdeep = read_file_zip(LTreclass_file)
        LT_deep_dict = LT_wdeep.set_index("GRIDCODE").to_dict(orient="index")
    except:
        print("Deep Water Reclass file not found")

    
    cells = list(cell_dict.keys())

    all_vars = ['Bareground','NotMod', 'Water', 'Fresh','Intermediate','Brackish','Saline','Bottomland','Swamp','Shallow Water','Deep Water','Shallow Deep Water','Not Deep']

    out_dict = {}
    for var in all_vars:
        out_dict[var] = {}


    for cell in cells:
        Vegland = max(0, (1-(cell_dict[cell][' BAREGRND_OLD'] + cell_dict[cell][' BAREGRND_NEW']+cell_dict[cell][' NOTMOD']+cell_dict[cell][' WATER'])))
        type_cells = {'Bareground': (cell_dict[cell][' BAREGRND_OLD'] + cell_dict[cell][' BAREGRND_NEW']),
                            'NotMod': cell_dict[cell][' NOTMOD'],
                            'Water': cell_dict[cell][' WATER'],
                            'Fresh':cell_dict[cell][' pL_FM']*Vegland,
                            'Intermediate': cell_dict[cell][' pL_IM']*Vegland,
                            'Brackish': cell_dict[cell][' pL_BM']*Vegland,
                            'Saline': cell_dict[cell][' pL_SM']*Vegland,
                            'Bottomland': cell_dict[cell][' pL_BF']*Vegland,
                            'Swamp':cell_dict[cell][' pL_SF']*Vegland,
                            'Shallow Water': LT_deep_dict[cell]['VALUE_6'],
                            'Deep Water': LT_deep_dict[cell]['VALUE_2'],
                            'Shallow Deep Water': LT_deep_dict[cell]['VALUE_7'],
                            'Not Deep': (LT_deep_dict[cell]['VALUE_6']+LT_deep_dict[cell]['VALUE_7'])}
    
        for veg_type in all_vars:
            out_dict[veg_type][cell] = type_cells[veg_type]

    return  out_dict

def save_varaible_output(Outdict, ey, region_information, base_out_path, outprefix, Var): #Saves the Shannons and Richness outputs to csv files
    for region_index, variables in Outdict.items():


        regions = region_information[region_index]['region']
        region_type_name = region_information[region_index]['name']

        out_path = f'{base_out_path}/{outprefix}_{region_type_name}_{ey}_{Var}.csv'
    
        data = {}
        
        for region in regions:
            data[region] = {}

        for variable_index, region_results in variables.items():
            for region, result in region_results.items():
                data[region][variable_index] = result
        
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'Region'
        df.reset_index(inplace=True)
        df.to_csv(out_path, index=False)

def save_landscape_output(output_dict, region_information, base_out_path, outprefix, ey): #Saves the Landscape outputs to csv files
    for region_index, variables in output_dict.items():
        regions = region_information[region_index]['region']
        region_type_name = region_information[region_index]['name']

        data = {}

        # Initialize all regions
        for region in regions:
            data[region] = {}

        # Fill each variable's results
        for variable_index, region_results in variables.items():
            for region, landscape_dict in region_results.items():
                if isinstance(landscape_dict, dict):
                    for land_type, area in landscape_dict.items():
                        col_name = f"{variable_index}_{land_type}"  # Customize if you want
                        data[region][col_name] = area
                else:
                    print(f"Warning: expected dict for landscape, got {type(landscape_dict)}")

        # Create DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'Region'
        df.reset_index(inplace=True)

        # Save
        metric_path = os.path.join(base_out_path, f"{outprefix}_{region_type_name}_{ey}_Landscape.csv")
        df.to_csv(metric_path, index=False)
        print(f"Saved Landscape to {metric_path}")


import pandas as pd
import numpy as np
import os
import zipfile
import sys

s = int(sys.argv[1]) #in put scenerio number
g = int(sys.argv[2]) #input group number
project = sys.argv[3] #input project (ie. MP2023, MP2029, UBDP)
year = int(sys.argv[4]) #input year for this calculation. Note this is the year, not the elaypsed year

region_types = [0,1,2,3] #Ecoregion, Compartment, Coastwide, Basin

region_type_names = {0: 'Ecoregion',
                    1: 'Compartment',
                    2: 'Coastwide',
                    3: 'Basin'}

variables = [0,1]

variable_names = {0: 'SetA', 1: 'SetB'}

variables_by_index = {0: ['Bareground', 'Water', 'Fresh', 'Intermediate', 'Brackish', 'Saline', 'Bottomland', 'Swamp'], #Basic Variables
                    1: ['Bareground', 'Deep Water', 'Not Deep', 'Fresh', 'Intermediate', 'Brackish', 'Saline', 'Bottomland', 'Swamp']} #Deep vs Not Deep Water

print(f'Calculationg HDI for Project {project} S{s:02d} G{g:03d} Year {year}')

run_folder = f'/ocean/projects/bcs200002p/ewhite12/{project}/ICM/S{s:02d}/G{g:03d}' 

if project == 'MP2023': #Does not create a new folder in MP2023 runs
    base_out_path = f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Outputs/S{s:02d}/G{g:03d}'  # Update
else: #does create a new folder in MP2029 or UBDP runs
    base_out_path = f'{run_folder}/HDI'  #

os.makedirs(base_out_path, exist_ok=True)

inputs = np.genfromtxt(f'{run_folder}/ICM_control.csv',dtype=str,comments='#',delimiter=',')

mpterm = inputs[47,1].lstrip().rstrip()
cterm = inputs[50,1].lstrip().rstrip()
uterm = inputs[51,1].lstrip().rstrip()
vterm = inputs[52,1].lstrip().rstrip()
rterm = inputs[53,1].lstrip().rstrip()
runprefix = '%s_S0%s_G%s_%s_%s_%s_%s' % (mpterm,s,g,cterm,uterm,vterm,rterm)
outprefix = '%s_S0%s_G%s_%s_%s_%s' % (mpterm,s,g,cterm,uterm,vterm)

start_year = int(inputs[29,1].lstrip().rstrip())
end_year = int(inputs[30,1].lstrip().rstrip())
veg_cell_area = 480*480 #Meters

    
veg_comp_import = read_file_zip(f'{run_folder}/hydro/grid_lookup_500m.csv') 
veg_basin_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Veg_to_basin.csv') #These are currently hard coded paths
veg_erdirect_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Veg_to_ER_direct.csv') #These are currently hard coded paths
deep_water_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/LAVegGrid_Deepwater.csv') #These are currently hard coded paths


#Creates Dictionaries of veg cells directly to each comparison region
veg_to_comp_init = veg_comp_import[['Grid','Compartment']].to_dict()
veg_to_basin_init =veg_basin_import[['gridID','BasinID']].to_dict()
veg_to_er_direct_init = veg_erdirect_import[['grid_code','er_n']].to_dict()
deep_water_init = deep_water_import[['gridcode','Deep Water']].to_dict()


veg_to_er = {veg: er for veg, er in zip(veg_to_er_direct_init['grid_code'].values(), veg_to_er_direct_init['er_n'].values())}
veg_to_comp = {veg: comp for veg, comp in zip(veg_to_comp_init['Grid'].values(), veg_to_comp_init['Compartment'].values())}
veg_to_basin = {veg: basin for veg, basin in zip(veg_to_basin_init['gridID'].values(), veg_to_basin_init['BasinID'].values())}
veg_to_coast = {key: 1 for key in veg_to_comp.keys()}


deep_water = {veg: deep for veg, deep in zip(deep_water_init['gridcode'].values(), deep_water_init['Deep Water'].values())}


for gridID, deep in deep_water.items(): #Defines the veg cells that are always deep water (Region clippling)
    if deep == 1:
        veg_to_basin[gridID] = -9999 
        veg_to_coast[gridID] = -9999
        veg_to_er[gridID] = -9999
        veg_to_comp[gridID] = -9999


cells = list(veg_to_comp.keys())
compartments = list(set(veg_to_comp.values()))
ecoregions = list(set(veg_to_er.values()))
basins = list(set(veg_to_basin.values()))

region_information = {0: {'region': ecoregions, 'lookup':veg_to_er, 'name': 'Ecoregions'},
            1: {'region': compartments, 'lookup':veg_to_comp, 'name': 'Compartments'},
            2: {'region': [1], 'lookup':veg_to_coast, 'name': 'Coastwide'},
            3: {'region': basins, 'lookup':veg_to_basin, 'name': 'Basin'}}


Richness_output = {}
Shannons_output = {}
Landscape_output = {}


ey = year - start_year + 1
      
type_dict = read_annual_run_data(project, s, g, runprefix, ey)

for region_index in region_types: #Loops throiugh each region type first, since data can be shared between region types

    Richness_output[region_index] = {}
    Shannons_output[region_index] = {}
    Landscape_output[region_index] = {}

    veg_to_region = region_information[region_index]['lookup']
    regions = region_information[region_index]['region']
    
            
    for variable_index in variables: #Loops through each variable set for each region type
        vars_to_use = variables_by_index[variable_index]
        
        temp_shannon,temp_richness, temp_landscape \
        = Calc_Shannons(vars_to_use, type_dict, regions, veg_to_region, year)

        Richness_output[region_index][variable_index]   = temp_richness
        Shannons_output[region_index][variable_index]   = temp_richness
        Landscape_output[region_index][variable_index]   = temp_landscape


save_varaible_output(Shannons_output, ey, region_information, base_out_path, outprefix, 'Shannons')
save_varaible_output(Richness_output, ey, region_information, base_out_path, outprefix, 'Richness')
save_landscape_output(Landscape_output, region_information, base_out_path, outprefix, ey)
