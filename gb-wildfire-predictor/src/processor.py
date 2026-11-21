'''
# processor.py

## Description:
This script fetches data that is desired for processing data, and placing into a data
directory in parquet format, suitable for determing the data.

## Usage:
NOT HERE WIP

## AI Attribution:
This script pseudcode was intially written by myself, adn then refined in  RedOne Gemma.
Gemma only wrote psuedocode, i wrote the final code myself
'''

import ee
import os
import pandas as pd
import datetime

def initialize_gee():
    """
    Handles authentication using the Service Account.
    """
    key_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
    if not key_path:
        raise EnvironmentError("GEE_SERVICE_ACCOUNT_KEY not found.")
    
    key_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
    

    credentials = ee.ServiceAccountCredentials('bp-gee-data-pipeline@uk-wildfire-predictor.iam.gserviceaccount.com', 
                                                key_path,
            )
    ee.Initialize(credentials)
            
    print("Successfully initialized Earth Engine!")
    return

def get_gb_aoi(): 
    """
    Defines the area of interst (AOI) which is great gritan (england + scotland+wales)
    """
    uk_aoi = (ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM0_NAME", "United Kingdom"))
        .filter(ee.Filter.inList("ADM1_NAME", ["England", "Scotland", "Wales"]))
        .geometry()
    )
    print("AOI area (km^2):", get_gb_aoi().area().divide(1e6).getInfo())
    # Expect 229,000 km^2 
    return uk_aoi
    

def get_temporal_composites(geometry, time_window):
    """
    The 'Fusion' Step:
    1. Define the time filter (e.g., last 24h).
    2. Load collections (IMERG, MERRA-2, etc.).
    3. Create a composite for each (e.g., .max() or .mean()).
    4. Stack them using .addBands().

    kwargs: 
    geometry: UK coastline polygon 
    time_window: (start_date, end_date) in 'YYYY-MM-DD' format
    """
    # Example logic:
    # rainfall = ee.ImageCollection("NASA/GPM_L3/IMERG").filterBounds(geometry)...max()
    # temp = ee.ImageCollection("MODIS_DATA").filterBounds(geometry)...max()
    # stacked_image = rainfall.addBands(temp).addBands(wind)
    # return stacked_image

    start_date, end_date = time_window

    # temperature 
    temp = (
        ee.ImageCollection("NASA/GLDAS/V021/NOAH/G025/T3H")
        .filterDate(start_date, end_date)
        .select("Tair_f_inst")
        .max()
        .subtract(273.15)
        .rename("temp_c")
    )

    # humidity 
    humidtiy = (ee.ImageCollection("NASA/GLDAS/V201/NOAH/G025/T3H")
        .filterDate(start_date, end_date)
        .select("Qair_f_inst")
        .min()
        .rename("humidity_q")
    )

    # rainfall 
    rainfall = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
        .filterDate(start_date, end_date)
        .select("precipitation")
        .sum()
        .multiply(0.5) # this turns the half hourly mm/hr rate into total rainfall in mm
        .rename("precipitation_mm")
    )















    stacked_image = (temp)
    return stacked_image

def extract_features(stacked_image, geometry):
    """
    The 'Reduction' Step:
    Runs the heavy math on Google's servers.
    """
    # stats = stacked_image.reduceRegion(
    #     reducer=ee.Reducer.max().combine(reducer=ee.Reducer.stdDev(), sharedInputs=True),
    #     geometry=geometry,
    #     scale=1000 # Very important: defines the resolution of your extraction
    # )
    # return stats.getInfo() # This is the ONLY time we pull data to local Python
    pass

def save_to_parquet(feature_dict, base_path):
    """
    The 'Persistence' Step:
    Converts the dictionary to a DataFrame and saves as Parquet.
    """
    # 1. Create timestamp
    # 2. Create DataFrame
    # 3. df.to_parquet(filename)
    pass

def main():
    # 1. Setup
    initialize_gee()
    
    # 2. Define AOI (Use a polygon for Scotland/Wales/England)
    # geometry = ee.Geometry.Polygon(...)
    
    # 3. Process
    # composite = get_temporal_composites(geometry, "24h")
    # features = extract_features(composite, geometry)
    
    # 4. Save
    # save_to_parquet(features, "data/output_")

if __name__ == "__main__":
    main()