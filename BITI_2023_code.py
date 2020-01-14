#Barrier Island Tidal Inlet (BITI) Model
import numpy as np

#For standalone testing uncomment the following two lines:
EH_comp_out = np.array([[561,1],[566,2],[575,4],[609,4],[704,5],[705,3]])
EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][1]) for n in range(0,len(EH_comp_out)))

# The two lines above are stand-ins for pulling from Hydro output. FROM 2017 ICM-Py:
# create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
# EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
########### Assuming EH_comp_out is a numpy array, the following works: #############

#Barrier Island Tidal Inlet (BITI) compartment IDs
#These are the compartments that make up each basin
######Will be updated once 2023 compartments finalized##########
BITI_Terrebonne_comp = [561,566,575,609]
BITI_Barataria_comp = [561,566]
BITI_Pontchartrain_comp = [561,566,575,704,705]
BITI_Biloxi_comp = [561,566,575]

#Barrier Island Tidal Inlet (BITI) link IDs
#These are the links that respresent the tidal inlets in each basin
######Will be updated once 2023 links are finalized##########
BITI_Terrebonne_link = [1244,1245,1246]
BITI_Barataria_link = [1244,1245]
BITI_Pontchartrain_link = [1002,1003]
BITI_Biloxi_link = [1000,1001,2000,3000]

BITI_Links = [BITI_Terrebonne_link,BITI_Barataria_link,BITI_Pontchartrain_link,BITI_Biloxi_link]

#Barrier Island Tidal Inlet (BITI) partition coefficients
#Each basin has it's own array of partition coefficients with size m by n,
#where m = number of compartments in the basin and n = the number of links in the basin
######Will be updated once 2023 compartments and links are finalized##########
BITI_Terrebonne_partition = np.array([[0.4,0.6,0],[1,0,0],[0.1,0.8,1],[0,0.1,0.9]])
BITI_Barataria_partition = np.array([[0.4,0.6],[1,0]])
BITI_Pontchartrain_partition = np.array([[0.4,0.6],[1,0],[0.7,0.3],[0.1,0.9],[0.2,0.8]])
BITI_Biloxi_partition = np.array([[0.4,0.6,0,0],[0,0,1,0],[0.1,0,0,0.8]])

#Barrier Island Tidal Inlet (BITI) depth to width ratio (dwr) for each link in each basin (Depth/Width)
BITI_Terrebonne_dwr = [2,2,1]
BITI_Barataria_dwr = [1,0.5]
BITI_Pontchartrain_dwr = [2,0.2]
BITI_Biloxi_dwr= [2,2,1,0.5]

#Barrier Island Tidal Inlet (BITI) tidal prism values
#Get the tidal prism values for each compartment from the Hydro output
BITI_Terrebonne_prism = [EH_prisms.get(comp) for comp in BITI_Terrebonne_comp]
BITI_Barataria_prism = [EH_prisms.get(comp) for comp in BITI_Barataria_comp]
BITI_Pontchartrain_prism = [EH_prisms.get(comp) for comp in BITI_Pontchartrain_comp]
BITI_Biloxi_prism = [EH_prisms.get(comp) for comp in BITI_Biloxi_comp]

#Barrier Island Tidal Inlet (BITI) effective tidal prism and inlet area
#kappa and alpha are the Gulf of Mexico constants for unjettied systems
kappa = 3.51e-4
alpha = 0.86

#Calculate the effective tidal prism and cross-sectional area for each link in each basin
#effective tidal prism = sum(tidal prism * partitioning coefficient) [summed across all compartments in the basin]
#cross-sectional area = kappa *((effective tidal prism)^alpha)
BITI_Terrebonne_inlet_area = np.zeros(shape=len(BITI_Terrebonne_link))
for n in range(0,len(BITI_Terrebonne_link)):
    BITI_Terrebonne_effective_prism = sum((BITI_Terrebonne_partition[:,n])*BITI_Terrebonne_prism)
    BITI_Terrebonne_inlet_area[n] = np.multiply(kappa, np.power(BITI_Terrebonne_effective_prism,alpha))

BITI_Barataria_inlet_area = np.zeros(shape=len(BITI_Barataria_link))
for n in range(0,len(BITI_Barataria_link)):
    BITI_Barataria_effective_prism = sum((BITI_Barataria_partition[:,n])*BITI_Barataria_prism)
    BITI_Barataria_inlet_area[n] = np.multiply(kappa, np.power(BITI_Barataria_effective_prism,alpha))

BITI_Pontchartrain_inlet_area = np.zeros(shape=len(BITI_Pontchartrain_link))
for n in range(0,len(BITI_Pontchartrain_link)):
    BITI_Pontchartrain_effective_prism = sum((BITI_Pontchartrain_partition[:,n])*BITI_Pontchartrain_prism)
    BITI_Pontchartrain_inlet_area[n] = np.multiply(kappa, np.power(BITI_Pontchartrain_effective_prism,alpha))

BITI_Biloxi_inlet_area = np.zeros(shape=len(BITI_Biloxi_link))
for n in range(0,len(BITI_Biloxi_link)):
    BITI_Biloxi_effective_prism = sum((BITI_Biloxi_partition[:,n])*BITI_Biloxi_prism)
    BITI_Biloxi_inlet_area[n] = np.multiply(kappa, np.power(BITI_Biloxi_effective_prism,alpha))

BITI_inlet_areas = [BITI_Terrebonne_inlet_area,BITI_Barataria_inlet_area,BITI_Pontchartrain_inlet_area,BITI_Biloxi_inlet_area]

#Barrier Island Tidal Inlet (BITI) depth for each link in each basin
#Depth = sqrt(inlet area*(depth to width ratio))
BITI_Terrebonne_inlet_depth = np.power(np.multiply(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
BITI_Barataria_inlet_depth = np.power(np.multiply(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
BITI_Pontchartrain_inlet_depth = np.power(np.multiply(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)
BITI_Biloxi_inlet_depth = np.power(np.multiply(BITI_Biloxi_inlet_area,BITI_Biloxi_dwr),0.5)

BITI_inlet_depth = [BITI_Terrebonne_inlet_depth,BITI_Barataria_inlet_depth,BITI_Pontchartrain_inlet_depth,BITI_Biloxi_inlet_depth]


#Barrier Island Tidal Inlet (BITI) width for each link in each basin
#Width = sqrt(inlet area/(depth to width ratio))
BITI_Terrebonne_inlet_width = np.power(np.divide(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
BITI_Barataria_inlet_width = np.power(np.divide(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
BITI_Pontchartrain_inlet_width = np.power(np.divide(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)
BITI_Biloxi_inlet_width = np.power(np.divide(BITI_Biloxi_inlet_area,BITI_Biloxi_dwr),0.5)

BITI_inlet_width = [BITI_Terrebonne_inlet_width,BITI_Barataria_inlet_width,BITI_Pontchartrain_inlet_width,BITI_Biloxi_inlet_width]

#Barrier Island Tidal Inlet (BITI) dimensions
#Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
#This dictionary can be used to update the link attributes. All inlet links are Type 1 links.
BITI_inlet_dimensions = {}
for n in range(0,len(BITI_Links)):
    for k in range(0,len(BITI_Links[n])):
        BITI_inlet_dimensions[BITI_Links[n][k]] = ([BITI_inlet_depth[n][k],BITI_inlet_width[n][k]])

print(BITI_inlet_dimensions)

#Example of accessing  a link's dimemsions (i.e., how ICM will read back output)
Link_1244_depth = BITI_inlet_dimensions[1244][0]
Link_1244_width = BITI_inlet_dimensions[1244][1]
