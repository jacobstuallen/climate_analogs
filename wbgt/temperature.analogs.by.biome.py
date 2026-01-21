#!/bin/python
# author: Jacob Stuivenvolt-Allen
# contact: jsallen@ucar.edu

import numpy as np
import xarray as xr

# User defined variables
# -----------------------------
# Netcdf dataset on ERA5 Grid 
raw_ds = xr.open_dataset('wbgt_annual_metrics.nc', decode_timedelta=False)
clim_ds = raw_ds.mean(dim='year')

varlist = list(clim_ds.keys())

lat = clim_ds.lat
lon = clim_ds.lon
X, Y = np.meshgrid(lon, lat)

# -----------------------------
# End of user defined variables

# Plot settings
# --------------------
import matplotlib.pyplot as plt
import cartopy as crs
import colormaps as cmaps
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
import matplotlib.font_manager as font_manager

font_dir = '/glade/work/jsallen/conda-envs/earth/fonts/Avenir-Medium.otf'
font_manager.fontManager.addfont(font_dir)
prop = font_manager.FontProperties(fname=font_dir)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()

xticks = np.arange(-180,181,60)
yticks = np.arange(-90,91,30)

pcrs = ccrs.Robinson()
tcrs = ccrs.PlateCarree()

def plot(ax):
    ax.set_extent([-180,180,-90,90])
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidths=0.3)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidths=0.3)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidths=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='gainsboro')
    return(ax)

# --------------------
# End of plot settings


# Load data
# ---------
path = '/glade/u/home/jsallen/projects/tnc_2025/analogs/biomes/'
file = 'biomes.analog.gridded.nc'

biome_ds = xr.open_dataset(path+file)

biomes = {1:'Boreal Forests/Taiga',
          2:'Deserts & Xeric Shrublands',
          3:'Flooded Grasslands & Savannas',
          4:'Mangroves',
          5:'Mediterranean Forests, Woodlands & Scrub',
          6:'Montane Grasslands & Shrublands',
          7:'Rock and Ice',
          8:'Temperate Broadleaf & Mixed Forests',
          9:'Temperate Conifer Forests',
          10:'Temperate Grasslands, Savannas & Shrublands',
          11:'Tropical & Subtropical Coniferous Forests',
          12:'Tropical & Subtropical Dry Broadleaf Forests',
          13:'Tropical & Subtropical Grasslands, Savannas & Shrublands',
          14:'Tropical & Subtropical Moist Broadleaf Forests',
          15:'Tundra'}

for b, biome in biomes.items():

    #if b != 7 : continue
    print(b, biome)
    bio = xr.where(biome_ds['BIOME_ID'] == b, 1, np.nan)

    # NOW, PLOT WITH AN ADDITIONAL FILTER
    # -----------------------------------
    for v, var in enumerate(varlist):
        if v == 2: continue

        # FIX: Don't reassign coordinates - they already match!
        # Just use the data directly
        clim_da = clim_ds[var]
        
        # Apply biome mask directly without coordinate reassignment
        cmpd_analog = xr.where(biome_ds['BIOME_ID'] == b, clim_da, np.nan)

        # Calculate 10th and 90th percentiles for contour levels
        p10 = np.nanpercentile(cmpd_analog.values, 15, method='closest_observation')
        p90 = np.nanpercentile(cmpd_analog.values, 85, method='closest_observation')
        
        # Round to nearest tenth (1 decimal place)
        p10_rounded = np.round(p10, 1)
        p90_rounded = np.round(p90, 1)
        
        # Skip if levels won't be increasing
        if p10_rounded >= p90_rounded:
            print(f"  {var}: Skipping - p10={p10_rounded} >= p90={p90_rounded} (no range)")
            continue
        
        # Create levels between rounded p10 and p90
        levels = np.linspace(p10_rounded, p90_rounded, 11)  # 11 levels between 10th and 90th percentile
        
        print(f"  {var}: p10={p10_rounded}, p90={p90_rounded}")

        # attributes
        units = raw_ds[var].attrs['units']
        ln    = raw_ds[var].attrs['long_name']

        fig = plt.figure(figsize=(9,5))
        ax = fig.add_subplot(111, projection=pcrs)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)
        varstr = var

        try:
            cf = ax.contourf(X, Y, cmpd_analog, levels=levels, cmap=cmaps.nice_gfdl, 
                            transform=tcrs, extend='both')
            ax.set_title(biome + f" and {ln}", fontsize=11, loc='left')
            plot(ax)

            cbar_ax = fig.add_axes([0.20,0.10,0.60,0.03])
            plt.colorbar(cf, cax=cbar_ax, orientation='horizontal', label=f'{units}')

            bb = f"{b:02d}"

            plt.savefig(f'figures/biome.{bb}.{var}.png', dpi=500)
            #plt.show()
            plt.close()
            
        except Exception as e:
            print(f"  ERROR plotting {var}: {type(e).__name__}: {str(e)}")
            print(f"  Skipping this plot...")
            plt.close()
            continue
