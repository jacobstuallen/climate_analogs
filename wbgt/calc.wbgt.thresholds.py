#!/bin/python
# author: Jacob Stuivenvolt-Allen
# contact: jsallen@ucar.edu

import numpy as np
import xarray as xr
import subprocess
from datetime import datetime
import os

# =============================================================================
# Wet Bulb Globe Temperature Processing
# =============================================================================

# Load data with better chunking
path = '/glade/campaign/ral/risc/jsallen/TNC/ERA5_heat/'
da = xr.open_mfdataset(f'{path}wbgtmax_*_daily_ERA5.nc',
                       chunks={'time': 365, 'latitude': 601, 'longitude': 1440})['wbgtmax']

# Rechunk for better memory efficiency
print("Rechunking data for memory efficiency...")
da = da.chunk({'time': 365, 'latitude': 601, 'longitude': 1440})
print(da)

# Create temporary directory for intermediate files
temp_dir = 'temp_wbgt_processing'
os.makedirs(temp_dir, exist_ok=True)

# =============================================================================
# Compute and save each variable ONE AT A TIME
# =============================================================================

print("\n" + "=" * 60)
print("Computing variables one at a time to manage memory...")
print("=" * 60)

# Variable 1: Daily mean
print("\n[1/6] Calculating daily mean...")
daily_mean = da.groupby('time.year').mean(skipna=True).mean(dim='year')
daily_mean = daily_mean.assign_attrs({
    'long_name': 'Multi-year mean of annual maximum wet bulb globe temperature',
    'units': 'degC',
    'description': 'Mean of annual maximum WBGT values averaged across all years',
    'grid_mapping': 'crs'
})
print("Computing...")
daily_mean_computed = daily_mean.compute()
print(f"  Mean: {float(daily_mean_computed.mean().values):.2f}")
daily_mean_computed.to_netcdf(f'{temp_dir}/daily_mean.nc')
del daily_mean, daily_mean_computed
print("  Saved and cleared from memory")

# Variable 2: 95th percentile - COMPUTE IN SPATIAL CHUNKS
print("\n[2/6] Calculating 95th percentile in spatial chunks (this may take a while)...")

# Split into longitude chunks to process separately
n_lon_chunks = 6  # Process 240 longitudes at a time (1440/6)
lon_size = len(da.longitude)
chunk_size = lon_size // n_lon_chunks

quant_95_chunks = []

for i in range(n_lon_chunks):
    start_idx = i * chunk_size
    end_idx = (i + 1) * chunk_size if i < n_lon_chunks - 1 else lon_size
    
    print(f"  Processing longitude chunk {i+1}/{n_lon_chunks} (indices {start_idx}:{end_idx})...")
    
    # Select spatial subset
    da_subset = da.isel(longitude=slice(start_idx, end_idx))
    
    # Compute quantile for this chunk
    quant_chunk = da_subset.quantile(0.95, dim='time', method='linear').compute()
    quant_95_chunks.append(quant_chunk)
    
    # Clean up
    del da_subset, quant_chunk
    print(f"    Chunk {i+1} complete")

# Concatenate all chunks
print("  Combining longitude chunks...")
quant_95_computed = xr.concat(quant_95_chunks, dim='longitude')
quant_95_computed = quant_95_computed.assign_attrs({
    'long_name': '95th percentile of daily maximum wet bulb globe temperature',
    'units': 'degC',
    'description': '95th percentile threshold across entire time period',
    'grid_mapping': 'crs'
})
print(f"  Mean: {float(quant_95_computed.mean().values):.2f}")
quant_95_computed.to_netcdf(f'{temp_dir}/quant_95.nc')

# Keep for threshold calculations
quant_95_value = quant_95_computed
del quant_95_chunks, quant_95_computed
print("  Saved and cleared from memory")

