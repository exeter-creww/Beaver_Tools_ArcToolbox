# -*- coding: utf-8 -*-

import arcpy
import BHI_Interp_Script
import BHI_StAl_Script
import BDC_Interp_Script
import os
arcpy.env.overwriteOutput = True

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Beaver ToolBox"
        self.alias = "Beaver ToolBox"

        # List of tool classes associated with this toolbox
        self.tools = [BHI_Tool, BHI_Tool_StandAlone, BDC_Tool]

class BHI_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Beaver Habitat Toolbox"
        self.description = "A tool for facilitating the interpretation of The Beaver Habitat Index (BHI)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Input BHI Raster",
            name="bhi_ras",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        #param0.filter.list = ['RASTER'] # need to double check this...

        param1 = arcpy.Parameter(
            displayName="Input Search Zones",
            name="s_zone",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ['Polygon']

        param2 = arcpy.Parameter(
            displayName="Output Summary Polygon",
            name="zones_out",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        param2.filter.list = ['Polygon']
        # param2.symbology = os.path.join(os.path.dirname(__file__), "bhiInt_vis.lyr")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, params, messages):
        """The source code of the tool."""
        BHI_Interp_Script.main(params[0].valueAsText,
                  params[1].valueAsText,
                  params[2].valueAsText)
        return
class BHI_Tool_StandAlone(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Beaver Habitat Stand Alone Toolbox"
        self.description = "A tool for facilitating the interpretation of The Beaver Habitat Index (BHI)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Input BHI Raster Workspace",
            name="bhi_home",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        # param0.filter.list = ["File System"]
        # param0.filter.list = ["Local Database"]

        param1 = arcpy.Parameter(
            displayName="Input Search Zones",
            name="s_zone",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ['Polygon']

        param2 = arcpy.Parameter(
            displayName="Output Summary Polygon",
            name="zones_out",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        param2.filter.list = ['Polygon']
        # param2.symbology = os.path.join(os.path.dirname(__file__), "bhiInt_vis.lyr")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, params, messages):
        """The source code of the tool."""
        BHI_StAl_Script.main(params[0].valueAsText,
                  params[1].valueAsText,
                  params[2].valueAsText)
        return

class BDC_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Beaver Dam Capacity Toolbox"
        self.description = "A tool for facilitating the interpretation of The Beaver Dam Capacity (BDC)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Input BDC Network(s)",
            name="bdc_nets",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue = True)
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Input Search Zones",
            name="s_zone",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ['Polygon']

        param2 = arcpy.Parameter(
            displayName="Output Summary Polygon",
            name="zones_out",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        param2.filter.list = ['Polygon']
        # param2.symbology = os.path.join(os.path.dirname(__file__), "bdcInt_vis.lyr")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, params, messages):
        """The source code of the tool."""
        BDC_Interp_Script.main(params[0].valueAsText,
                  params[1].valueAsText,
                  params[2].valueAsText)
        return
