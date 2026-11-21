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
    gb_aoi = (ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM0_NAME", "United Kingdom"))
        .filter(ee.Filter.inList("ADM1_NAME", ["England", "Scotland", "Wales"]))
        .geometry()
    )
    print("AOI area (km^2):", gb_aoi.area().divide(1e6).getInfo())
    # Expect 229,000 km^2 
    return gb_aoi

def compute_hourly_wind_vector(image):
        """
        Turns U and V ciomponents from NASA/GSFC/MERRA/slv/2. conducts calculations on the GEE server
        to reduce compute constraints

        kwargs: 
        image - image from the database 

        returns: 
        magnitude.addBands(direction) - two bands, magntiude, and direction respectively. 
        """
        magnitude = (image.expression(
        "sqrt(u**2 + v**2)", {
            "u": image.select("U10M"),
            "v": image.select("V10M")
        })
        .rename("wind_magnitude")
        )

        direction = (image.expression(
        'atan2(v, u)', {
            'u': image.select('u_wind'),
            'v': image.select('v_wind')
        })
        .rename('wind_direction_rad')
        )

        return magnitude.addBands(direction)

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

    returns: 
    stacked-image
    """


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
    humidity = (ee.ImageCollection("NASA/GLDAS/V201/NOAH/G025/T3H")
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

        # satelites 
    

    wind_hourly = (
        ee.ImageCollection("NASA/GSFC/MERRA/slv/2")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .map(compute_hourly_wind_vector)
    )

    wind_data = (
        wind_hourly.select("wind_magnitude").max()
        .addBands(wind_hourly.select("wind_direction_rad").mean())
    )
    wind_data_magnitude = wind_hourly.select("wind_magnitude").max().rename("wind_magnitude")
    wind_data_direction= wind_hourly.select("wind_direction_rad").mean().rename("wind_direction_rad")

    # FIRMs mosaic, put together of multiple overlapping images 
    firms_mosaic = (
    ee.ImageCollection("FIRMS")
    .filterDate(start_date, end_date)
    .filterBounds(geometry)
    .mosaic()
    )

    fire = (
    firms_mosaic.select("T21").gt(320)
    .And(firms_mosaic.select("confidence").gte(50))
    .unmask(0)
    .toFloat()
    .rename("fire_active")
)


    # 3. Stack everything together
    # This combines your scalar weather variables and your new hybrid wind features
    stacked_image = (
        temp
        .addBands(humidity)
        .addBands(rainfall)
        .addBands(wind_data_magnitude)
        .addBands(wind_data_direction)
        .addBands(fire)
        .clip(geometry)
    )

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