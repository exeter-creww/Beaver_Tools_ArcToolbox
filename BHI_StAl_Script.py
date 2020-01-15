########################################################################################################################
########################################################################################################################
# --- Title: Beaver Habitat Index (BHI) Stand Alone Tool Script.
# --- Description: This Script is part of the BeaverMod_ToolBox. The script's purpose is to calculate statistics from
#                  the Beaver Habitat Index for Great Britain. This Stand Alone tool requires the full GB dataset
#                  to be loaded locally. The path to the National BHI data must be provided along with an
#                  ESRI featureclass or shapefile containing features that define the zones for which summary
#                  statistics are required.
# --- Authors: Hugh Graham, Alan Puttock and Richard Brazier (May, 2019)
########################################################################################################################
########################################################################################################################

import sys
import arcpy
import os
from arcpy.sa import *
import numpy as np
arcpy.env.overwriteOutput = True
arcpy.env.scratchWorkspace = r"in_memory"

arcpy.CheckOutExtension("Spatial")


# def main():
#     bhi_home = os.path.abspath("D:/Work/GB_Beaver_Data/Beaver_Mod_Data_NE_EA_fin/GB_BHI_BVI\BHI_5m")
#     s_zone = os.path.abspath("C:/Users/hughg/Desktop/Beaver_Workshop/BHI_BDC_Demo/Shp_Files/WholeEstate.shp")
#     zones_out = os.path.abspath("C:/Users/hughg/Desktop/Beaver_Workshop/BHI_BDC_Demo/ToolBoxResults/WholeEstateTB_Out_am2.shp")

