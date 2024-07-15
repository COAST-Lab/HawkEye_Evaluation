# Integrating In-Situ Measurements and Satellite Imagery for Coastal Biogeochemical Analysis in the Cape Fear River Estuary

## Introduction
This project at UNCW evaluates the efficacy of the HawkEye satellite sensor in capturing ocean color (OC) imagery, specifically focusing on the Cape Fear River Estuary (CFRE) in southeastern North Carolina. Coastal and estuarine environments, which are vital for biodiversity and local economies, present unique challenges for remote sensing due to their optically complex waters. This research involves detailed comparisons of in-situ measurements with data from HawkEye and other satellite sensors to refine and enhance marine conservation and management strategies.

![Study Site](assets/img/studysite_mosaic_presentation.png)  
*Sampling overview of the Cape Fear River Estuary and Masonboro Inlet Area we collected in-situ water quality measurements with the R/V Cape Fear (transect lines) and where we acquired satellite-derived measurements.*

## Objectives
1.	**In-Situ Data Collection**: Use the Sea Sciences Acrobat to collect three-dimensional spatial data on conductivity, CDOM, salinity, Chl a, turbidity, dissolved oxygen, density, and temperature.
2. **Synchronized Satellite Data Collection**: Analyze OC imagery from SeaHawk-HawkEye, Aqua-MODIS, Sentinel 3A/3B-OLCI to study Chl a variations in the Cape Fear River Estuary, correlating with in-situ data from R/V Cape Fear cruises.
3. **Water Quality Evaluation**: Evaluate spatial and temporal variations of salinity, density, turbidity, temperature, Chl a, and dissolved oxygen using in-situ measurements from the Acrobat.
4. **Matchup Analysis**: Perform a matchup analysis between satellite-derived and in-situ Chl a concentrations using R2, RMSE, MAPE, and Bias to understand discrepancies and systematic differences.
5. **Multi-Sensor Strategy**: Highlight the importance of integrating high-resolution satellites and in-situ instruments to better understand coastal dynamics, acknowledging the limitations of relying on a single measurement tool.


## Methodology
Our approach leverages a multi-sensor strategy that combines surface-level satellite imagery with in-situ chlorophyll a measurements collected with the Acrobat, which is capable of vertical water column profiling. Satellite imagery from SeaHawk-HawkEye, Aqua-MODIS, and Sentinel 3A/3B-OLCI were analyzed for overlapping temporal and spatial coverage with field data. This integration allows us to assess the accuracy and utility of satellite sensors in estimating chlorophyll a concentrations in the coastal Cape Fear region, crucial for understanding estuarine primary productivity dynamics.

![Satellite-derived chl mosaic](assets/img/mosaic_masonboro_chl_single.jpg)  
*Satellite-derived Chl a concentration in the study region for each sensor type on May 7, 2023. Parallel red lines indicate the path of in-situ data collection. A) Aqua-MODIS, B) SeaHawk-HawkEye, C) S3A-OLCI, D) S3B-OLCI.*

Utilizing a 3D in-situ dataset for satellite matchup analysis enhances satellite analysis since satellite sensors often provide a surface-level perspective, limiting the understanding of vertical variations within water bodies. Our 3D approach captures data across different depths, providing a comprehensive view essential for accurately interpreting satellite imagery. This depth-resolved data enables enhanced calibration and validation of satellite sensors, leading to improved accuracy in mapping and monitoring aquatic environments. The 3D dataset aids in understanding the spatial distribution of water quality parameters and supports the development of models predicting ecological changes within these complex systems.

![In-Situ Chl a](/assets/img/chl.gif)  
*In-situ Chl a concentration along the 7 transects, collected using the Acrobat instrument on May 5, 2023.*

## Preliminary Results
During the study period from May 5 to May 7, we observed variations in environmental factors like wind speed, Chl a concentration, and tidal changes. These factors influenced water quality metrics, highlighting the dynamic nature of the study area. Our in-situ data collection revealed detailed profiles of various water quality parameters, including chlorophyll a, turbidity, temperature, salinity, density, and dissolved oxygen. We observed increasing Chl a concentrations from transect 1 to transect 7 and with depth. Temperature showed a slight thermal divide with depth, while density, salinity, turbidity, and dissolved oxygen displayed minor variations. 

The analysis of satellite imagery provided a comprehensive view of the study site. The SeaHawk-HawkEye sensor offered high spatial resolution, revealing detailed patterns in water quality parameters. Our matchup analysis showed notable discrepancies between in-situ and satellite-derived Chl a data, primarily due to differences in sensor resolution, environmental variability, and the temporal gap between data acquisition between in-situ and satellite-derived datasets. Low R-squared scores indicate poor model fit between the sensors, suggesting the water column had significantly changed over the 48-hour window.

![Satellite and In-Situ Matchup Statistical Metric Comparison](assets/img/bar-plots.jpg)
*Statistical metric comparison across satellite sensor types at different in-situ depth ranges for 1x1 pixel size windows.*

## Research Findings
The integration of in-situ measurements with satellite imagery revealed several key findings:
- **Three-Dimensional Phytoplankton Plumes**: The detection of three-dimensional phytoplankton plumes showcases the effective integration of in-situ and satellite data.
- **Data Discrepancies**: Notable discrepancies between in-situ and satellite-derived chlorophyll-a data were observed, attributed to differences in sensor resolution, atmospheric correction effectiveness, vertical heterogeneity in the water column, and proximity to land/benthos.
- **Enhanced Accuracy**: The multi-sensor strategy proved crucial in providing a more comprehensive understanding of coastal dynamics, demonstrating variability and complexity in coastal water quality monitoring.

## Implications and Future Work
The preliminary findings from this study underscore the potential of advanced satellite sensors like HawkEye in improving our understanding of complex coastal waters. By providing more accurate and timely data, HawkEye can significantly aid in the management and conservation of aquatic resources. Ongoing research will focus on further integrating these insights into broader marine management practices and continuing to validate and refine our findings.

## Contact
Mitchell D. Torkelson  
University of North Carolina Wilmington  
Center for Marine Science  
[COAST Lab Graduate Researcher](https://coast-lab.org/MitchTorkelson/)  
**Email:** [mdt3971@uncw.edu](mailto:mdt3971@uncw.edu)  
**Portfolio:** [Mitch Torkelson's Research](https://dinodiver.github.io/mitchtorkelson/)

## Acknowledgements

We thank the Gordon and Betty Moore Foundation for funding this project. We also extend our gratitude to UNCW’s Center for Marine Science, particularly Dave Wells for dock maintenance and data collection support, and Bruce Monger for his technical support and expertise in satellite image processing and analysis. Special thanks to my advisory committee, Dr. Phil Bresnahan, Dr. Joanne Halls, and Dr. Qianqian Liu, as well as Dr. Brewin and my fellow COAST lab members who have contributed to this research. Lastly, we acknowledge the SeaHawk-HawkEye development and characterization team, including John Morrison, Gene Feldman, Alan Holmes, Sean Bailey, Alicia Scott, and Liang Hong.

