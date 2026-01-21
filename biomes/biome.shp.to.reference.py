import geopandas as gpd
import xarray as xr
import rasterio
from rasterio import features
import numpy as np
import pandas as pd

def shp_to_netcdf_aligned_to_reference(
    shapefile, reference_nc, output_nc, eco_field="BIOME_NAME", start_id=1
):
    # Load reference NetCDF grid
    ref_ds = xr.open_dataset(reference_nc)
    lat = ref_ds["lat"].values
    lon = ref_ds["lon"].values
    resolution_lat = abs(lat[1] - lat[0])
    resolution_lon = abs(lon[1] - lon[0])
    height = len(lat)
    width = len(lon)

    # Define transform (top-left origin)
    minx = lon.min() - resolution_lon / 2
    maxy = lat.max() + resolution_lat / 2
    transform = rasterio.transform.from_origin(minx, maxy, resolution_lon, resolution_lat)

    # Load and reproject shapefile
    gdf = gpd.read_file(shapefile)
    gdf = gdf.dropna(subset=["geometry", eco_field])
    gdf = gdf.to_crs("EPSG:4326")  # Match typical NetCDF lat/lon grid

    # Assign unique BIOME_IDs starting at `start_id`
    gdf = gdf.copy()
    gdf["BIOME_ID"] = gdf[eco_field].astype("category").cat.codes + start_id

    # Clean geometries (avoids invalid polygons)
    gdf["geometry"] = gdf["geometry"].buffer(0)

    # Create mapping: BIOME_ID -> ECO_NAME
    eco_mapping_df = gdf[["BIOME_ID", eco_field]].drop_duplicates().sort_values("BIOME_ID")
    eco_mapping = dict(zip(eco_mapping_df["BIOME_ID"], eco_mapping_df[eco_field]))

    # Rasterize
    shapes = ((geom, val) for geom, val in zip(gdf.geometry, gdf["BIOME_ID"]))
    raster = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        fill=-1,
        dtype=np.int32
    )

    # Ensure longitude is sorted (in case reference grid wraps)
    lon_sorted_idx = np.argsort(lon)
    lon = lon[lon_sorted_idx]
    raster = raster[:, lon_sorted_idx]

    # Build xarray DataArray
    da = xr.DataArray(
        raster,
        coords={"lat": lat, "lon": lon},
        dims=("lat", "lon"),
        name="BIOME_ID",
        attrs={"long_name": "Ecoregion ID", "missing_value": -1}
    )
    da.coords["lon"].attrs["units"] = "degrees_east"
    da.coords["lat"].attrs["units"] = "degrees_north"

    # Create dataset and attach mapping
    ds = da.to_dataset()
    ds.attrs["eco_name_mapping"] = str(eco_mapping)

    # Save output
    ds.to_netcdf(output_nc)
    print(f"Saved rasterized ecoregions aligned to {reference_nc} → {output_nc}")


shp_to_netcdf_aligned_to_reference(
    shapefile="Ecoregions2017.shp",
    reference_nc="/glade/campaign/ral/risc/jsallen/CPC/regrid_025/precip.1979.nc",
    output_nc="biomes.analog.gridded.nc"
)


