import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

s = 7
runs = [520,220,223]

var_definition_lookup = {
  'pL_BM': '% Coverage of Brackish Marsh',
  'BM_HSI': 'Brackish Marsh - Habitiat Suitability Index',
  'BM_SI1': 'Brackish Marsh - Emergent Vegetation',
  'BM_SI2': 'Brackish Marsh - % Submerged Aquatic Vegetation',
  'BM_SI3': 'Brackish Marsh - Marsh Edge and Interspersion',
  'BM_SI4': 'Brackish Marsh - % Shallow Open Water',
  'BM_SI5': 'Brackish Marsh - Mean Annual Salinity',
  'BM_SI6': 'Brackish Marsh - Aquatic Organism Access',
  'BM_HSI_W': 'Brackish Marsh - Open Water HSI',
  'pL_SM': '% Coverage of Saline Marsh',
  'SM_HSI': 'Saline Marsh Habitiat Suitability Index',
  'SM_SI1': 'Saline Marsh - Emergent Vegetation',
  'SM_SI2': 'Saline Marsh - % Submerged Aquatic Vegetation',
  'SM_SI3': 'Saline Marsh - Marsh Edge and Interspersion',
  'SM_SI4': 'Saline Marsh - % Shallow Open Water',
  'SM_SI5': 'Saline Marsh - Mean Annual Salinity',
  'SM_SI6': 'Saline Marsh - Aquatic Organism Access',
  'SM_HSI_W': 'Saline Marsh - Open Water HSI',
  'pL_FM': '% Coverage of Fresh Marsh',
  'FM_HSI': 'Fresh Marsh Habitiat Suitability Index',
  'FM_SI1': 'Fresh Marsh - Emergent Vegetation',
  'FM_SI2': 'Fresh Marsh - % Submerged Aquatic Vegetation',
  'FM_SI3': 'Fresh Marsh - Marsh Edge and Interspersion',
  'FM_SI4': 'Fresh Marsh - % Shallow Open Water',
  'FM_SI5': 'Fresh Marsh - Mean High Salinity',
  'FM_SI6': 'Fresh Marsh - Aquatic Organism Access',
  'FM_HSI_W': 'Fresh Marsh - Open Water HSI',
  'pL_SF': '% Coverage of Swamp Forest', 
  'SF_HSI': 'Swamp Forest - Habitiat Suitability Index',
  'SF_SI1': 'Swamp Forest - Stand Structure',
  'SF_SI2': 'Swamp Forest - Stand Maturity',
  'SF_SI3': 'Swamp Forest - Water Regime',
  'SF_SI4': 'Swamp Forest - Mean High Salinity',
  'pL_IM': '% Coverage of Intermediate Marsh',
  'IM_HSI': 'Intermediate Marsh Habitiat Suitability Index',
  'IM_SI1': 'Intermediate Marsh - Emergent Vegetation',
  'IM_SI2': 'Intermediate Marsh - % Submerged Aquatic Vegetation',
  'IM_SI3': 'Intermediate Marsh - Marsh Edge and Interspersion',
  'IM_SI4': 'Intermediate Marsh - % Shallow Open Water',
  'IM_SI5': 'Intermediate Marsh - Mean High Salinity',
  'IM_SI6': 'Intermediate Marsh - Aquatic Organism Access',
  'IM_HSI_W': 'Intermediate Marsh - Open Water HSI',
  'pL_BF': '% Coverage of Bottomland Hardwood Forest',
  'BF_HSI': 'Bottomland Hardwood - Habitiat Suitability Index',
  'BF_SI1': 'Bottoland Hardwood - Tree Species Association',
  'BF_SI2': 'Bottoland Hardwood - Stand Maturity',
  'BF_SI3': 'Bottoland Hardwood - Understory / Midstory',
  'BF_SI4': 'Bottoland Hardwood - Hydrology',
  'BF_SI5': 'Bottoland Hardwood - Contiguous Forested Area',
  'BF_SI6': 'Bottoland Hardwood - Suitability and Traversability of Surrounding Land Use',
  'BF_SI7': 'Bottoland Hardwood - Disturbance',
}

#Set run prefexis and get some basic info

run = runs[0]

run_folder = f'/ocean/projects/bcs200002p/ewhite12/UBDP/ICM/S07/G{run:03d}'
#ICM Location
inputs = np.genfromtxt(f'{run_folder}/ICM_control.csv',dtype=str,comments='#',delimiter=',')

mpterm = inputs[47,1].lstrip().rstrip()
cterm = inputs[50,1].lstrip().rstrip()
uterm = inputs[51,1].lstrip().rstrip()
vterm = inputs[52,1].lstrip().rstrip()
rterm = inputs[53,1].lstrip().rstrip()
runprefix = '%s_S0%s_G%s_%s_%s_%s_%s' % (mpterm,s,run,cterm,uterm,vterm,rterm)