def main(bhi_home, s_zone, zones_out):

    scratchPath = os.path.abspath(os.path.join(__file__, os.pardir))
    scratchName = "scratch.gdb"
    scratch = os.path.join(scratchPath, scratchName)
    if arcpy.Exists(scratch):

        arcpy.AddMessage("scratch gdb exists - Deleting")
        arcpy.Delete_management(scratch)

    arcpy.CreateFileGDB_management(scratchPath, scratchName)

    if arcpy.Exists(zones_out):
        arcpy.Delete_management(zones_out)

    arcpy.AddMessage("Running BHI Stand Alone Script")

    p = os.path.abspath(os.path.join(__file__, os.pardir))
    osGrid = os.path.join(p, "OsGridShp", "OSGB_Grid_100km.shp")

    # classifying_zones
    sZone_fields = [f.name for f in arcpy.ListFields(s_zone)]
    if "Zone_no" in sZone_fields:
        arcpy.DeleteField_management(s_zone, "Zone_no")

    zone_info = os.path.join(scratch, "tmp_shp_copy")
    if arcpy.Exists(zone_info):
        arcpy.Delete_management(zone_info)
    arcpy.CopyFeatures_management(s_zone, zone_info)

    # create sequential numbers for reaches
    arcpy.AddField_management(zone_info, "Zone_no", "LONG")

    with arcpy.da.UpdateCursor(zone_info, ["Zone_no", 'OBJECTID']) as cursor:
        for row in cursor:
            row[0] = row[1]

            cursor.updateRow(row)


    arcpy.AddField_management(zone_info, field_name="BHI_MEAN", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_MIN", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_MAX", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_STD", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_0", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_1", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_2", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_3", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_4", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_PERC_5", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_0", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_1", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_2", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_3", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_4", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BHI_AREA_5", field_type="DOUBLE")

    arcpy.AddGeometryAttributes_management(zone_info, Geometry_Properties="AREA", Area_Unit="SQUARE_KILOMETERS")

    arcpy.AddMessage("begin looping features...")
    sz_fl = arcpy.MakeFeatureLayer_management(zone_info, "tempFL", "", scratch)

    n_feat = arcpy.GetCount_management(sz_fl)

    arcpy.env.workspace = bhi_home
    bhi_list = arcpy.ListRasters("*", "ALL")

    with arcpy.da.SearchCursor(sz_fl, ["Zone_no"]) as cursor:
        for row in cursor:

            # print("working on feature {0}/{1}".format(row[0], n_feat))
            arcpy.AddMessage("working on feature {0}/{1}".format(row[0], n_feat))
            expr = """{0} = {1}""".format('Zone_no', row[0])
            arcpy.SelectLayerByAttribute_management(sz_fl,
                                                    "NEW_SELECTION",
                                                    expr)
            out_shp = os.path.join(scratch, "op{0}".format(row[0]))

            arcpy.CopyFeatures_management(sz_fl, out_shp)

            tempshp = r"in_memory/tempshp"
            if arcpy.Exists(tempshp):
                arcpy.Delete_management(tempshp)

            arcpy.Clip_analysis(osGrid, sz_fl, tempshp)

            with arcpy.da.SearchCursor(tempshp, ["TILE_NAME"]) as cursorb:
                gridList = sorted({rowb[0] for rowb in cursorb})

            ras_selec = []

            for ras in bhi_list:
                if ras[:2] in gridList:
                    ras_selec.append(ras)
            ras_selecN = [os.path.join(bhi_home, s) for s in ras_selec]

            if len(ras_selec) > 1:
                arcpy.AddMessage("feature intersects multiple OS tiles - merging rasters")
                bhi_ras = arcpy.MosaicToNewRaster_management(ras_selecN, scratch, "tempRas", number_of_bands=1)
            else:
                arcpy.AddMessage("feature intersects only one OS tile - skip merge")
                bhi_ras = arcpy.CopyRaster_management(ras_selec[0], os.path.join(scratch, "tempRas"))

            xcell = arcpy.GetRasterProperties_management(bhi_ras, property_type="CELLSIZEX").getOutput(0)
            area_ras = r"in_memory/area_ras_temp"
            arcpy.env.snapRaster = os.path.join(scratch, "tempRas")
            arcpy.FeatureToRaster_conversion(out_shp, field="Zone_no", out_raster=area_ras, cell_size=xcell)

            ebm_ras = Con(IsNull(Raster(area_ras)), -100, Raster(bhi_ras))

            ebm_ras = SetNull(ebm_ras == -100, ebm_ras)

            area_ras = None
            bhi_ras = None

            #arcpy alternative:
            stdVal = arcpy.GetRasterProperties_management(ebm_ras, property_type="STD").getOutput(0)
            meanVal = arcpy.GetRasterProperties_management(ebm_ras, property_type="MEAN").getOutput(0)
            minVal = arcpy.GetRasterProperties_management(ebm_ras, property_type="MINIMUM").getOutput(0)
            maxVal = arcpy.GetRasterProperties_management(ebm_ras, property_type="MAXIMUM").getOutput(0)

            histtab = os.path.join(scratch, "histtab")

            ZonalHistogram(out_shp, "Zone_no", ebm_ras, histtab)
            field_names = [f.name for f in arcpy.ListFields(histtab)]

            tab_arr = list(arcpy.da.TableToNumPyArray(histtab, field_names=field_names))

            arr = np.asarray([x[1] for x in tab_arr])
            arrb = np.asarray([x[2] for x in tab_arr])
            # arr = tab_arr['LABEL']
            # arrb = tab_arr['OBJEC_1']

            namesList = list(arr)

            if '0' in namesList:
                n0 = int(arrb[arr == '0'])
            else:
                n0 = 0
            if '1' in namesList:
                n1 = int(arrb[arr == '1'])
            else:
                n1 = 0
            if '2' in namesList:
                n2 = int(arrb[arr == '2'])
            else:
                n2 = 0
            if '3' in namesList:
                n3 = int(arrb[arr == '3'])
            else:
                n3 = 0
            if '4' in namesList:
                n4 = int(arrb[arr == '4'])
            else:
                n4 = 0
            if '5' in namesList:
                n5 = int(arrb[arr == '5'])
            else:
                n5 = 0

            print(n0, n1, n2, n3, n4, n5)

            countN = sum([n0, n1, n2, n3, n4, n5])

            p0 = round(float(n0)/countN*100, 2)
            p1 = round(float(n1)/countN*100, 2)
            p2 = round(float(n2)/countN*100, 2)
            p3 = round(float(n3)/countN*100, 2)
            p4 = round(float(n4)/countN*100, 2)
            p5 = round(float(n5)/countN*100, 2)

            print(p0, p1, p2, p3, p4, p5)

            with arcpy.da.UpdateCursor(out_shp, ["BHI_MEAN", "BHI_MIN", "BHI_MAX",
                                                 "BHI_STD", "BHI_PERC_0","BHI_PERC_1",
                                                 "BHI_PERC_2", "BHI_PERC_3", "BHI_PERC_4", "BHI_PERC_5",
                                                 "BHI_AREA_0", "BHI_AREA_1", "BHI_AREA_2", "BHI_AREA_3",
                                                 "BHI_AREA_4", "BHI_AREA_5", "SHAPE_AREA"]) as cursorc:  # NEED TO CHECK COL NAME OF AREA.
                for rowc in cursorc:
                    rowc[0] = meanVal
                    rowc[1] = minVal
                    rowc[2] = maxVal
                    rowc[3] = stdVal
                    rowc[4] = p0
                    rowc[5] = p1
                    rowc[6] = p2
                    rowc[7] = p3
                    rowc[8] = p4
                    rowc[9] = p5
                    rowc[10] = round((rowc[16]/100 * p0)/1000000, 2)
                    rowc[11] = round((rowc[16]/100 * p1)/1000000, 2)
                    rowc[12] = round((rowc[16]/100 * p2)/1000000, 2)
                    rowc[13] = round((rowc[16]/100 * p3)/1000000, 2)
                    rowc[14] = round((rowc[16]/100 * p4)/1000000, 2)
                    rowc[15] = round((rowc[16]/100 * p5)/1000000, 2)

                    cursorc.updateRow(rowc)
            arcpy.Delete_management(r"in_memory")

    if arcpy.Exists(zone_info):
        arcpy.Delete_management(zone_info)
    if arcpy.Exists(sz_fl):
        arcpy.Delete_management(zone_info)

    if arcpy.Exists(os.path.join(scratch, "histtab")):
        arcpy.Delete_management(os.path.join(scratch, "histtab"))

    if arcpy.Exists(os.path.join(scratch, "tempRas")):
        arcpy.Delete_management(os.path.join(scratch, "tempRas"))

    zones_list = []

    walk = arcpy.da.Walk(scratch, datatype="FeatureClass", type="Polygon")

    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            zones_list.append(os.path.join(dirpath, filename))

    if len(zones_list) > 1:
        arcpy.AddMessage("merging final features")
        arcpy.Merge_management(zones_list, zones_out)
    else:
        arcpy.AddMessage("copying final features")
        arcpy.CopyFeatures_management(zones_list[0], zones_out)

    for fc in zones_list:
        arcpy.Delete_management(fc)

    if arcpy.Exists(scratch):
        try:
            arcpy.Delete_management(scratch)
        except Exception:
            print("An issue occured when deleting the scratch folder - not a big deal")

    arcpy.Delete_management(r"in_memory")

    arcpy.AddMessage("Tool completed")


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3])


