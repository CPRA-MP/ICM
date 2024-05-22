#Python imports
import subprocess


def RunMorph(wetland_morph_dir, startyear, elapsedyear, ncomp, year, fwoa_init_cond_tag, file_prefix_prv,
             exist_cond_tag, shallow_subsidence_column, file_oprefix, monthly_file_avstg, monthly_file_mxstg,
             monthly_file_sdowt, act_del_file_2use, monthly_file_sdint, monthly_file_sdedg, monthly_file_avsal,
             monthly_file_avtss, bidem_xyz_file, file_prefix, new_grid_filepath, grid_Gdw_dep_file, 
             grid_GwT_dep_file, grid_MtD_dep_file, grid_pct_edge_file, comp_elev_file, comp_wat_file, 
             comp_upl_file, dem_grid_data_outfile, file_o_01_end_prefix, n_mc_yr, mc_project_list_yr, 
             mc_project_list_VolArea_yr, n_rr_yr, rr_project_list_yr, n_sp_cumul, sp_project_list_cumul,
             morph_exe_path, mc_depth_threshold_def, dem_res
             ):
      
        
    #########################################################
    ##          RUN MORPH MODEL FOR CURRENT YEAR           ##
    #########################################################

    # read in Wetland Morph input file and update variables for year of simulation
    wm_param_file = r'%s/input_params.csv' % wetland_morph_dir
    morph_zonal_stats = 0               # 1=zonal stats run in ICM-Morph; 0=zonal stats run in ICM
    
    with open (wm_param_file, mode='w') as ip_csv:
        ip_csv.write("%d, start_year - first year of model run\n" % startyear)
        ip_csv.write("%d, elapsed_year - elapsed year of model run\n" % elapsedyear)
        ip_csv.write("%d, dem_res - XY resolution of DEM (meters)\n" % dem_res)
        ip_csv.write("-9999, dem_NoDataVal - value representing nodata in input rasters and XYZ files\n")
        ip_csv.write("171284090, ndem - number of DEM pixels - will be an array dimension for all DEM-level data\n")
        ip_csv.write("2904131, ndem_bi - number of pixels in interpolated ICM-BI-DEM XYZ that overlap primary DEM\n")
        ip_csv.write("%d, ncomp - number of ICM-Hydro compartments - will be an array dimension for all compartment-level data\n" % ncomp)
        ip_csv.write("173898, ngrid - number of ICM-LAVegMod grid cells - will be an array dimension for all gridd-level data\n")
        ip_csv.write("32, neco - number of ecoregions\n")
        ip_csv.write("5, nlt - number of landtype classifications\n")
        ip_csv.write("0.10, ht_above_mwl_est - elevation (meters) relative to annual mean water level at which point vegetation can establish\n")
        ip_csv.write("2.57, ptile_Z - Z-value for quantile definining inundation curve\n")
        ip_csv.write("0.0058, B0 - beta-0 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("-0.00207, B1 - beta-1 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.0809, B2 - beta-2 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.0892, B3 - beta-3 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("-0.19, B4 - beta-4 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.835, ow_bd - bulk density of water bottoms (g/cm3)\n")
        ip_csv.write("0.076, om_k1 - organic matter self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
        ip_csv.write("2.106, mn_k2- mineral soil self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
        ip_csv.write("0, FIBS_intvals(1) - FFIBS score that will serve as lower end for Fresh forested\n")
        ip_csv.write("0.15, FIBS_intvals(2) - FFIBS score that will serve as lower end for Fresh marsh\n")
        ip_csv.write("1.5, FIBS_intvals(3) - FFIBS score that will serve as lower end for Intermediate marsh\n")
        ip_csv.write("5, FIBS_intvals(4) - FFIBS score that will serve as lower end for Brackish marsh\n")
        ip_csv.write("18, FIBS_intvals(5) - FFIBS score that will serve as lower end for Saline marsh\n")
        ip_csv.write("24, FIBS_intvals(6) - FFIBS score that will serve as upper end for Saline marsh\n")
        ip_csv.write("10, min_accretion_limit_cm - upper limit to allowable mineral accretion on the marsh surface during any given year [cm]\n")
        ip_csv.write("50, ow_accretion_limit_cm - upper limit to allowable accretion on the water bottom during any given year [cm]\n")
        ip_csv.write("-50, ow_erosion_limit_cm - upper limit to allowable erosion of the water bottom during any given year [cm]\n")
        ip_csv.write("0.05, bg_lowerZ_m - height that bareground is lowered [m]\n")
        ip_csv.write("0.25, me_lowerDepth_m - depth to which eroded marsh edge is lowered to [m]\n")
        ip_csv.write("1.0, flt_lowerDepth_m - depth to which dead floating marsh is lowered to [m]\n")
        ip_csv.write("%0.3f, mc_depth_threshold - default water depth threshold (meters) defining deep water area to be excluded from marsh creation projects footprint - this is replaced with project-specific fill depths if provided in the separate MC Project List input file\n" % mc_depth_threshold_def)
        ip_csv.write("1.1211425, spsal_params[1] - SAV parameter - spring salinity parameter 1\n")
        ip_csv.write("-0.7870841, spsal_params[2] - SAV parameter - spring salinity parameter 2\n")
        ip_csv.write("1.5059876, spsal_params[3] - SAV parameter - spring salinity parameter 3\n")
        ip_csv.write("3.4309696, sptss_params_params[1] - SAV parameter - spring TSS parameter 1\n")
        ip_csv.write("-0.8343315, sptss_params_params_params[2] - SAV parameter - TSS salinity parameter 2\n")
        ip_csv.write("0.9781167, sptss_params[3] - SAV parameter - spring TSS parameter 3\n")
        ip_csv.write("5.934377, dfl_params[1] - SAV parameter - distance from land parameter 1\n")
        ip_csv.write("-1.957326, dfl_params[2] - SAV parameter - distance from land parameter 2\n")
        ip_csv.write("1.258214, dfl_params[3] - SAV parameter - distance from land parameter 3\n")

        if year == startyear:
            ip_csv.write("0,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")
        else:
            ip_csv.write("1,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")

        ip_csv.write("1,binary_out - write raster datas to binary format only (1) or to ASCI XYZ files (0)\n")

        if year == startyear:
            ip_csv.write("'geomorph/input/%s_W_dem30.xyz', dem_file - file name with relative path to DEM XYZ file\n" % fwoa_init_cond_tag)
            ip_csv.write("'geomorph/input/%s_W_lndtyp30.xyz', lwf_file - file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n" % fwoa_init_cond_tag)
        else:
            ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_file - file name with relative path to DEM XYZ file\n" % file_prefix_prv)
            ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lwf_file - file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n" % file_prefix_prv)

           
        ip_csv.write("'geomorph/input/%s_W_meer30.xyz', meer_file - file name with relative path to marsh edge erosion rate file that is same resolution and structure as DEM XYZ\n" % fwoa_init_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_polder30.xyz', pldr_file - file name with relative path to polder file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_comp30.xyz', comp_file - file name with relative path to ICM-Hydro compartment map file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_grid30.xyz', grid_file - file name with relative path to ICM-LAVegMod grid map file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_dpsub30.xyz', dsub_file - file name with relative path to deep subsidence rate map file that is same resolution and structure as DEM XYZ (mm/yr; positive value\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/ecoregion_shallow_subsidence_mm.csv', ssub_file - file name with relative path to shallow subsidence table with statistics by ecoregion (mm/yr; positive values are for downward VLM)\n")
        ip_csv.write(" %d,ssub_col - column of shallow subsidence rates to use for current scenario (1=25th percentile; 2=50th percentile; 3=75th percentile)\n" % shallow_subsidence_column)
        ip_csv.write("'geomorph/input/%s', act_del_file - file name with relative path to lookup table that identifies whether an ICM-Hydro compartment is assigned as an active delta site\n" % act_del_file_2use)
        ip_csv.write("'geomorph/input/ecoregion_organic_matter_accum.csv', eco_omar_file - file name with relative path to lookup table of organic accumulation rates by marsh type/ecoregion\n")
        ip_csv.write("'geomorph/input/compartment_ecoregion.csv', comp_eco_file - file name with relative path to lookup table that assigns an ecoregion to each ICM-Hydro compartment\n")
        ip_csv.write("'geomorph/input/ecoregion_sav_priors.csv', sav_priors_file - file name with relative path to CSV containing parameters defining the periors (per basin) for the SAV statistical model\n")

        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro\n" % year)

        if year == startyear:
            ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year))
        else:
            ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year-1))

        ip_csv.write("'veg/%s_V_vegty.asc+', veg_out_file - file name with relative path to *vegty.asc+ file saved by ICM-LAVegMod\n" % file_oprefix)
        ip_csv.write("'%s', monthly_mean_stage_file - file name with relative path to compartment summary file with monthly mean water levels\n" % monthly_file_avstg)
        ip_csv.write("'%s', monthly_max_stage_file - file name with relative path to compartment summary file with monthly maximum water levels\n" % monthly_file_mxstg)
        ip_csv.write("'%s', monthly_ow_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition in open water\n" % monthly_file_sdowt)
        ip_csv.write("'%s', monthly_mi_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on interior marsh\n" % monthly_file_sdint)
        ip_csv.write("'%s', monthly_me_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on marsh edge\n" % monthly_file_sdedg)
        ip_csv.write("'%s', monthly_mean_sal_file - file name with relative path to compartment summary file with monthly mean salinity values\n" % monthly_file_avsal)
        ip_csv.write("'%s', monthly_mean_tss_file - file name with relative path to compartment summary file with monthly mean suspended sediment concentrations\n" % monthly_file_avtss)
        ip_csv.write("'%s', bi_dem_xyz_file - file name with relative path to XYZ DEM file for ICM-BI-DEM model domain - XY resolution must be snapped to XY resolution of main DEM\n" % bidem_xyz_file)
        ip_csv.write("'geomorph/input/%s_W_dem30_channels.xyz', dredge_dem_xyz_file - file name, with relative path, to XYZ DEM file for raster that will have elevations for all maintained/dredged channels/locations, these elevations will be maintained for every year regardless of calculated deposition/erosion rates\n" % exist_cond_tag)
        ip_csv.write("'geomorph/output/%s_W_edge30.xyz', edge_eoy_xyz_file - file name with relative path to XYZ raster output file for edge pixels\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_eoy_xyz_file - file name with relative path to XYZ raster output file for topobathy DEM\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dz30.xyz', dz_eoy_xyz_file - file name with relative path to XYZ raster output file for elevation change raster\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lndtyp_eoy_xyz_file - file name with relative path to XYZ raster output file for land type\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndchg30.xyz', lndchng_eoy_xyz_file - file name with relative path to XYZ raster output file for land change flag\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_salav30.xyz', salav_xyz_file - file name with relative path to XYZ raster output file for average salinity\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_salmx30.xyz', salmx_xyz_file - file name with relative path to XYZ raster output file for maximum salinity\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_inun30.xyz', inun_xyz_file - file name with relative path to XYZ raster output file for average inundation depth\n" % file_prefix)
        ip_csv.write("'geomorph/output/grid_summary_eoy_%d.csv', grid_summary_eoy_file - file name with relative path to summary grid file for end-of-year landscape\n" % year)
        ip_csv.write("'%s', grid_data_file - file name with relative path to summary grid data file used internally by ICM\n" % new_grid_filepath)
        ip_csv.write("'%s', grid_depth_file_Gdw - file name with relative path to Gadwall depth grid data file used internally by ICM and HSI\n" % grid_Gdw_dep_file)
        ip_csv.write("'%s', grid_depth_file_GwT - file name with relative path to Greenwing Teal depth grid data file used internally by ICM and HSI\n" % grid_GwT_dep_file)
        ip_csv.write("'%s', grid_depth_file_MtD - file name with relative path to Mottled Duck depth grid data file used internally by ICM and HSI\n" % grid_MtD_dep_file)
        ip_csv.write("'%s', grid_pct_edge_file - file name with relative path to percent edge grid data file used internally by ICM and HSI\n" % grid_pct_edge_file)
        ip_csv.write("'geomorph/output/%s_W_SAV.csv', grid_sav_file - file name with relative path to csv output file for SAV presence\n" % file_oprefix)
        ip_csv.write("'%s', comp_elev_file - file name with relative path to elevation summary compartment file used internally by ICM\n" % comp_elev_file)
        ip_csv.write("'%s', comp_wat_file - file name with relative path to percent water summary compartment file used internally by ICM\n" % comp_wat_file)
        ip_csv.write("'%s', comp_upl_file - file name with relative path to percent upland summary compartment file used internally by ICM\n" % comp_upl_file)
        ip_csv.write("%d, write_zonal_stats - integer flag to indicate whether zonal statistics are to be conducted in ICM-Morph (1) or whether a CSV file will be saved to do external zonal statistics(0)\n" % morph_zonal_stats)
        ip_csv.write("'%s',dem_grid_out_summary_file - file name, with relative path, to CSV output file that will save DEM-resolution landscape data to be used in zonal statistics\n" % dem_grid_data_outfile)
        ip_csv.write("2941, nqaqc - number of QAQC points for reporting - as listed in qaqc_site_list_file\n")
        ip_csv.write("'geomorph/output_qaqc/qaqc_site_list.csv', qaqc_site_list_file - file name, with relative path, to percent upland summary compartment file used internally by ICM\n")
        ip_csv.write(" %s, file naming convention prefix\n" % file_o_01_end_prefix)
        ip_csv.write(" %d, n_mc - number of marsh creation elements to be built in current year\n" % n_mc_yr)
        ip_csv.write("'%s', project_list_MC_file - file name with relative path to list of marsh creation raster XYZ files\n" % mc_project_list_yr)
        ip_csv.write("'%s', project_list_MC_VA_file - file name with relative path to file that will report out marsh creation volumes and footprint areas\n" % mc_project_list_VolArea_yr)
        ip_csv.write(" %d, n_rr - number of ridge or levee projects to  be built in current year\n" % n_rr_yr)
        ip_csv.write("'%s', project_list_RR_file - file name with relative path to list of ridge and levee raster XYZ files\n" % rr_project_list_yr)
        ip_csv.write(" %d, n_bs - number of bank stabilization projects built in current year OR PREVIOUS years\n" % n_sp_cumul)
        ip_csv.write("'%s', project_list_BS_file - file name with relative path to list of MEE rate multiplier XYZ files for current and all previous BS projects\n" % sp_project_list_cumul)
   
    morph_run = subprocess.call(morph_exe_path)