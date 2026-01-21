# Climate Analogs of Weather and Climate Metrics

## Overview

This repository contains Python scripts for calculating and estimating **Climate Analogs** — regions across the globe that experience similar weather and climate extremes. By identifying areas with comparable climate characteristics, these scripts are intended to help researchers, planners, and conservationists understand how climate impacts in one location might mirror conditions elsewhere.

### Analogs of Extreme and Impactful Weather

Climate analogs are identified by comparing key weather and climate metrics across different regions. This approach reveals geographical areas that, despite being potentially far apart, share similar patterns of climate extremes.

**Current metrics include:**
- **Wet Bulb Globe Tempreature**
<!--- **Heat extremes**: Number of days exceeding a Heat Index of 37°C (98.6°F)
- Additional extreme weather metrics (customizable based on research needs)-->

We will be adding more metrics to capture the intensity and frequency of impactful weather events that affect ecosystems, human health, agriculture, and infrastructure.

### Constraining Analogs by Global Biomes

To make climate analogs more ecologically meaningful and actionable, we constrain our analysis using **global biome classifications**. 

**What are biomes?**  
Biomes are large-scale ecological regions characterized by distinct climate conditions, vegetation types, and ecosystems. They represent areas where similar environmental conditions have given rise to comparable biological communities.

**Major global biomes include:**
- **Tropical & Subtropical Forests**: Warm, wet regions with high biodiversity (e.g., rainforests, seasonal tropical forests)
- **Temperate Forests**: Moderate climates with distinct seasons and deciduous or mixed forests
- **Boreal Forests/Taiga**: Cold climates with coniferous forests
- **Grasslands & Savannas**: Open landscapes dominated by grasses, with seasonal rainfall patterns
- **Deserts & Xeric Shrublands**: Arid regions with sparse vegetation adapted to low precipitation
- **Tundra**: Cold, treeless regions with permafrost and low-growing vegetation
- **Mediterranean Forests & Shrublands**: Hot, dry summers and mild, wet winters with drought-adapted vegetation
- **Mangroves**: Coastal wetland ecosystems in tropical and subtropical regions

**Why constrain by biomes?**  
By filtering climate analogs to regions within the same or similar biomes, we ensure that:
- Ecosystems have comparable vegetation structures and ecological functions
- Adaptive strategies and species responses may be more transferable between regions
- Conservation and management insights are more directly applicable
- The analogs reflect not just climate similarity but also ecological context

This dual approach produces more useful analog regions for understanding climate impacts and informing adaptation strategies.

### Joint Effort Between NCAR and The Nature Conservancy

This project is a collaborative initiative between:
- **NSF NCAR (National Science Foundation National Center for Atmospheric Research)**: Providing climate science expertise, data infrastructure, and computational resources
- **The Nature Conservancy**: Contributing conservation science perspectives, ecological expertise, and applied needs for climate adaptation planning

---

## Data Sources
We currently leverage ERA5 Reanalysis to identify Climate Analog regions in our historical climate. The analysis period is 1950-2020. Additionally, when available, we make use of the impact metrics computed from ERA5 which are provided by the World Bank through the CCKP.

<!-- Add the following info later
## Installation
[Installation instructions]

## Usage
[Usage examples]

## Contributing
[Contribution guidelines]

## License
[License information] -->

## Contact

Jacob Stuivenvolt-Allen : jsallen@ucar.edu
