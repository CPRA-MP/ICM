#Barrier Island Tidal Inlet (BITI) Model (to be added to the ICM py code)
import numpy as np
import pandas

# FROM 2017 ICM-Py:
# create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
# EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
########### EH_comp_out is a numpy array #############

#Barrier Island Tidal Inlet (BITI) input file
#The input file only needs to be read once
#It contains the comp IDs, link IDs, depth to width ratios, partition coefficients, and basin-wide factors.
BITI_input_filename = r'[Add path here]\BITI_setup_input.xlsx'
BITI_Terrebonne_setup = pandas.read_excel(BITI_input_filename, 'Terrebonne',index_col=None)
BITI_Barataria_setup = pandas.read_excel(BITI_input_filename, 'Barataria',index_col=None)
BITI_Pontchartrain_setup = pandas.read_excel(BITI_input_filename, 'Pontchartrain',index_col=None)

#Barrier Island Tidal Inlet (BITI) compartment IDs
#These are the compartments that make up each basin
BITI_Terrebonne_comp = list( BITI_Terrebonne_setup.iloc[3::,0] )
BITI_Barataria_comp = list( BITI_Barataria_setup.iloc[3::,0] )
BITI_Pontchartrain_comp = list( BITI_Pontchartrain_setup.iloc[3::,0] )

#Barrier Island Tidal Inlet (BITI) link IDs
#These are the links that respresent the tidal inlets in each basin
BITI_Terrebonne_link = list(BITI_Terrebonne_setup.iloc[0,1:-2])
BITI_Barataria_link = list(BITI_Barataria_setup.iloc[0,1:-2])
BITI_Pontchartrain_link = list(BITI_Pontchartrain_setup.iloc[0,1:-2])

BITI_Links = [BITI_Terrebonne_link,BITI_Barataria_link,BITI_Pontchartrain_link]

#Barrier Island Tidal Inlet (BITI) partition coefficients
#Each basin has it's own array of partition coefficients with size m by n,
#where m = number of compartments in the basin and n = the number of links in the basin
BITI_Terrebonne_partition = np.asarray(BITI_Terrebonne_setup)[3::,1:-2]
BITI_Barataria_partition = np.asarray(BITI_Barataria_setup)[3::,1:-2]
BITI_Pontchartrain_partition = np.asarray(BITI_Pontchartrain_setup)[3::,1:-2]

#Barrier Island Tidal Inlet (BITI) depth to width ratio (dwr) for each link in each basin (Depth/Width)
BITI_Terrebonne_dwr = list(BITI_Terrebonne_setup.iloc[1,1:-2])
BITI_Barataria_dwr = list(BITI_Barataria_setup.iloc[1,1:-2])
BITI_Pontchartrain_dwr = list(BITI_Pontchartrain_setup.iloc[1,1:-2])

#Barrier Island Tidal Inlet (BITI) basin-wide factor (BWF) for each basin
BITI_Terrebonne_BWF = float(BITI_Terrebonne_setup.iloc[1,-1])
BITI_Barataria_BWF = float(BITI_Barataria_setup.iloc[1,-1])
BITI_Pontchartrain_BWF = float(BITI_Pontchartrain_setup.iloc[1,-1])

#Barrier Island Tidal Inlet (BITI) tidal prism values
#Get the tidal prism values for each compartment from the Hydro output
BITI_Terrebonne_prism = [EH_prisms.get(comp) for comp in BITI_Terrebonne_comp]
BITI_Barataria_prism = [EH_prisms.get(comp) for comp in BITI_Barataria_comp]
BITI_Pontchartrain_prism = [EH_prisms.get(comp) for comp in BITI_Pontchartrain_comp]

#BITI effective tidal prism and inlet area
#kappa and alpha are the Gulf of Mexico constants for unjettied systems (units = metric)
kappa = 6.99e-4
alpha = 0.86

#Calculate the effective tidal prism and cross-sectional area for each link in each basin
#effective tidal prism = sum(tidal prism * partitioning coefficient) [summed across all compartments in the basin]
#cross-sectional area = kappa *((effective tidal prism)^alpha)
BITI_Terrebonne_inlet_area = np.zeros(shape=len(BITI_Terrebonne_link))
for n in range(0,len(BITI_Terrebonne_link)):
    BITI_Terrebonne_effective_prism = sum((BITI_Terrebonne_partition[:,n])*BITI_Terrebonne_prism)
    BITI_Terrebonne_inlet_area[n] = np.multiply(kappa, np.power(BITI_Terrebonne_effective_prism,alpha))*BITI_Terrebonne_BWF

BITI_Barataria_inlet_area = np.zeros(shape=len(BITI_Barataria_link))
for n in range(0,len(BITI_Barataria_link)):
    BITI_Barataria_effective_prism = sum((BITI_Barataria_partition[:,n])*BITI_Barataria_prism)
    BITI_Barataria_inlet_area[n] = np.multiply(kappa, np.power(BITI_Barataria_effective_prism,alpha))*BITI_Barataria_BWF

BITI_Pontchartrain_inlet_area = np.zeros(shape=len(BITI_Pontchartrain_link))
for n in range(0,len(BITI_Pontchartrain_link)):
    BITI_Pontchartrain_effective_prism = sum((BITI_Pontchartrain_partition[:,n])*BITI_Pontchartrain_prism)
    BITI_Pontchartrain_inlet_area[n] = np.multiply(kappa, np.power(BITI_Pontchartrain_effective_prism,alpha))*BITI_Pontchartrain_BWF

BITI_inlet_areas = [BITI_Terrebonne_inlet_area,BITI_Barataria_inlet_area,BITI_Pontchartrain_inlet_area]

#BITI depth for each link in each basin
#Depth = sqrt(inlet area*(depth to width ratio))
BITI_Terrebonne_inlet_depth = np.power(np.multiply(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
BITI_Barataria_inlet_depth = np.power(np.multiply(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
BITI_Pontchartrain_inlet_depth = np.power(np.multiply(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

BITI_inlet_depth = [BITI_Terrebonne_inlet_depth,BITI_Barataria_inlet_depth,BITI_Pontchartrain_inlet_depth]

#BITI width for each link in each basin
#Width = sqrt(inlet area/(depth to width ratio))
BITI_Terrebonne_inlet_width = np.power(np.divide(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
BITI_Barataria_inlet_width = np.power(np.divide(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
BITI_Pontchartrain_inlet_width = np.power(np.divide(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

BITI_inlet_width = [BITI_Terrebonne_inlet_width,BITI_Barataria_inlet_width,BITI_Pontchartrain_inlet_width]

#BITI dimensions
#Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
#This dictionary can be used to update the link attributes. All inlet links are Type 1 links.
BITI_inlet_dimensions = {}
for n in range(0,len(BITI_Links)):
    for k in range(0,len(BITI_Links[n])):
        BITI_inlet_dimensions[BITI_Links[n][k]] = ([BITI_inlet_depth[n][k],BITI_inlet_width[n][k]])



#Example of accessing  a link's dimemsions
#Link_554_depth = BITI_inlet_dimensions[554][0]
#Link_554_width = BITI_inlet_dimensions[554][1]
