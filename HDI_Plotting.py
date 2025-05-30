def Solo_Plotting(base_out_path, outprefix, g, Shannons, Richness, Landscape, regions, region_names, region_type_name, variable_set_name):
    
    outpdf = f'{base_out_path}/{outprefix}_HDI.pdf'
    with PdfPages(outpdf) as pdf:
        plot_count = 1
        plt.figure(figsize=(11,8.5))
        for region in regions:
            if region != -9999:
                ax1 =plt.subplot(3,1,plot_count)
                plot_count += 1
                ax1.plot(Shannons[region].keys(), Shannons[region].values(), label=f'G{g:03d}', color='blue')      
                ax1.set_xlabel('Year')
                ax1.set_title(f'{region_type_name}: {region_names[region]} - {variable_set_name}',pad=10)
                ax1.set_ylabel(f'Habitat Diversity Index')
                ax1.set_ylim(0,2)
                ax1.legend(title='Group',loc='center left', bbox_to_anchor=(1, 0.5))
                ax1.grid(True)
                plt.xticks(range(start_year, end_year + 1, 5))
                if plot_count == 4:
                    plt.tight_layout(rect=[0, 0, 1, 1])
                    pdf.savefig()
                    plt.close()
                    plt.figure(figsize=(11,8.5))
                    plot_count=1
        if plot_count != 1:  # If there are remaining subplots (plot_count didn't reset to 1)
            plt.tight_layout(rect=[0, 0, 1, 1])
            pdf.savefig()
            plt.close()

    outpdf = f'{base_out_path}/{outprefix}_Richness.pdf'
    with PdfPages(outpdf) as pdf:
        plot_count = 1
        plt.figure(figsize=(11,8.5))
        for region in regions:
            if region != -9999:
                ax1 =plt.subplot(3,1,plot_count)
                plot_count += 1
                ax1.plot(Richness[region].keys(), Richness[region].values(), label=f'G{g:03d}', color='blue')      
                ax1.set_xlabel('Year')
                ax1.set_title(f'{region_type_name}: {region_names[region]} - {variable_set_name}',pad=10)
                ax1.set_ylabel(f'Habitat Richness')
                ax1.set_ylim(0,10)
                ax1.legend(title='Group',loc='center left', bbox_to_anchor=(1, 0.5))
                ax1.grid(True)
                plt.xticks(range(start_year, end_year + 1, 5))
                if plot_count == 4:
                    plt.tight_layout(rect=[0, 0, 1, 1])
                    pdf.savefig()
                    plt.close()
                    plt.figure(figsize=(11,8.5))
                    plot_count=1
        if plot_count != 1:  # If there are remaining subplots (plot_count didn't reset to 1)
            plt.tight_layout(rect=[0, 0, 1, 1])
            pdf.savefig()
            plt.close()


    plot_path = f'{base_out_path}/{outprefix}_Combined_HDI.png'
    plt.figure(figsize=(8.5,11))
    # Generate a colormap for regions
    i = 0
    for region in regions:
        if region != -9999:
            years = list(Shannons[region].keys())
            values = list(Shannons[region].values())
            i +=1
            # Plot the line with the assigned color
            plt.plot(years, values, label=f'{region_names[region]}')

            # Annotate the first point with the same color
            plt.text(years[0], values[0], region_names[region], fontsize=8,
                    verticalalignment='bottom', horizontalalignment='right')
    plt.xlabel('Year')
    plt.ylabel('Habitat Diversity Index')
    plt.xticks(range(start_year, end_year + 1, 5))
    plt.title(f'G{g:03d} - Habitat Diversity Index - All Regions', pad=10)
    plt.legend(title=region_type_name, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    outpdf = f'{base_out_path}/{outprefix}_Landscape.pdf'
    with PdfPages(outpdf) as pdf:
        for region in regions:
            if region != -9999:
                fig,ax = plt.subplots(figsize=(11,8.5))
                years = sorted(list(Landscape[region].keys()))
                bottoms = np.zeros(len(years))
                # For each variable (e.g., 'Fresh', 'Brackish'...), collect year-wise values
                for var in Landscape[region][years[0]].keys():
                    values = [Landscape[region][year].get(var, 0) for year in years]
                    ax.bar(years, values, bottom=bottoms, label=var, color=colors_by_var[var])
                    bottoms += values
                ax2 = ax.twinx()
                ax2.plot(list(Shannons[region].keys()), list(Shannons[region].values()), color = 'black', label = "Habitat Diversity Index",linewidth=2)
                ax.set_xlabel("Years")
                ax.set_ylabel("Percent Region Coverage")
                ax2.set_ylabel("Habitat Diversity Index")  # Secondary Y-axis label
                ax.set_title(f"{region_names[region]}")
                ax2.set_ylim(0,2)
                ax.set_ylim(0,1)
                ax.legend(
                        title='Landscape Type', 
                        loc='upper center', 
                        bbox_to_anchor=(0.5, -0.1),  # Moves legend below the plot
                        ncol=max(4, len(Landscape[region]) // 4),  # Adjust number of columns dynamically
                        frameon=True  # Optional: Removes legend border for cleaner look
                    )        
                ax.set_xticks(range(start_year, end_year + 1, 5))
                plt.tight_layout()
                pdf.savefig(fig, dpi=300, bbox_inches='tight')
                plt.close(fig)

def Compare_Plotting(base_out_path, outprefix, g_fwa, g_fwoa, Shannons, Richness, regions, region_names, region_type_name, variable_set_name):        
    outpdf = f'{base_out_path}/{outprefix}_HDI.pdf'
    with PdfPages(outpdf) as pdf:
        plot_count = 1
        plt.figure(figsize=(11,8.5))
        for region in regions:
            if region != -9999:
                ax1 = plt.subplot(3, 1, min(plot_count, 3))  
                plot_count +=1
                ax1.plot(Shannons[g_fwoa][region].keys(),Shannons[g_fwoa][region].values(), label=f'G{g_fwoa:03d} - FWOA', color = 'black', linestyle='--')      
                ax1.plot(Shannons[g_fwa][region].keys(),Shannons[g_fwa][region].values(), label=f'G{g_fwa:03d} - FWA', color = 'red')      
                ax1.set_xlabel('Year')
                ax1.set_title(f'{region_type_name}: {region_names[region]} - {variable_set_name}',pad=10)
                ax1.set_ylabel(f'Habitat Diversity Index')
                ax1.set_ylim(0,2)
                ax1.legend(title='Group',loc='center left', bbox_to_anchor=(1, 0.5))
                ax1.grid(True)
                ax1.set_xticks(range(start_year, end_year + 1, 5))
                if plot_count == 4:
                    plt.tight_layout(rect=[0, 0, 1, 1])
                    pdf.savefig()
                    plt.close()
                    plt.figure(figsize=(11,8.5))
                    plot_count=1
        if plot_count != 1:  # If there are remaining subplots (plot_count didn't reset to 1)
            plt.tight_layout(rect=[0, 0, 1, 1])
            pdf.savefig()
            plt.close()
    
    outpdf = f'{base_out_path}/{outprefix}_Richness.pdf'
    with PdfPages(outpdf) as pdf:
            plot_count = 1
            plt.figure(figsize=(11,8.5))
            for region in regions:
                if region != -9999:
                    ax1 =plt.subplot(3,1,plot_count)
                    plot_count += 1
                    ax1.plot(Richness[g_fwoa][region].keys(),Richness[g_fwoa][region].values(), label=f'G{g_fwoa:03d} - FWOA', color = 'black', linestyle='--')      
                    ax1.plot(Richness[g_fwa][region].keys(),Richness[g_fwa][region].values(), label=f'G{g_fwa:03d} - FWA', color = 'red')      
                    ax1.set_xlabel('Year')
                    ax1.set_title(f'{region_type_name}: {region_names[region]} - {variable_set_name}',pad=10)
                    ax1.set_ylabel(f'Habitat Richness')
                    ax1.set_ylim(0,10)
                    ax1.legend(title='Group',loc='center left', bbox_to_anchor=(1, 0.5))
                    ax1.grid(True)
                    plt.xticks(range(start_year, end_year + 1, 5))
                    if plot_count == 4:
                        plt.tight_layout(rect=[0, 0, 1, 1])
                        pdf.savefig()
                        plt.close()
                        plt.figure(figsize=(11,8.5))
                        plot_count=1
            if plot_count != 1:  # If there are remaining subplots (plot_count didn't reset to 1)
                plt.tight_layout(rect=[0, 0, 1, 1])
                pdf.savefig()
                plt.close()

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

def dict2asc_flt(mapping_dict,outfile,asc_grid,asc_header,write_mode):
        # this function maps a dictionary of floating point data into XY space and saves as a raster file of ASCII grid format
        # this function does not return anything but it will save 'outfile' to disk

        # ASCII grid format description: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm

        # 'mapping_dict' is a dictionary with grid cell ID as the key and some value for each key
        # 'outfile' is the filename (full path) of the output .asc raster text file to be saved
        # 'asc_grid' is a numpy array that is the grid structure of an ASCII text raster
        # 'asc_header' is a string that includes the 6 lines of text required by the ASCII grid format
        msg = '\ndid not save %s' % (outfile)
        with open(outfile, mode=write_mode) as outf:
            outf.write(asc_header)
            for row in asc_grid:
                nc = 0
                for col in row:
                    gid_map = row[nc]
                    if gid_map > 0:                     # if the ASC grid has a no data cell (-9999) there will be no dictionary key, the else criterion is met and it keeps the no data value (-9999)
                        gid_val = float(mapping_dict[gid_map] )
                    else:
                        gid_val = float(gid_map)
                    if nc == 0:
                        rowout = '%0.4f'  % gid_val
                    else:
                        rowout = '%s %0.4f' % (rowout,gid_val)
                    nc += 1
                outf.write('%s\n' % rowout)
                msg = '\nsuccessfully saved %s' % (outfile)
        return msg

def read_single_var_files(base_out_path,inprefix,ey,region_type_name, Var):
    in_path = f'{base_out_path}/{inprefix}_{region_type_name}_{ey}_{Var}.csv'
    in_raw = pd.read_csv(in_path)
    in_raw.set_index('Region', inplace=True)
    outdict = {}
    for region, row in in_raw.iterrows():
        outdict[region] = {}
        for variable_index, result in row.items():
            variable_index = int(variable_index)
            outdict[region][variable_index] = result 
    return outdict

def read_landscape_data(region_index, region_type_name, base_out_path, inprefix, ey):
    filepath = os.path.join(base_out_path, f"{inprefix}_{region_type_name}_{ey}_Landscape.csv")
    df = pd.read_csv(filepath)
    df.set_index('Region', inplace=True)

    output_dict = {region_index: {}}

    for region, row in df.iterrows():
        for col_name, value in row.items():
            if pd.isna(value):
                continue
            try:
                variable_index_str, land_type = col_name.split("_", 1)
                variable_index = int(variable_index_str)
            except ValueError:
                print(f"Skipping malformed column: {col_name}")
                continue

            output_dict[region_index].setdefault(variable_index, {})
            output_dict[region_index][variable_index].setdefault(region, {})
            output_dict[region_index][variable_index][region][land_type] = value
    return output_dict


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import zipfile


s = int(sys.argv[1]) #in put scenerio number
g_fwa = int(sys.argv[2]) #input group number
g_fwoa = int(sys.argv[3]) #input Future without Action group number
project = sys.argv[4] #input project (ie. MP2023, MP2029, UBDP)

region_types = [0,1,2,3] #Ecoregion, Compartment, Coastwide, Basin

region_type_names = {0: 'Ecoregion',
                    1: 'Compartment',
                    2: 'Coastwide',
                    3: 'Basin'}

variables = [0,1]

variable_names = {0: 'SetA', 1: 'SetB'}

variables_by_index = {0: ['Bareground', 'Water', 'Fresh', 'Intermediate', 'Brackish', 'Saline', 'Bottomland', 'Swamp'], #Basic Variables
                    1: ['Bareground', 'Deep Water', 'Not Deep', 'Fresh', 'Intermediate', 'Brackish', 'Saline', 'Bottomland', 'Swamp']} #Deep vs Not Deep Water


colors_by_var = {'Bareground': 'saddlebrown',
                'Water': 'cornflowerblue',
                'Fresh': 'limegreen',
                'Intermediate': 'gold',
                'Brackish': 'orange',
                'Saline': 'red',
                'Swamp': 'darkgreen',
                'Bottomland': 'bisque',
                'Shallow Water': 'lightblue',
                'Shallow Deep Water': 'dodgerblue',
                'Deep Water': 'blue',
                'Not Deep': 'dodgerblue',}

run_folder = f'/ocean/projects/bcs200002p/ewhite12/{project}/ICM/S{s:02d}/G{g_fwa:03d}' 

if project == 'MP2023': #Does not create a new folder in MP2023 runs
    base_out_path = f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Outputs/S{s:02d}/G{g_fwa:03d}'  # Update
else: #does create a new folder in MP2029 or UBDP runs
    base_out_path = f'{run_folder}/HDI'  #

os.makedirs(base_out_path, exist_ok=True)

inputs = np.genfromtxt(f'{run_folder}/ICM_control.csv',dtype=str,comments='#',delimiter=',')

mpterm = inputs[47,1].lstrip().rstrip()
cterm = inputs[50,1].lstrip().rstrip()
uterm = inputs[51,1].lstrip().rstrip()
vterm = inputs[52,1].lstrip().rstrip()
rterm = inputs[53,1].lstrip().rstrip()
runprefix = '%s_S0%s_G%s_%s_%s_%s_%s' % (mpterm,s,g_fwa,cterm,uterm,vterm,rterm)
outprefix = '%s_S0%s_G%s_%s_%s_%s' % (mpterm,s,g_fwa,cterm,uterm,vterm)

global start_year, end_year

start_year = int(inputs[29,1].lstrip().rstrip())
end_year = int(inputs[30,1].lstrip().rstrip())


veg_comp_import = read_file_zip(f'{run_folder}/hydro/grid_lookup_500m.csv')
comp_eco_import = read_file_zip(f'{run_folder}/geomorph/input/compartment_ecoregion.csv')
veg_basin_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Veg_to_basin.csv')
veg_erdirect_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Veg_to_ER_direct.csv')
deep_water_import = read_file_zip(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/LAVegGrid_Deepwater.csv')


#Creates Dictionaries of veg cells directly to each comparison region
veg_to_comp_init = veg_comp_import[['Grid','Compartment']].to_dict()
basin_to_basinname_init = veg_basin_import[['BasinID','BasinName']].to_dict()
er_to_ername_direct_init = veg_erdirect_import[['er_n', 'ecoregion']].to_dict()

deep_water_init = deep_water_import[['gridcode','Deep Water']].to_dict()


er_to_ername = {er: ername for er, ername in zip(er_to_ername_direct_init['er_n'].values(), er_to_ername_direct_init['ecoregion'].values())}
basin_to_basinname = {basin: basinname for basin, basinname in zip(basin_to_basinname_init['BasinID'].values(), basin_to_basinname_init['BasinName'].values())}
deep_water = {veg: deep for veg, deep in zip(deep_water_init['gridcode'].values(), deep_water_init['Deep Water'].values())}

ecoregions = list(set(er_to_ername.keys()))
compartments = list(set(veg_to_comp_init['Compartment'].values()))
comp_to_compname = {comp: f"Compartment {comp}" for comp in compartments}
basins = list(set(basin_to_basinname.keys()))


region_information = {0: {'region': ecoregions, 'name': 'Ecoregions', 'names': er_to_ername},
            1: {'region': compartments, 'name': 'Compartments', 'names': comp_to_compname},
            2: {'region': [1],'name': 'Coastwide', 'names': {1: "Coastwide"}},
            3: {'region': basins,'name': 'Basin', 'names': basin_to_basinname}}


Shannons = {}
Richness = {}
Landscape = {}
for region_index in region_types:
    Shannons[region_index] = {}
    Richness[region_index] = {}
    Landscape[region_index] = {}

    regions = region_information[region_index]['region']
    for variable_index in variables:
        Shannons[region_index][variable_index] = {}
        Richness[region_index][variable_index] = {}
        Landscape[region_index][variable_index] = {}

        for g in [g_fwa, g_fwoa]:
            Shannons[region_index][variable_index][g] = {}
            Richness[region_index][variable_index][g] = {}
            Landscape[region_index][variable_index][g] = {}
            for region in regions:
                Shannons[region_index][variable_index][g][region] = {}
                Richness[region_index][variable_index][g][region] = {}
                Landscape[region_index][variable_index][g][region] = {}


                    
for g in g_fwoa,g_fwa:
    
    inprefix = '%s_S0%s_G%s_%s_%s_%s' % (mpterm,s,g,cterm,uterm,vterm)
    run_folder = f'/ocean/projects/bcs200002p/ewhite12/{project}/ICM/S{s:02d}/G{g:03d}' 
    
    if project == 'MP2023': #Does not create a new folder in MP2023 runs
        base_out_path = f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/Shannon_diversity/Outputs/S{s:02d}/G{g:03d}'  # Update
    else: #does create a new folder in MP2029 or UBDP runs
        base_out_path = f'{run_folder}/HDI'  #

    for region_index in region_types:
        regions = region_information[region_index]['region']
        region_type_name = region_information[region_index]['name']
        region_names = region_information[region_index]['names']
        
        for year in range(start_year, end_year + 1):
            ey = year - start_year + 1
            
            raw_shannons = read_single_var_files(base_out_path,inprefix,ey,region_type_name, 'Shannons')
            raw_richness = read_single_var_files(base_out_path,inprefix,ey,region_type_name, 'Richness')
            raw_landscape = read_landscape_data(region_index, region_type_name, base_out_path, inprefix, ey)
            
            for region in regions:
                for variable_index in variables:
                    Shannons[region_index][variable_index][g][region][year] = raw_shannons[region][variable_index]
                    Richness[region_index][variable_index][g][region][year] = raw_richness[region][variable_index]
                    Landscape[region_index][variable_index][g][region][year] = raw_landscape[region_index][variable_index][region]

        for variable_index in variables:

            variable_set_name = variable_names[variable_index]
            
            outprefix = f'{inprefix}_{region_type_name}_{variable_set_name}_01_52'
            
            Solo_Plotting(base_out_path, outprefix, g, Shannons[region_index][variable_index][g], 
                            Richness[region_index][variable_index][g], Landscape[region_index][variable_index][g],
                        regions, region_names, region_type_name, variable_set_name)

            if g == g_fwa:
                outprefix = f'{inprefix}_{region_type_name}_{variable_set_name}_52_52'
                Compare_Plotting(base_out_path, outprefix, g_fwa, g_fwoa, Shannons[region_index][variable_index],
                                Richness[region_index][variable_index],
                                regions, region_names, region_type_name, variable_set_name)

