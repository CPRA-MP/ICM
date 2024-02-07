#ICM imports


#Python imports


def ICMVars():
    #Years to implement new files for hydro model
    hyd_switch_years = []
    hyd_file_orig = []
    hyd_file_new = []
    hyd_file_bk = []

    # Link numbers to be activated or deactivated in Hydro model
    links_to_change = []
    # Years (calendar year) to activate or deactivate each respective Hydro model links listed above
    link_years = []

    # full path to directory with FWA project GIS data files
    FWA_prj_input_dir_MC = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/MC_elev_rasters'
    FWA_prj_input_dir_RR = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/Ridge_Levee_elev_rasters'
    FWA_prj_input_dir_BS = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/BS_SP_edge_erosion_multiplier_rasters'

    # Marsh creation project element IDs that are implemented in this simulation
    mc_elementIDs = []
    # Years (calendar year) to implement each respective marsh creation element IDs listed above
    mc_years = []
    # Marsh creation project element IDs that have deep water areas filled in (leave array empty if all use default shallow water fill threshold)
    mc_eid_with_deep_fill = []
    mc_depth_threshold_def = 0.762
    mc_depth_threshold_deep = 9999.999


    # link ID numbers for 'composite' marsh flow links (type 11) that need to be updated due to marsh creation projects
    mc_links = []
    # Years (calendar year) to update each respective'composite' marsh flow links (type 11) for marsh creation projects - this value should be the year after the project is implemented in the morphology model
    mc_links_years = []

    # Shoreline protection project IDs that are implemented in this simulation
    sp_projectIDs = []
    # Years (calendar year) to implement each respective shoreline protection project listed above
    sp_years = []

    # Levee and ridge project IDs that are implemented in this simulation
    rr_projectIDs = []
    # Years (calendar year) to implement each respective levee and ridge restoration project listed above
    rr_years = []

    # Compartment numbers to have new bed elevations assigned (e.g. dredging)
    comps_to_change_elev = []
    # New bed elevation for compartments that will be updated for dredging
    comp_elevs = []
    # Years (calendar year) when compartments will have new elevations updated
    comp_years = []

    # Active deltaic compartment file names that are used by ICM-Morph (all files must be saved in S##/G###/geomorph/input directory)
    act_del_files = []
    # Years (calendar year) to implement each respective active deltaic compartment file listed above
    act_del_years = []

    return (hyd_switch_years, hyd_file_orig, hyd_file_new, hyd_file_bk, links_to_change, link_years, \
            FWA_prj_input_dir_MC, FWA_prj_input_dir_RR, FWA_prj_input_dir_BS, mc_elementIDs, mc_years, \
            mc_eid_with_deep_fill, mc_depth_threshold_def, mc_depth_threshold_deep, mc_links, mc_links_years, \
            sp_projectIDs, sp_years, rr_projectIDs, rr_years, comps_to_change_elev, comp_elevs, comp_years, \
            act_del_files, act_del_years)


    