start_year = int(inputs[29,1].lstrip().rstrip())
end_year = int(inputs[30,1].lstrip().rstrip())

veg_cell_area_meters = 480*480 #Meters
veg_cell_area = veg_cell_area_meters/4046.856422 #ACRES

years = range(start_year+1, end_year+1)

#ICM Locations
veg_comp_import = pd.read_csv(f'{run_folder}/hydro/grid_lookup_500m.csv')
comp_eco_import = pd.read_csv(f'{run_folder}/geomorph/input/compartment_ecoregion.csv')


#Creates Dictionaries of veg cells directly to each comparison region
veg_to_comp_init = veg_comp_import[['Grid','Compartment']].to_dict()
comp_to_er_init = comp_eco_import[['ICM-Hydro_comp', 'er_n']].to_dict()
er_to_ername_init = comp_eco_import[['er_n','er']].to_dict()

veg_to_comp = {veg: comp for veg, comp in zip(veg_to_comp_init['Grid'].values(), veg_to_comp_init['Compartment'].values())}
comp_to_er = {comp: er for comp, er in zip(comp_to_er_init['ICM-Hydro_comp'].values(), comp_to_er_init['er_n'].values())}
veg_to_er = {veg_cell: comp_to_er.get(comp, -1) for veg_cell, comp in veg_to_comp.items()}
er_to_ername = {er: ername for er, ername in zip(er_to_ername_init['er_n'].values(), er_to_ername_init['er'].values())}

ecoregions = list(set(veg_to_er.values()))

data_in = {}
data_out = {}
i = 0

hu = {}
#Reads the Scaled output to create necessary data for line and diff plots

for run in runs:
    hu[run] = {}

    run_folder = f'/ocean/projects/bcs200002p/ewhite12/UBDP/ICM/S07/G{run:03d}'
    #ICM Location
    inputs = np.genfromtxt(f'{run_folder}/ICM_control.csv',dtype=str,comments='#',delimiter=',')
    mpterm = inputs[47,1].lstrip().rstrip()
    cterm = inputs[50,1].lstrip().rstrip()
    uterm = inputs[51,1].lstrip().rstrip()
    vterm = inputs[52,1].lstrip().rstrip()
    rterm = inputs[53,1].lstrip().rstrip()
    runprefix = '%s_S0%s_G%s_%s_%s_%s_%s' % (mpterm,s,run,cterm,uterm,vterm,rterm)

    for year in years:
        ey = year - start_year+1
        # ICM Locationn
        importhus = f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/WVA/Outputs/G{run}/{runprefix}_O_{ey:02d}_{ey:02d}_X_HUS.csv'

        hudata = pd.read_csv(importhus)
        #waterdata = pd.read_csv(importwater)

        if ey ==2:
            models =list(set(hudata.columns))
            models.remove('GridID')
            for ecoregion in ecoregions:
                hu[run][ecoregion] = {}
                hu[run][ecoregion]['Total'] = {}
                for model in models:
                    hu[run][ecoregion][model] = {}

        
        for ecoregion in ecoregions:
            hu[run][ecoregion]['Total'][year] = 0
            ind_in_er = [key -1 for key, value in veg_to_er.items() if value == ecoregion]
            filteredhus = hudata.loc[ind_in_er]
            for model in models:
                hu[run][ecoregion][model][year] = sum(filteredhus[f'{model}'])
                hu[run][ecoregion]['Total'][year] += sum(filteredhus[f'{model}'])

models.append('Total')

colors_by_var = {'FM': 'limegreen',
                'IM': 'gold',
                'BM': 'orange',
                'SM': 'red',
                'SF': 'darkgreen',
                'BF': 'bisque',
                'Total': 'black'}

out_folder=f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/WVA/Outputs/HU'
os.makedirs(out_folder, exist_ok=True)  # Create the folder if it doesn't exist

out_pdf = f'{out_folder}/{"_".join(str(run) for run in runs)}_WVA_HUs_Compare.pdf'
with PdfPages(out_pdf) as pdf:
    for ecoregion in ecoregions: 
        plt.figure(figsize=(11,2.85))
        for run in runs:
            data = hu[run][ecoregion]['Total']
            if run == 520:
                plt.plot(data.keys(),data.values(), label = f'G{run}', color='black',linestyle = '--',linewidth=2)
            else:
                plt.plot(data.keys(),data.values(), label = f'G{run}')
        plt.legend(title='Group',loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlabel('Year')
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        plt.title(f'{er_to_ername[ecoregion]} Ecoregion - HUs', pad=10)
        plt.ylabel('Habitat Units')
        plt.ylim(0, 1.1*max([max(hu[run][ecoregion]['Total'].values()) for run in runs]))
        plt.grid(True)                    
        plt.tight_layout(rect=[0, 0, 1, 1])
        pdf.savefig()
        plt.close()

