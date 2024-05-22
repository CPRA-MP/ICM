# sequentially numbers link and cell ids
# renumbering is default (probably objectID) but could be modified to use a particular field
#from mp29MN_functions import *
import os
import arcpy
# inputs
#username = 'tnelson'
#projectgdb = r'C:\Users\{}\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\TestDomain\TestDomainBasemapData.gdb'.format(username)
projectgdb = r'C:\Users\tnelson\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\TestDomain\TestDomainBasemapData.gdb'

links = os.path.join(projectgdb, 'links_testing') # existing cells shapefile to be modified
cells = os.path.join(projectgdb, 'cells_testing') # existing links shapefile to be modified
# todo add option to pull latest version from ftp based on the ftppull function

# variables to turn parts of the code on and off
#do_preversion = False # saves a backup copy before running
#if do_preversion:
#    vesiongdb = r'Q:\BR\221661-07\21 GIS\versions_linksandcells.gdb'
#    versionsuffix = '_20231117_test' # appended to name of links and cells in the versioned copy
do_renumber = True # turns on renumbering links and cells
do_linkUSDS = True # turns on determining upstream and downstream nodes in links

# input fields
field_ICMID = "ICM_ID"
field_USnode = 'USnode_ICM'
field_DSnode = 'DSnode_ICM'
#field_orderfield = "'OID@'" # IDs are renumbered sequentially based on the order in this field

# env
arcpy.env.workspace = projectgdb
arcpy.env.overwriteOutput = True

# script specific functions, more generic functions are in mp29MN_functions
def renumber_ids(feature_class, id_field):
    new_id = 1 # first new id is 1
    with arcpy.da.UpdateCursor(feature_class, [id_field]) as cursor:
        for row in cursor:
            row[0] = new_id
            new_id += 1 # next is 2
            cursor.updateRow(row)

# version on Q before making changes
#if do_preversion:
#    preversion(links, vesiongdb, os.path.basename(links), versionsuffix)
#    preversion(cells, vesiongdb, os.path.basename(cells), versionsuffix)

# renumber cells
newID = 1
if do_renumber:
    print('Renumbering cells')
    renumber_ids(cells, field_ICMID)
    # Reset counter for links
    print('Renumbering links')
    renumber_ids(links, field_ICMID)

# update upstream and downstream nodes
if do_linkUSDS:
    print('Assigning US/DS attributes')
    spatial_reference = arcpy.Describe(cells).spatialReference
    # dictionary to map object ids to start/end ICMIDs
    line_icmid_mapping = {}
    # find start and end ICMIDs from polygons
    with arcpy.da.UpdateCursor(links, [field_ICMID, "SHAPE@", field_USnode, field_DSnode]) as link_cursor:
        for link_row in link_cursor:
            link_id, link_geometry, us_node, ds_node = link_row
            line_start_point = link_geometry.firstPoint
            line_end_point = link_geometry.lastPoint
            # todo add print for if points arent in a cell
            with arcpy.da.SearchCursor(cells, [field_ICMID, "SHAPE@"], spatial_reference=spatial_reference) as cell_cursor:
                for cell_row in cell_cursor:
                    cell_icmid, cell_geometry = cell_row
                    if cell_geometry.contains(line_start_point):
                        us_node = cell_icmid
                    if cell_geometry.contains(line_end_point):
                        ds_node = cell_icmid
            # update the line's USnode_ICM and DSnode_ICM fields
            link_row[2] = us_node
            link_row[3] = ds_node
            link_cursor.updateRow(link_row)
print('Done')