# Variable 3: Days above 95th percentile
print("\n[3/6] Calculating days above 95th percentile...")
n_wbt_95 = xr.where(da >= quant_95_value, 1, np.nan).groupby('time.year').sum().mean(dim='year')
n_wbt_95 = n_wbt_95.assign_attrs({
    'long_name': 'Mean annual days exceeding 95th percentile WBGT',
    'units': 'days',
    'description': 'Average number of days per year exceeding the 95th percentile threshold',
    'grid_mapping': 'crs'
})
print("Computing...")
n_wbt_95_computed = n_wbt_95.compute()
print(f"  Mean: {float(n_wbt_95_computed.mean().values):.2f}")
n_wbt_95_computed.to_netcdf(f'{temp_dir}/n_wbt_95.nc')
del n_wbt_95, n_wbt_95_computed, quant_95_value
print("  Saved and cleared from memory")

# Variable 4: Days above 27C
print("\n[4/6] Calculating days above 27C...")
n_wbt_27 = xr.where(da >= 27, 1, np.nan).groupby('time.year').sum().mean(dim='year')
n_wbt_27 = n_wbt_27.assign_attrs({
    'long_name': 'Mean annual days with WBGT ≥ 27°C',
    'units': 'days',
    'description': 'Average number of days per year with moderate heat risk (WBGT ≥ 27°C)',
    'risk_level': 'moderate',
    'grid_mapping': 'crs'
})
print("Computing...")
n_wbt_27_computed = n_wbt_27.compute()
print(f"  Mean: {float(n_wbt_27_computed.mean().values):.2f}")
n_wbt_27_computed.to_netcdf(f'{temp_dir}/n_wbt_27.nc')
del n_wbt_27, n_wbt_27_computed
print("  Saved and cleared from memory")

# Variable 5: Days above 29C
print("\n[5/6] Calculating days above 29C...")
n_wbt_29 = xr.where(da >= 29, 1, np.nan).groupby('time.year').sum().mean(dim='year')
n_wbt_29 = n_wbt_29.assign_attrs({
    'long_name': 'Mean annual days with WBGT ≥ 29°C',
    'units': 'days',
    'description': 'Average number of days per year with high heat risk (WBGT ≥ 29°C)',
    'risk_level': 'high',
    'grid_mapping': 'crs'
})
print("Computing...")
n_wbt_29_computed = n_wbt_29.compute()
print(f"  Mean: {float(n_wbt_29_computed.mean().values):.2f}")
n_wbt_29_computed.to_netcdf(f'{temp_dir}/n_wbt_29.nc')
del n_wbt_29, n_wbt_29_computed
print("  Saved and cleared from memory")

# Variable 6: Days above 31C
print("\n[6/6] Calculating days above 31C...")
n_wbt_31 = xr.where(da >= 31, 1, np.nan).groupby('time.year').sum().mean(dim='year')
n_wbt_31 = n_wbt_31.assign_attrs({
    'long_name': 'Mean annual days with WBGT ≥ 31°C',
    'units': 'days',
    'description': 'Average number of days per year with extreme heat risk (WBGT ≥ 31°C)',
    'risk_level': 'extreme',
    'grid_mapping': 'crs'
})
print("Computing...")
n_wbt_31_computed = n_wbt_31.compute()
print(f"  Mean: {float(n_wbt_31_computed.mean().values):.2f}")
n_wbt_31_computed.to_netcdf(f'{temp_dir}/n_wbt_31.nc')
del n_wbt_31, n_wbt_31_computed
print("  Saved and cleared from memory")

# Clear the large input data from memory
del da

# =============================================================================
# Combine all variables into final dataset
# =============================================================================

print("\n" + "=" * 60)
print("Combining variables into final dataset...")
print("=" * 60)

