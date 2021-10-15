#!/bin/bash

for S in S06 S07 S08 S09
do
	for G in G500 # G501 G502 G503 G504 G505
	do
		echo $S $G
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM/ICM.py $S/$G/ICM.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM/ICM_batch.py $S/$G/ICM_batch.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM/ICM_control_update.py $S/$G/ICM_control_update.py
		
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/config.py $S/$G/veg/config.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/event.py $S/$G/veg/event.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/function.py $S/$G/veg/function.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/landscape.py $S/$G/veg/landscape.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/lavegmod.py $S/$G/veg/lavegmod.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/model_v3.py $S/$G/veg/model_v3.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/plantingmodel.py $S/$G/veg/plantingmodel.py
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/MP2023_LaVegMod3_Establishment_Tables.xlsx $S/$G/veg/MP2023_LaVegMod3_Establishment_Tables.xlsx
		cp /ocean/projects/bcs200002p/ewhite12/code/ICM_LAVegMod/MP2023_LaVegMod3_Mortality_Tables.xlsx $S/$G/veg/MP2023_LaVegMod3_Mortality_Tables.xlsx
		
	 
		ln -s /ocean/projects/bcs200002p/ewhite12/code/ICM_Morph/build/morph_v23.1.1 $S/$G/morph_v23.1.1
		
		ln -s /ocean/projects/bcs200002p/ewhite12/code/ICM_Hydro/build/hydro_v23.4.1 $S/$G/hydro/hydro_v23.4.1

		for B in Barataria Breton Caminada Chandeleurs IsleDernieres Timbalier
		do	
			echo $B
			ln -s /ocean/projects/bcs200002p/ewhite12/code/ICM_BIDEM/build/bidem_v23.0.0 $S/$G/bidem/$B/bidem_v23.0.0
		done
	done
done
