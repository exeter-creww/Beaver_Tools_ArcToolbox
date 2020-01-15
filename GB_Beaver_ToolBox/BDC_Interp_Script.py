########################################################################################################################
########################################################################################################################
# --- Title: Beaver Dam Capacity(BDC) Interpretation (BDC) Tool Script.
# --- Description: This Script is part of the BeaverMod_ToolBox. The script's purpose is to calculate statistics from
#                  the BDC datasets produced for Great Britain. The paths to all BDC regions of interest must be
#                  provided along with an ESRI featureclass or shapefile containing features that define the zones for
#                  which summary statistics are required.
# --- Authors: Hugh Graham, Alan Puttock and Richard Brazier (May, 2019)
########################################################################################################################
########################################################################################################################

import sys
import arcpy
import os
import numpy as np
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")


def main(bdc_nets, s_zone, zones_out):
    scratchPath = os.path.abspath(os.path.join(__file__, os.pardir))
    scratchName = "scratch.gdb"
    scratch = os.path.join(scratchPath, scratchName)

    if arcpy.Exists(scratch):
        print("scratch gdb exists - Deleting")
        arcpy.Delete_management(scratch) # turned off for testing

    arcpy.CreateFileGDB_management(scratchPath, scratchName)

    if arcpy.Exists(zones_out):
        arcpy.Delete_management(zones_out)

    bdc_copy = os.path.join(scratch, "bdc_copy")
    if len(bdc_nets) > 1:
        print("merging bdc files")
        arcpy.Merge_management(bdc_nets, bdc_copy)
    elif len(bdc_nets) == 1:
        arcpy.CopyFeatures_management(bdc_nets[0], bdc_copy)
    else:
        print("no bdc features supplied") # also worth raising error here perhaps????

    # arcpy.AddField_management(bdc_copy, field_name="BDC_CAT", field_type="SHORT")
    # print("Running BHI Stand Alone Script")

    # classifying_zones
    sZone_fields = [f.name for f in arcpy.ListFields(s_zone)]
    if "Zone_no" in sZone_fields:
        arcpy.DeleteField_management(s_zone, "Zone_no")

    zone_info = os.path.join(scratch, "tmp_shp_copy")
    arcpy.CopyFeatures_management(s_zone, zone_info)

    # create sequential numbers for reaches
    arcpy.AddField_management(zone_info, "Zone_no", "LONG")

    with arcpy.da.UpdateCursor(zone_info, ["Zone_no", 'OBJECTID']) as cursor:
        for row in cursor:
            row[0] = row[1]

            cursor.updateRow(row)

    arcpy.AddField_management(zone_info, field_name="BDC_MEAN", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_W_AVG", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_TOT", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_MIN", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_MAX", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_STD", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_W_STD", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_P_NONE", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_P_RARE", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_P_OCC", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_P_FREQ", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_P_PERV", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_km_NONE", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_km_RARE", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_km_OCC", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_km_FREQ", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="BDC_km_PERV", field_type="DOUBLE")
    arcpy.AddField_management(zone_info, field_name="TOT_km", field_type="DOUBLE")

    sz_fl = arcpy.MakeFeatureLayer_management(zone_info, "tempFL", "", r"in_memory")

    n_feat = arcpy.GetCount_management(sz_fl)

    tmp_table = os.path.join(r"in_memory", "temp_table")

    with arcpy.da.SearchCursor(sz_fl, ["Zone_no"]) as cursor:
        for row in cursor:
            arcpy.AddMessage("working on feature {0}/{1}".format(row[0], n_feat))

            expr = """{0} = {1}""".format('Zone_no', row[0])
            arcpy.SelectLayerByAttribute_management(sz_fl,
                                                    "NEW_SELECTION",
                                                    expr)
            out_shp = os.path.join(scratch, "op{0}".format(row[0]))

            arcpy.CopyFeatures_management(sz_fl, out_shp)
            tempshp = r"in_memory/tempshp"
            # tempshp = os.path.join(scratch, "tempshp")  # SHALL WE GO WITH GDB SAVES OR IN-MEMORY... HMMM

            arcpy.Clip_analysis(bdc_copy, out_shp, tempshp)

            arcpy.AddMessage("converting bdc network to numpy array")
            # bdc_arr = arcpy.da.FeatureClassToNumPyArray(tempshp, ("BDC", "SHAPE@LENGTH"))
            bdcVal_arr = arcpy.da.FeatureClassToNumPyArray(tempshp, "BDC").astype(np.float)
            if bdcVal_arr.size > 0:
                lenVal_arr = arcpy.da.FeatureClassToNumPyArray(tempshp,  "SHAPE@LENGTH").astype(np.float)

                arcpy.AddMessage("retrieving statistics from array")
                total_length = np.sum(lenVal_arr)
                no_cap_length = np.sum(lenVal_arr[bdcVal_arr <= 0])
                rare_cap_length = np.sum(lenVal_arr[(bdcVal_arr > 0) & (bdcVal_arr <= 1)])
                occ_cap_length = np.sum(lenVal_arr[(bdcVal_arr > 1) & (bdcVal_arr <= 4)])
                freq_cap_length = np.sum(lenVal_arr[(bdcVal_arr > 4) & (bdcVal_arr <= 15)])
                perv_cap_length = np.sum(lenVal_arr[bdcVal_arr > 15])


                # weigh_arr = bdcVal_arr * lenVal_arr
                # weigh_avg = np.sum(weigh_arr)/total_length
                #standard stats
                bdc_mean = np.mean(bdcVal_arr)
                bdc_std = np.std(bdcVal_arr)
                bdc_max = np.max(bdcVal_arr)
                bdc_min = np.min(bdcVal_arr)
                bdc_tot = np.sum(bdcVal_arr)

                # weighted stats
                bdc_w_avg = np.average(bdcVal_arr, weights=lenVal_arr) # weighted average
                bdc_variance = np.average((bdcVal_arr - bdc_w_avg) ** 2, weights=lenVal_arr)  # weighted  variance and stDev
                bdc_w_std = np.sqrt(bdc_variance)
                arcpy.AddMessage("assigning bdc values to area shape file")

                with arcpy.da.UpdateCursor(out_shp, ["BDC_MEAN", "BDC_W_AVG", "BDC_TOT", "BDC_MIN", "BDC_MAX","BDC_STD",
                                                     "BDC_W_STD", "BDC_P_NONE", "BDC_P_RARE", "BDC_P_OCC", "BDC_P_FREQ",
                                                     "BDC_P_PERV", "BDC_km_NONE", "BDC_km_RARE", "BDC_km_OCC",
                                                     "BDC_km_FREQ", "BDC_km_PERV", "TOT_km"]) as cursord:
                    for rowd in cursord:
                        rowd[0] = round(float(bdc_mean), 2)
                        rowd[1] = round(float(bdc_w_avg), 2)
                        rowd[2] = round(float(bdc_tot), 2)
                        rowd[3] = round(float(bdc_min), 2)
                        rowd[4] = round(float(bdc_max), 2)
                        rowd[5] = round(float(bdc_std), 2)
                        rowd[6] = round(float(bdc_w_std), 2)
                        rowd[7] = round(float((no_cap_length/total_length) * 100), 2)
                        rowd[8] = round(float((rare_cap_length/total_length) * 100), 2)
                        rowd[9] = round(float((occ_cap_length/total_length) * 100), 2)
                        rowd[10] = round(float((freq_cap_length/total_length) * 100), 2)
                        rowd[11] = round(float((perv_cap_length/total_length) * 100), 2)
                        rowd[12] = round(float(no_cap_length/1000), 2)
                        rowd[13] = round(float(rare_cap_length/1000), 2)
                        rowd[14] = round(float(occ_cap_length/1000), 2)
                        rowd[15] = round(float(freq_cap_length/1000), 2)
                        rowd[16] = round(float(perv_cap_length/1000), 2)
                        rowd[17] = round(float(total_length/1000), 2)

                        cursord.updateRow(rowd)
            else:
                with arcpy.da.UpdateCursor(out_shp,
                                           ["BDC_MEAN", "BDC_W_AVG", "BDC_TOT", "BDC_MIN", "BDC_MAX", "BDC_STD",
                                            "BDC_W_STD", "BDC_P_NONE", "BDC_P_RARE", "BDC_P_OCC", "BDC_P_FREQ",
                                            "BDC_P_PERV", "BDC_km_NONE", "BDC_km_RARE", "BDC_km_OCC",
                                            "BDC_km_FREQ", "BDC_km_PERV", "TOT_km"]) as cursord:
                    for rowd in cursord:
                        rowd[0] = 0
                        rowd[1] = 0
                        rowd[2] = 0
                        rowd[3] = 0
                        rowd[4] = 0
                        rowd[5] = 0
                        rowd[6] = 0
                        rowd[7] = 0
                        rowd[8] = 0
                        rowd[9] = 0
                        rowd[10] = 0
                        rowd[11] = 0
                        rowd[12] = 0
                        rowd[13] = 0
                        rowd[14] = 0
                        rowd[15] = 0
                        rowd[16] = 0
                        rowd[17] = 0

                        cursord.updateRow(rowd)

    zones_list = []

    if arcpy.Exists(tempshp):
        arcpy.Delete_management(zone_info)

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
