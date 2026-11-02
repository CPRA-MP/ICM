Integrated Compartment Model (ICM)
================
Denise J. Reed & Eric D. White

------------------------------------------------------------------------

Citation:

Reed, D., & White, E. D. (2023). 2023 Coastal Master Plan: Appendix C:
Use of Predictive Models in the 2023 Coastal Master Plan. Version 3.
(p. 13-22). Baton Rouge, Louisiana: Coastal Protection and Restoration
Authority.

------------------------------------------------------------------------

## Contents

1.  [ICM OVERVIEW](#10-icm-overview)
    1.  [HYDROLOGY](#11-hydrology)
    2.  [VEGETATION](#12-vegetation)
    3.  [WETLAND MORPHOLOGY](#13-wetland-morphology)
    4.  [BARRIER ISLANDS](#14-barrier-islands)
    5.  [ECOSYSTEM OUTCOMES](#15-ecosystem-outcomes)
2.  [ICM BOUNDARY CONDITIONS](#20-icm-boundary-conditions)
3.  [FUTURE ENVIRONMENTAL SCENARIOS](#30-future-environmental-scenarios)
4.  [REFERENCES](#40-references)

## 1.0 ICM Overview

The ICM is a planning-level model that was developed by integrating into
a single modeling platform several models (now referred to as ICM
subroutines) that were previously used for coastal zone planning and
research in Louisiana (White et al., 2017). Subroutines within the ICM
framework include a hydrologic and hydraulic model, a vegetation
dynamics model, a wetland morphology/elevation change model, as well as
a barrier island model and several receptor models that summarize the
hydrologic and landscape conditions into numerous habitat indices and
metrics used in decision-making. The following sections provide an
overview of these subroutine and outline updates made to many aspects of
the ICM for use in the 2023 Coastal Master Plan.

### 1.1 Hydrology

Hydrologic conditions are simulated within the ICM-Hydro subroutine.
This subroutine is a link-node mass balance model capable of simulating:
water level (stage), flow rate, salinity, water temperature, suspended
sediment concentration, sediment deposition and resuspension within open
water areas, and sediment deposition on the marsh surface (Meselhe et
al., 2013; White et al., 2019; Reed et al., 2020). The model is driven
by boundary condition data representing tidal water levels and
salinities as well as tributary inflows (and corresponding salinity and
suspended sediment concentrations). Environmental forcing data
representing rainfall, temperature, evapotranspiration, and wind are
also required model inputs (see Appendix B: Scenario Development &
Future Conditions for more details).

The link-node structure of ICM-Hydro utilizes an idealized geometry of
the estuary where each model node, or compartment, represents a unit of
open water surrounded by marsh area (and in some cases non-tidal upland
drainage areas). Some of the compartment attributes included in the
model are updated annually by other ICM subroutines, primarily ICM-Morph
(e.g., open water bed elevation, marsh surface elevation, portion of
compartment that is open water). Other attributes remain constant
throughout the simulation periods (e.g., surface roughness of the bed,
surface roughness of the marsh). For the 2023 Coastal Master Plan,
compartment resolution was refined to better reflect landscape
topography and water management features, the latter especially in the
Chenier Plain (Figure 1). The domain was also extended into tributary
basins to include the lowest gaging points.

A one dimensional (1D) open channel flow routing algorithm for
channelized flows such as rivers and navigational channels has been
added for the Mississippi River, the Atchafalaya River, and the
Calcasieu River/Ship Channel (Figure 1). The addition of this 1D model
resulted in two distinct improvements to ICM-Hydro. First, in the
Mississippi and Atchafalaya River deltas, the use of the 1D channel
routing algorithms improves the ability of the model to simulate
changing flow distributions in the river delta distributary passes as a
result of upstream management (e.g., large scale river diversions) and
downstream changes due to SLR. The second improvement relates to
modeling flood tide propagation up-channel. This is of particular
importance to the Calcasieu River/Ship Channel where salinity intrusion
and tidal dynamics are an important driver of the hydrology of the
Calcasieu-Sabine Basin.

![](C:/Users/P00357462/Documents/MP23%20Appendices%20for%20GitHub/ICM/C_ICM_Fig1.png)  

<caption>

Figure 1. Final ICM-Hydro domain.
</caption>

More details on ICM-Hydro are provided in Attachment C7: 2023 ICM-Hydro
Model.

### 1.2 Vegetation

Annual land cover, represented by the relative abundance of vegetation
species and the amount of bareground, is modeled within the ICM-LAVegMod
vegetation modeling subroutine (Visser & DukeSylvester, 2017). This
model utilizes mean salinity during the growing season (May through
August), the maximum 2-week salinity (used for swamp forest and fresh
marsh species), mean water level (used for bottom land hardwood
species), and variability of the water surface, defined as the standard
deviation (SD) of the water level during the year from ICM-Hydro. The
vegetation model operates on an annual timestep. For most species, mean
salinity during the growing season (May through August) and variability
of the water surface are used to determine changes in vegetation,
reflecting the damaging effect of ‘stagnant’ flooding conditions in some
wetlands, especially forested wetlands (Conner et al., 2014; Shaffer et
al., 2016).

These data determine the relative likelihood that a wetland plant
species currently on the modeled landscape would experience any
mortality. The further from its preferred hydrologic condition, the
greater probability of mortality for the species. If coverage of a
species is reduced, that area becomes bareground is eligible for new
vegetation to establish. If the right environmental conditions exist,
species will establish on the bareground, and the vegetation community
will change. Dispersal rules govern this process and have been updated
for the 2023 Coastal Master Plan to include three categories for species
based on their proximity to the bareground, with one category that can
establish anywhere that the right conditions exist (Attachment D2:
ICM-Wetlands, Vegetation & Soils Model Improvements; Attachment C8: 2023
Modeling Wetland Vegetation and Morphology: ICM-LAVegMod and ICM-Morph).
The result is that establishment will always occur if salinity is lower
than ~3 ppt or greater than ~20 ppt (Figure 2). The species list has
also been updated, and changes have been made to the flotant algorithm
to allow thick mat flotant an opportunity to re-establish following
mortality and transition to ‘bare flotant’ if environmental conditions
are appropriate.

Once simulated, the 33 species modeled are assigned a score based on the
habitat type they are most often associated with (Forested, Fresh,
Intermediate, Brackish, or Saline \[FFIBS\]). Habitat type is then
assigned based on the cover weighted average score assigned to each
species (Visser, 2002). The habitat type and FFIBS score are used in the
subsequent ICM subroutine, ICM-Morph.

![](C:/Users/P00357462/Documents/MP23%20Appendices%20for%20GitHub/ICM/C_ICM_Fig2.png)  

<caption>

Figure 2. Sum of establishment conditions for all high dispersal species
used in ICM-LAVegMod.
</caption>

More details on ICM-LAVegMod are provided in [Attachment C8: 2023
Modeling Wetland Vegetation and Morphology: ICM-LAVegMod and
ICM-Morph](https://coastal.la.gov/wp-content/uploads/2024/02/C8_ICM-LAVegModICM-Morph_v2.pdf).

### 1.3 Wetland Morphology

The wetland morphology subroutine, ICM-Morph, simulates annual elevation
change and wetland transition to and from open water over time as a
function of dynamic variables modeled by the ICMHydro and ICM-LAVegMod
subroutines: average and maximum annual water levels, mean annual
salinity, inorganic sediment deposition on the marsh edge and interior
surfaces, and FFIBS score.

Elevation change of the marsh surface is a function of downward and
upward shifts. Surface elevation is lowered due to subsidence
(Attachment B3: Determining Subsidence Rates for use in Predictive
Modeling) and the gradual lowering of bareground where vegetation
species have been subject to mortality the previous year and no species
were established. Vertical accretion, based on mineral sediment
deposition and organic matter accumulation, increases elevation. Mineral
sediment deposition is dynamically linked to the ICM-Hydro simulations
and is assessed on a monthly basis based on which areas have been
subject to inundation (Figure 3). Organic matter accumulation rates by
habitat, derived from Coastwide Reference Monitoring System (CRMS) data,
are interpolated based on FFIBS score ([Attachment C8: 2023 Modeling
Wetland Vegetation and Morphology: ICM-LAVegMod and
ICM-Morph](https://coastal.la.gov/wp-content/uploads/2024/02/C8_ICM-LAVegModICM-Morph_v2.pdf)).
Mineral and organic accretion are derived using the ideal mixing model
(Morris et al., 2016) and self-packing densities also developed from
CRMS data ([Attachment D2: ICM-Wetlands, Vegetation & Soils Model
Improvements](https://coastal.la.gov/wp-content/uploads/2023/08/D2_2023ICM-Wetlands-Veg-Soils-Model-Improvements_Jun2020_v2.pdf))
(Figure 3). Total accretion on the wetland surface is the sum of mineral
and organic components.

![](C:/Users/P00357462/Documents/MP23%20Appendices%20for%20GitHub/ICM/C_ICM_Fig3.png)  

<caption>

Figure 3. Process and conceptual diagram for vertical accretion
functions in ICM.
</caption>

Transitions from water to land occur when bed elevation of open water
areas increases, through mineral sediment deposition, to within 10 cm of
the annual mean water level. Areas meeting these conditions are
classified as bareground and eligible for vegetation establishment in
ICM-LAVegMod.

Two mechanisms in the model drive transitions from land to water: marsh
edge erosion and excessive inundation of vegetation. Marsh edge erosion
(MEE) rates are based on historical rates estimated by U.S. Geological
Survey (USGS) and imposed as a temporally constant, yet spatially
varied, linear erosive rate (Attachment B1: Landscape Input Data;
Allison et al., 2017). ICM-Morph pixels that are classified as edge,
except in locations with revetment or shoreline protection features, are
subject to the MEE rates, and 30 m pixels are converted from land to
water, with a depth of 0.25m,over time as erosion proceeds, e.g., MEE
rate of 2 m/yr results in loss of 30 m every 15 years.

The approach for converting herbaceous vegetated wetlands to open water
was changed for the 2023 Coastal Master Plan. CRMS data was used to
identify environmental conditions, based on annual mean salinity and
inundation (a function of surface elevation and water level), that can
be tolerated by non-forested wetland vegetation, and those where
emergent vegetation does not survive. The inundation tolerance of the
vegetation varies by salinity (Figure 4), and if environmental
conditions exceed the 99.5th percentile line shown in Figure 4 for two
consecutive years, land is converted to open water and is not eligible
for vegetative establishment.

![](C:/Users/P00357462/Documents/MP23%20Appendices%20for%20GitHub/ICM/C_ICM_Fig4.png)  

<caption>

Figure 4. Salinity-inundation depth relationship used to define water
depth limitation on vegetation (from CRMS data analysis). Lines are the
0.5th (gray) and 99.5th (blue) percentiles.
</caption>

These processes are applied on an annual timestep in ICM-Morph and
result in changes in the configuration of land and water across the
landscape.

More details on ICM-Morph are provided in [Attachment C8: 2023 Modeling
Wetland Vegetation and Morphology: ICM-LAVegMod and
ICM-Morph](https://coastal.la.gov/wp-content/uploads/2024/02/C8_ICM-LAVegModICM-Morph_v2.pdf).

### 1.4 Barrier Islands

Barrier islands are considered using two separate modules: the Barrier
Island Tidal Inlet Module (ICM-BITI), which models the evolution of
tidal inlets along barrier islands as informed by basin hydraulics, and
the Barrier Island Digital Elevation Model (ICM-BI), which models island
configuration through time to support storm surge modeling ([Attachment
D4: ICM-BI Model
Improvements](https://coastal.la.gov/wp-content/uploads/2023/06/D4_ICM-BIModelImprovements_Nov2020_v3.pdf)).
The ICM-BITI module is fully incorporated in the ICM, while ICM-BI
informs the model at annual timesteps (Figure 5).

The ICM-BITI module captures the positive relationship between tidal
inlet cross sectional area and backbarrier tidal prism. Due to the size
of each coastal basin and the presence of multiple barrier island tidal
inlets per basin, ICM-BITI assigns a fraction of the total tidal prism
to each tidal inlet. The module evolves inlets as the size of the
backbarrier basin and tidal prism increases over time as land converts
to open water.

ICM-BI uses historic barrier island cross-shore retreat rates under
varying SLR scenarios to migrate barrier island transects. The transects
migrate based on cross-shore retreat rates of index profiles selected to
represent key geomorphic features along the coast. The subroutine also
includes an auto-restoration feature that increases the profile of the
islands on restoration units that drop below a critical width threshold.

![](C:/Users/P00357462/Documents/MP23%20Appendices%20for%20GitHub/ICM/C_ICM_Fig5.png)  

<caption>

Figure 5. Flow diagram of ICM-BI and ICM-BITI
</caption>

ICM-BI simulates change for six island regions: Isles Dernieres,
Timbalier, Caminada Headland and Grand Isle, Barataria, Breton Island,
and Chandeleur Island, with a number of smaller restoration units within
each region. A new digital elevation model for the barrier islands is
available annually for use in other ICM subroutines and ADCIRC.

More details on the barrier island models are provided in [Attachment
C9: 2023 Barrier Island Model: ICM-BI and
ICM-BITI](https://coastal.la.gov/wp-content/uploads/2023/08/C9_2023BarrierIslandModel_ICM-BITI_ICM-BI_Feb2021_v3.pdf).

### 1.5 Ecosystem Outcomes

Once the hydrologic and landscape modeling subroutines simulate a full
year, model outputs are used to quantify effects on the ecosystem using
a suite of habitat suitability indices. These use output data from other
subroutines including salinity, temperature, sediment deposition, and
changes in land cover, wetland coverage, and habitat features.

Habitat suitability index (HSI) models are used to generate a relative
score for the condition (i.e., suitability) of an area to support a
particular organism. HSI models consist of simplified relationships that
relate key environmental variables to the quality of the habitat for
that organism. The relationships, termed suitability indices, are
standardized on a 0 to 1 scale, with 1 being the most favorable
conditions and 0 being completely unsuitable. Statistical relationships
were developed using field data (from the Louisiana Department of
Wildlife and Fisheries \[LDWF\] long-term fisheries-independent
monitoring program) to predict fish and shellfish catch-per-unit effort
from key environmental variables collected concurrently with the fish
sampling, namely salinity and temperature ([Attachment D5: ICM-HSI Model
Improvements](https://coastal.la.gov/wp-content/uploads/2023/06/D5_HSIModelImprovements_Nov2022_v3.pdf)).
For key environmental variables in which statistical relationships could
not be developed, such as availability of marsh habitat area, literature
values and expert professional judgment were used to generate
suitability indices. The final HSI equation for each species was then
generated by aggregating both the statistically and expertly derived
relationships into a single suitability index value. The bald eagle HSI
model was developed using LDWF bald eagle aerial nest surveys and land
cover data. Expert derived relationships are used for all variables in
the oyster and wildlife HSIs, except for bald eagle. The species for
which HSIs were calculated include mottled duck, green-winged teal,
gadwall, wild-caught crawfish, alligator, brown pelican, seaside
sparrow, bald eagle , blue crab (juvenile), brown shrimp (large and
small juveniles), white shrimp (large and small juveniles), Gulf
menhaden (adult and juvenile), bay anchovy (adult and juvenile), spotted
sea trout (adult and juvenile), largemouth bass, and oysters.

More details on the habitat suitability models are provided in
[Attachment C10: 2023 Habitat Suitability Index (HSI)
Model](https://coastal.la.gov/wp-content/uploads/2023/08/C10_2023HSIModel_Feb2023_v3.pdf).

## 2.0 ICM Boundary Conditions

Many boundary forcings vary by environmental scenario (see Section 2.3).
However, a single future scenario hydrograph is used for Mississippi and
Atchafalaya River flows. The USACE continental-scale Routing Application
for Parallel Computation of Discharge (RAPID) Hydraulics and Hydrology
(H&H) model generated daily river flows for a 16-member ensemble using
Intergovernmental Panel on Climate Change (IPCC) Representative
Concentration Pathway (RCP)-4.5 daily precipitation forcing (Lewis et
al., 2019). The ensemble runs were examined in terms of the total volume
of freshwater, springtime flood peak discharge, and the number of Bonnet
Carre openings. The ensemble mean +0.6 SD was used as it matches the
historical spring flood peak and has a low bias in relation to Bonnet
Carre openings, while increasing freshwater flux 15% over the historic
mean. Suspended mineral sediment concentrations were derived for the
Mississippi River based upon a separate sediment rating curve for sand
and fines developed from field sampling conducted in the Mississippi
River at Belle Chasse (Allison et al., 2012).

Separate sand and fines sediment rating curves were developed for the
Atchafalaya River from observed USGS data. Rating curves were developed
for total suspended sediments from paired discharge-total suspended
solids (TSS) observed data timeseries for tributaries in the Florida
Parishes east of the Mississippi River. The derived TSS concentration
timeseries were then partitioned into sand and fines portions by using
the sand/fine partitioning relationships found in the Mississippi River
observations. For Florida Parishes tributaries without any paired
discharge-TSS observational data, tributary drainage area relationships
developed by Roblin (2008) were used. Due to a lack of observational
data for tributaries west of the Atchafalaya River, a single sediment
rating curve was developed for Chenier Plain tributaries, with an
adjusted-lower sand/fine partitioning relationship than the other
coastal tributaries. For a full discussion of the sediment rating curves
and sand/fine partitioning methodologies, refer to [Attachment B2:
Scenario Development: Sea Level Rise and Additional Climate-Driven
Variables](https://coastal.la.gov/wp-content/uploads/2023/11/B2_ScenarioDevel_SLRAdditionalClimateDrivenVariables_Nov2023_v2.pdf).

Gridded wind velocity and direction timeseries were compiled from the
North American Regional Reanalysis climate dataset. Salinity
concentrations in the offshore Gulf waters were developed from observed
data samples (Brown, 2017). Gridded rainfall timeseries were prepared
for the ICM-Hydro domain, with one bias-adjusted radar rainfall
timeseries provided for each ICM-Hydro compartment (Sharif et al.,
2020). Observed daily air temperature, Mississippi River water
temperature, and estuarine water temperature timeseries were also used.
Observed tidal water levels in the Gulf of Mexico were used from five
observation stations ranging from Dauphin Island, Alabama to Sabine
Pass, Louisiana.

While the observed datasets described above were used for the model
calibration (2010-2018) and validation (2006-2009) periods, the boundary
conditions were adjusted for future environmental scenarios, as
described in Appendix B: Scenario Development & Future Conditions.
Temperature, precipitation, and coastal tributary river flow boundary
forcings were adjusted independently for each future environmental
scenario; the exact adjustments made were dependent upon temperature and
rainfall anomalies that were calculated from climate change model
ensembles made available through the World Climate Research Program’s
Coupled Model Intercomparison Project (CMIP5).

To project tidal water levels for each future environmental scenario,
observed tidal data was first decomposed into six constituent
components: 1) astronomic tidal fluctuations; 2) local gage-specific
subsidence; 3) Gulf wide SLR; 4) acute surge from tropical cyclones; 5)
seasonal temperature fluctuation; and 6) the residual water level
fluctuation that was the result of wind, frontal passages, and other
localized weather events. Each of these constituent tidal components
could then be treated independently under future environmental scenario
assumptions.

For all future environmental scenarios, the wind timeseries was not
adjusted; the observed wind record from 2010 was used for every single
year; this year was chosen for the lack of any hurricanes making
landfall in coastal Louisiana. Corresponding to this single wind-year,
water level deviations in coastal waters that corresponded to wind and
frontal passages from 2010 were also used for every year in all future
environmental scenarios. Additionally, the seasonal temperature and
astronomic tidal fluctuations from 2010 were also repeated each year in
all future scenarios.

Subsidence was treated as a scenario-specific variable applied to all
model subroutines; and therefore, was not directly applied to the tidal
boundary conditions in ICM-Hydro; rather the entire modeled landscape
was subjected to a subsidence forcing (see Section 2.3). Eustatic SLR
was a prime component of each assumed future environmental scenario and
was subsequently applied to the tidal boundary condition in all
ICM-Hydro simulations, with the exact rate of SLR being assigned as a
unique value to each scenario, as discussed in section 2.3 (Table 1).

Storm forcing in the ICM is represented by a sequence of synthetic
storms that maintains the same frequency of landfall as the historic
record, while reducing the variability in the number and severity of
events each ICM compartment experiences. The storms were identified by
extracting water surface elevation (WSE) for both interior water bodies
and more exposed coastal waters from ADCIRC simulations of the 645
synthetic storms (Attachment B4: Storm Selection for the ICM). The
resulting ICM synthetic storm sequence balances the number of 20%, 10%,
2%, and 1% annual exceedance probability (AEP) – 5-, 10-, 50-, and
100-year return intervals, respectively – water surface elevation events
at 33 locations across the coast. A storm was considered to “match” a
given AEP if its peak WSE is within 0.5 ft of the estimated WSE
exceedance corresponding to that AEP. This resulted in a “balanced”
storm suite where each of the 33 locations across the coast was exposed
to the same cumulative likelihood of storm-induced inundation across the
50-year FWOA period.

## 3.0 Future Environmental Scenarios

While a number of future environmental scenarios were used to generate
information about the response of the coastal landscape and ecosystem to
climate change and subsidence (see Appendix H: Exploratory Analysis),
two scenarios were used for project selection. Model runs for future
scenario simulations use boundary forcings (temperature, precipitation,
evapotranspiration, coastal zone tributary hydrographs) coupled to the
SLR curves included in the scenario (Table 1). The process used to
develop the scenarios is described in [Appendix B: Scenario Development
& Future
Conditions](https://coastal.la.gov/wp-content/uploads/2023/09/B_ScenarioDevelopmentFutureConditions_Jan2023_v3.pdf).

<caption>

Table 1. Values used in lower and higher environmental scenarios
</caption>

|  | Lower | Higher |
|----|----|----|
| Sea level rise (regionally adjusted) | NOAA\* Intermediate: ~0.50 m by 2070; ~1.07 m by 2100 | NOAA Intermediate High: ~0.77 m by 2070; 1.75 m by 2100 |
| Temperature and Evapotranspiration | following RCP 4.5 50th percentile | following RCP 8.5 50th percentile |
| Precipitation and Tributary flows | following RCP 4.5 50th percentile | following RCP 8.5 50th percentile |
| Subsidence | deep subsidence + 1st quartile shallow subsidence by ecoregion | deep subsidence + median shallow subsidence by ecoregion |
| Storm Intensity (Risk analysis only) | +5% over 50 years | +10% over 50 years |

\* National Oceanic and Atmospheric Administration (NOAA)

Subsidence values varied spatially across the model domain. The approach
uses a deep subsidence map derived from data from geodetic survey
benchmarks, both primary (Continuously Operating Reference Stations) and
secondary (CPRA/National Geodetic Survey benchmarks), and two shallow
subsidence maps created using data from rod surface elevation
table-marker horizon measurements taken at CRMS sites ([Attachment B3:
Determining Subsidence Rates for use in Predictive
Modeling](https://coastal.la.gov/wp-content/uploads/2023/08/B3_DeterminingSubsidenceRates_Mar2021_v3.pdf)).
Two maps were created due to variability in the shallow subsidence data,
and these were applied separately for the two environmental scenarios
used in the master plan analysis. As the shallow subsidence maps are
derived from CRMS data, no rates are calculated for the Atchafalaya
Basin and the Verret Basin.

## 4.0 References

Allison, M.A., Chen, Q.J., Couvillion, B., Leadon, M., McCorquodale, A.,
Meselhe, E., Ramatchandirane, C., Reed, D.J., & White, E.D. (2017). 2017
Coastal Master Plan: Model Improvement Plan, Attachment C3-2: Marsh Edge
Erosion. (No. Final). Coastal Protection and Restoration Authority of
Louisiana.
<http://coastal.la.gov/wp-content/uploads/2017/04/Attachment-C3-2_FINAL_02.23.2017.pdf>

Allison, M. A., Demas, C. R., Ebersole, B. A., Kleiss, B. A., Little, C.
D., Meselhe, E. A., … & Vosburg, B. M. (2012). A water and sediment
budget for the lower Mississippi–Atchafalaya River in flood years
2008–2010: Implications for sediment discharge to the oceans and coastal
restoration in Louisiana. Journal of Hydrology, 432, 84-97.

Baustian, M.M., Reed, D., Visser, J., Duke-Sylvester, S., Snedden, G.,
Wang, H., DeMarco, K., FosterMartinez, M., Sharp, L.A., McGinnis, T., &
Jarrell, E. (2020). 2023 Coastal Master Plan: Model Improvement Plan,
ICM-Wetlands, Vegetation, and Soil. Version I. (p. 155). Baton Rouge,
Louisiana: Coastal Protection and Restoration Authority.

Brown, S. (2017). 2017 Coastal Master Plan Modeling: Attachment C3-26:
Hydrology and Water Quality Boundary Conditions. Version Final.
(pp. 1-44). Baton Rouge, Louisiana: Coastal Protection and Restoration
Authority.

Conner, W.H., Duberstein, J.A., Day, J.W., & Hutchinson, S. (2014).
Impacts of Changing Hydrology and Hurricanes on Forest Structure and
Growth Along a Flooding/Elevation Gradient in a South Louisiana Forested
Wetland from 1986 to 2009. Wetlands, 34(4), 803–14.

Coastal Protection and Restoration Authority. (2023). 2023 Coastal
Master Plan: Appendix B: Scenario Development and Future Conditions.
Version 3. (pp. 1-18). Baton Rouge, Louisiana: Coastal Protection and
Restoration Authority.

Dalyander, S., Foster-Martinez, M., Di Leonardo, D., Georgiou, I.Y., &
Miner, M.D., Fitzpatrick, C.E. (2020). 2023 Coastal Master Plan
Louisiana Coastal Master Plan Barrier Island Tidal Inlet (ICM-BITI)
Module and Barrier Island Digital Elevation Model (ICM-BI) Updates.
Version I. (p. 70). Baton Rouge, Louisiana: Coastal Protection and
Restoration Authority.

Fitzpatrick, C., Jankowski, K.L., & Reed, D. (2020). 2023 Coastal Master
Plan: Determining Subsidence Rates for Use in Predictive Modeling.
Version I. (p. 70). Baton Rouge, Louisiana: Coastal Protection and
Restoration Authority.

Foster-Martinez, M., White, E., Jarrell, E., Reed, D., & Visser, J.
(2023). 2023 Coastal Master Plan: Attachment C8: Modeling Wetland
Vegetation and Morphology: ICM-LAVegMod and ICM-Morph. Version 2.
(p. 59). Baton Rouge, Louisiana: Coastal Protection and Restoration
Authority.

Lewis, J., Tavakoly, A., Martin, C. & Morre, C. (2019). Mississippi
River and Tributaries Future Flood Conditions. U.S. Army Corps of
Engineers, Mississippi Valley Division, MRG&P Report No. 28

Lindquist, D.C., Sable, S.E., D’Acunto, L., Hijuelos, A.C., Johnson,
E.I., Langlois, S.R.M., Michel, N.L., Nakashima, L., O’Connell, A.M.,
Percy, K., & Robinson, E.M. (2020). 2023 Coastal Master Plan: Habitat
Suitability Index Model Improvements. Draft Final (194 p.). Baton Rouge,
Louisiana: Coastal Protection and Restoration Authority.

Lindquist, D. C. (2023). 2023 Coastal Master Plan: Attachment C10: 2023
Habitat Suitability Index (HSI) Model. Version 3. (pp. 1-35). Baton
Rouge, Louisiana: Coastal Protection and Restoration Authority.

Meselhe, E., McCorquodale, J.A., Shelden, J., Dortch, M., Brown, T.S.,
Elkan, P., … Wang, Z. (2013). Ecohydrology component of Louisiana’s 2012
Coastal Master Plan: Mass-balance compartment model. Journal of Coastal
Research, 67, 16–28. <https://doi.org/10.2112/SI_67_2.1>

Morris, J.T., Barber, D.C., Callaway, J.C., Chambers, R., Hagen, S.C.,
Hopkinson, C.S., Johnson, B.J., Megonigal, P., Neubauer, S.C., Troxler,
T., & Wigand, C. (2016). Contributions of organic and inorganic matter
to sediment volume and accretion in tidal wetlands at steady state.
Earth’s Future, 4(4), 110–121.

Pahl, J. W., Freeman, A. M, Fitzpatrick, C., Jankowski, K. L., & White,
E. D. (2023). 2023 Coastal Master Plan: Attachment B2: Scenario
Development: Sea Level Rise and Additional Climate-Driven Variables.
Version 2. (p. 43). Baton Rouge, Louisiana: Coastal Protection and
Restoration Authority.

Reed, D., Wang, Y., Meselhe, E., & White, E. 2020. Modeling wetland
transitions and loss in coastal Louisiana under scenarios of future
relative sea-level rise. Geomorphology, 352, 106991.

Roblin, R. (2008). Water quality modeling of freshwater diversions in
the Pontchartrain estuary. (Unpublished master’s thesis). University of
New Orleans, New Orleans, LA.

Shaffer, G.P., Day, J.W., Kandalepas, D., Wood, W.B., Hunter, R.G.,
Lane, R.R., & Hillmann, E.R. (2016). Decline of the Maurepas Swamp,
Pontchartrain Basin, Louisiana, and approaches to restoration. Water,
8(3), 101.

Sharif, R.B., Habib, E.H., & El Saadani, M. (2020). Evaluation of
radar-rainfall products over Coastal Louisiana. Remote Sensing. 12, 9.
<https://doi.org/10.3390/rs12091477>

Visser, J.M. & Duke-Sylvester, S.M. (2017). LaVegMod v2: Modeling
coastal vegetation dynamics in response to proposed coastal restoration
and protection projects in Louisiana, USA. Sustainability, 9, 1625.
<http://dx.doi.org/10.3390/su9091625>

Visser, J.M., Sasser, C.E., Chabreck, R.H., & Linscombe, R.G. (2002).
The impact of a severe drought on the vegetation of a subtropical
estuary. Estuaries, 25(6,), 1184–1195.

White, E.D., Meselhe, E., Reed, D., Renfro, A., Snider, N.P., & Wang, Y.
2019. Mitigating the Effects of Sea-Level Rise on Estuaries of the
Mississippi Delta Plain Using River Diver-sions. Water, 11(10), 2028.

White, E., Meselhe, E., McCorquodale, A., Couvillion, B., Dong, Z.,
Duke-Sylvester, S. M., & Wang, Y. (2017). 2017 Coastal Master Plan:
Attachment C3-22: Integrated Compartment Model (ICM) Development
(pp. 1–49) \[Version Final\]. Coastal Protection and Restoration
Authority.
