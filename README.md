# GB Beaver Tools ArcToolbox
A Repository Containing an Arc Toolbox (>Arc10 and ArcPro compatible) to help investigate the results of the Beaver 
Habitat Index Model and Beaver Dam Capacity Model (Graham, et al. (in review) and Macfarlane, et al. (2015). These tools were developed for the 
Environment Agency and Natural England as part of a national beaver habitat and regional dam capacity modelling project.

#### Model Descriptions
#####The Beaver Habitat index: 
A raster dataset which provides an integer value between 0-5, at a resolution of 5m, which describes the suitability of
the vegetaion/landuse type for beaver forage.

#####Beaver Dam Capacity Model
A vector dataset of a river network that describes the reach scale (~130m) capacity to support dams. Dam capacity is 
provided as 0-30 dams/km.

##Arc Tool Box *(BeaverMod_ToolBox.pyt)*
This repository contains an Arc tool ([*BeaverMod_ToolBox.pyt*](GB_Beaver_ToolBox/BeaverMod_ToolBox.pyt)) box which 
contains 3 tools:

#####1) Beaver Dam Capacity Toolbox ([*BDC_Interp_Script.py*](GB_Beaver_ToolBox/BDC_Interp_Script.py))
Returns summary statistics, for defined search areas, of BDC model results

#####2) Beaver Habitat Toolbox ([*BHI_Interp_Script.py*](GB_Beaver_ToolBox/BHI_Interp_Script.py))
Returns summary statistics, for defined search areas, of BHI model results.

#####3) Beaver Habitat Stand Alone Toolbox ([*BHI_StAl_Script.py*](GB_Beaver_ToolBox/BHI_StAl_Script.py))
Returns summary statistics, for defined search areas, of BHI model results as in te Beaver Habitat Toolbox. However, 
this tool requires the full England BHI dataset to be loaded to disk. it then automatically locates the required raster 
tiles to analyse. Gives the same results as the Beaver Habitat Toolbox but requires no pre-processing of raster data. 
Slightly slower than Beaver Habitat Toolbox.


## Tool Box Demo...

* Download This Repo 
([*https://github.com/exeter-creww/Beaver_Tools_ArcToolbox*](https://github.com/exeter-creww/Beaver_Tools_ArcToolbox)):

![download_repo](demo_files/download_repo.PNG=100x100)

<img src=".demo_files/download_repo.PNG" alt="" width="100"/>