import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import cartopy as crs
import xarray as xr
import colormaps as cmaps
from colormaps.utils import concat
from matplotlib.patches import Patch

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
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidths=0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidths=0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidths=0.5)
    return(ax)

# Load data
# ---------
# OPEN BIOME DATA AND LOOP THROUGH:

path = '/glade/u/home/jsallen/projects/tnc_2025/analogs/biomes/'
file = 'biomes.analog.gridded.nc'

ds = xr.open_dataset(path+file)['BIOME_ID']

lat = ds.lat
lon = ds.lon
X, Y = np.meshgrid(lon,lat)

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

# FIRST, JUST THE BIOME
# ---------------------
plt.style.use('dark_background')

fig = plt.figure(figsize=(12,7))
ax = fig.add_subplot(111, projection=pcrs)
fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)

concat1 = concat(["bold","set2"])
cmap_points = np.linspace(0, 1, 15)
colors = concat1(cmap_points)

from matplotlib.colors import ListedColormap
hex_colors = [
    '#2D5016',   # 1: Boreal Forests/Taiga
    '#D4A574',   # 2: Deserts & Xeric Shrublands
    '#7FBF7F',   # 3: Flooded Grasslands & Savannas
    '#1B4D3E',   # 4: Mangroves
    '#8B7355',   # 5: Mediterranean Forests, Woodlands & Scrub
    '#A8C256',   # 6: Montane Grasslands & Shrublands
    '#E8F4F8',   # 7: Rock and Ice
    '#4A7C59',   # 8: Temperate Broadleaf & Mixed Forests
    '#1F5E3D',   # 9: Temperate Conifer Forests
    '#C8B568',   # 10: Temperate Grasslands, Savannas & Shrublands
    '#3D6B3D',   # 11: Tropical & Subtropical Coniferous Forests
    '#8FAF4D',   # 12: Tropical & Subtropical Dry Broadleaf Forests
    '#D4C157',   # 13: Tropical & Subtropical Grasslands, Savannas & Shrublands
    '#228B22',   # 14: Tropical & Subtropical Moist Broadleaf Forests
    '#B8C9D9'    # 15: Tundra
]


hex_colors = [
    '#2D5016',   # 1: Boreal Forests/Taiga - dark evergreen
    '#E8A965',   # 2: Deserts & Xeric Shrublands - warm orange
    '#6BCDCD',   # 3: Flooded Grasslands & Savannas - aqua blue
    '#1B4D3E',   # 4: Mangroves - dark teal green
    '#C17E5D',   # 5: Mediterranean Forests, Woodlands & Scrub - terracotta
    '#9B6B9E',   # 6: Montane Grasslands & Shrublands - purple
    '#E8F4F8',   # 7: Rock and Ice - icy blue-white
    '#4A7C59',   # 8: Temperate Broadleaf & Mixed Forests - medium forest green
    '#1F5E3D',   # 9: Temperate Conifer Forests - deep forest green
    '#D4A837',   # 10: Temperate Grasslands, Savannas & Shrublands - golden yellow
    '#3D6B3D',   # 11: Tropical & Subtropical Coniferous Forests - tropical evergreen
    '#8FAF4D',   # 12: Tropical & Subtropical Dry Broadleaf Forests - lime green
    '#E8954A',   # 13: Tropical & Subtropical Grasslands, Savannas & Shrublands - burnt orange
    '#228B22',   # 14: Tropical & Subtropical Moist Broadleaf Forests - vibrant rainforest green
    '#8B7FA8'    # 15: Tundra - lavender purple
]


cmap = ListedColormap(hex_colors, name="biome_cmap")
#cmap_points = np.linspace(0, 1, 15)
#colors = cmap(cmap_points)
#print(colors)

cf = ax.contourf(X, Y, ds, 
                 levels=np.arange(1,16), 
                 cmap=cmap,
                 #cmap=concat1,
                 #cmap='gist_ncar',
                 transform=tcrs)


cbar_ax = fig.add_axes([0.3,0.20,0.4,0.03])
plt.colorbar(cf, cax=cbar_ax, orientation='horizontal')

legend_handles = []
legend_labels = []

for index, label in biomes.items():
    color = hex_colors[index-1]
    legend_handles.append(Patch(facecolor=color))
    legend_labels.append(label)
    print(label)

# 4. Add the Legend to the plot
ax.legend(bbox_to_anchor=(0.50, -0.3), 
          loc='lower center', borderaxespad=0.,
          handles=legend_handles, 
          labels=legend_labels, 
          ncols=4,
          labelspacing=0.7,
          columnspacing=0.7,
          fontsize=8)

ax.set_title("Global Biomes", fontsize=14, loc='left')
plot(ax)
plt.savefig('biomes.overview.png', dpi=300)
plt.show()
plt.close()