# Load all computed variables (they're small now)
daily_mean = xr.open_dataarray(f'{temp_dir}/daily_mean.nc')
quant_95 = xr.open_dataarray(f'{temp_dir}/quant_95.nc')
n_wbt_95 = xr.open_dataarray(f'{temp_dir}/n_wbt_95.nc')
n_wbt_27 = xr.open_dataarray(f'{temp_dir}/n_wbt_27.nc')
n_wbt_29 = xr.open_dataarray(f'{temp_dir}/n_wbt_29.nc')
n_wbt_31 = xr.open_dataarray(f'{temp_dir}/n_wbt_31.nc')

# Create CRS variable
crs_var = xr.DataArray(
    0,
    attrs={
        'grid_mapping_name': 'latitude_longitude',
        'longitude_of_prime_meridian': 0.0,
        'semi_major_axis': 6378137.0,
        'inverse_flattening': 298.257223563,
        'crs_wkt': 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]',
    }
)

# Global attributes
global_attrs = {
    'title': 'Wet Bulb Globe Temperature (WBGT) Climate Metrics',
    'institution': 'NSF NCAR',
    'source': 'ERA5 reanalysis',
    'history': f'Created {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
    'author': 'Jacob Stuivenvolt-Allen',
    'contact': 'jsallen@ucar.edu',
    'description': 'Multi-year averaged statistics and threshold exceedance metrics for daily maximum WBGT',
    'references': 'Heat risk thresholds based on occupational health guidelines',
    'Conventions': 'CF-1.8',
}

# Create final dataset
ds_out = xr.Dataset(
    data_vars={
        'wbgtmax_annual_mean': daily_mean,
        'wbgtmax_p95': quant_95,
        'days_above_p95': n_wbt_95,
        'days_above_27C': n_wbt_27,
        'days_above_29C': n_wbt_29,
        'days_above_31C': n_wbt_31,
        'crs': crs_var
    },
    attrs=global_attrs
)

print("\nDataset Summary:")
print("=" * 60)
print(ds_out)
print("\n" + "=" * 60)

# Define CF-compliant fill value and encoding
fill_value = -9999.0

encoding = {
    var: {
        'zlib': True,
        'complevel': 4,
        'dtype': 'float32',
        '_FillValue': fill_value
    }
    for var in ds_out.data_vars if var != 'crs'
}
encoding['crs'] = {'dtype': 'int32'}

# Save to netCDF
output_file = 'wbgt_annual_metrics.nc'
print("\nWriting final NetCDF file...")
ds_out.to_netcdf(output_file, encoding=encoding)
print(f"NetCDF output saved to: {output_file}")

# Display variable statistics
print("\nVariable Statistics:")
print("-" * 60)
for var in ds_out.data_vars:
    if var == 'crs':
        continue
    print(f"\n{var}:")
    print(f"  Mean: {float(ds_out[var].mean().values):.2f}")
    print(f"  Min:  {float(ds_out[var].min().values):.2f}")
    print(f"  Max:  {float(ds_out[var].max().values):.2f}")

# Clean up temporary files
print("\nCleaning up temporary files...")
import shutil
shutil.rmtree(temp_dir)
print("Temporary files removed")

# =============================================================================
# Convert to GeoTIFF using GDAL
# =============================================================================

print("\n" + "=" * 60)
print("Converting to GeoTIFF format...")
print("=" * 60)

# Convert each variable to a separate GeoTIFF
variables_to_convert = [
    'wbgtmax_annual_mean', 'wbgtmax_p95', 'days_above_p95',
    'days_above_27C', 'days_above_29C', 'days_above_31C'
]

for var in variables_to_convert:
    output_tif = f'wbgt_{var}.tif'

    # Use gdal_translate to convert netCDF to GeoTIFF
    cmd = [
        'gdal_translate',
        '-of', 'GTiff',
        '-co', 'COMPRESS=LZW',
        '-co', 'TILED=YES',
        '-a_srs', 'EPSG:4326',
        f'NETCDF:{output_file}:{var}',
        output_tif
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Created: {output_tif}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {var}: {e.stderr}")

print("\n" + "=" * 60)
print("Processing complete!")
print("=" * 60)
