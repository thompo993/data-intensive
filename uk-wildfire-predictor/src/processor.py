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
import argparse

def initialize_gee():
    """
    Handles authentication using the Service Account.
    """
    key_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
    if not key_path:
        raise EnvironmentError("GEE_SERVICE_ACCOUNT_KEY not found.")     

    credentials = ee.ServiceAccountCredentials('bp-gee-data-pipeline@uk-wildfire-predictor.iam.gserviceaccount.com', 
                                                key_path,
            )
    ee.Initialize(credentials)
            
    print("Successfully initialized Earth Engine!")
    return

def get_uk_aoi() -> ee.Geometry:
    """
    Defines the Area of Interest (AOI) for the UK
    (England, Scotland, Wales and Northern Ireland).
    """
    uk_aoi = (
        ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.inList("ADM1_NAME", ["England", "Scotland", "Wales", "Northern Ireland"]))
        .geometry()
    )
    print("AOI area (km^2):", uk_aoi.area().divide(1e6).getInfo())
    # Expect ~243,000 km^2
    return uk_aoi

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
            'u': image.select('U10M'),
            'v': image.select('V10M')
        })
        .rename('wind_direction_rad')
        )

        return magnitude.addBands(direction).addBands(image.select(["U10M", "V10M"]))

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
    humidity = (ee.ImageCollection("NASA/GLDAS/V021/NOAH/G025/T3H")
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

    wind_data_magnitude = wind_hourly.select("wind_magnitude").max().rename("wind_magnitude")
    wind_data_direction = (wind_hourly.select("V10M").mean().atan2(wind_hourly.select("U10M").mean()).rename("wind_direction_rad"))

    
    # FIRMs mosaic, put together of multiple overlapping images 
    firms_mosaic = (
    ee.ImageCollection("FIRMS")
    .filterDate(start_date, end_date)
    .filterBounds(geometry)
    .mosaic()
    )

    firms = (
        ee.ImageCollection("FIRMS")
        .filterDate(start_date, end_date)
        .filterBounds(geometry)
    )

    def to_fire(img):
        return (
            img.select("T21").gt(320)
            .And(img.select("confidence").gte(50))
            .rename("fire_active")
            .toFloat()
        )

    zero = ee.Image.constant(0).toFloat().rename("fire_active")

    fire = (
        firms.map(to_fire)
        .merge(ee.ImageCollection([zero]))   
        .max()
        .unmask(0)
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
        .set("system:time_start", ee.Date(start_date).millis())
    )

    return stacked_image

def extract_features(stacked_image, geometry, scale=1000):
    """ extracts spatial features (max, mean stdDev) and
        timestamps across an ee.Imagecollection (our stacked images)
        puts into 10km grids. 
    """
    reducer = (ee.Reducer.max()
            .combine(ee.Reducer.mean(), sharedInputs=True)
        )

    grid = geometry.coveringGrid(ee.Projection("EPSG:27700"), 10_000)

    def image_to_feature(image):
        """get the image and convert it into statistics (data reduction)
        """
        stats = image.reduceRegions(
            collection=grid,
            reducer=reducer, 
            scale=scale,
        )
        window_start = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd'T'HH:mm:ss")


        def get_pixel_centre(pixel):
            """ get the lat and long of each pixel to get a location
            """
            centre = pixel.geometry().transform("EPSG:4326", 1).centroid(1).coordinates()
            return(ee.Feature(None, pixel.toDictionary())
                   .set({"cell_id": pixel.id(),
                         "lon": centre.get(0),
                         "lat": centre.get(1),
                         "window_start": window_start
                }))
        
        return stats.map(get_pixel_centre)


    if isinstance(stacked_image, ee.Image):
        stacked_image = ee.ImageCollection([stacked_image])
    features_composite = stacked_image.map(image_to_feature).flatten()
    info = features_composite.getInfo()

    return [f["properties"] for f in info["features"]]

def save_to_parquet(rows, base_path):
    """
    The 'Persistence' Step:
    Converts the dictionary to a DataFrame and saves as Parquet.
    saves a tmp file so corrupted jobs dont fail 
    adds a timestamp so that the file is not overlapped 

    file format: 
    date[YYYYMMDD]timestamp[YYYYMMDD]
    """

    # 1. Create DataFrame   
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No data found from GEE, so not saving...")

    df["window_start"] = pd.to_datetime(df["window_start"], utc=True)
    df = df.sort_values(["window_start", "cell_id"]).reset_index(drop=True)

    # 2. Create filename
    # Source - https://stackoverflow.com/a/55022031
    day = df["window_start"].min().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    # date, timestamp 
    filename = f"dt{base_path}{day}_ts{timestamp}.parquet"


    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    # write temp file and then rename, so a cancelled job cant corrupt (current issue)
    front = ["window_start", "cell_id", "lat", "lon"]
    cols = front + sorted(c for c in df.columns if c not in front)
    tmp = filename + ".tmp"
    df[cols].to_parquet(filename, index=False)
    os.replace(tmp, filename)
    print(f"Saved: {filename}")

def main():
    # 2. Initialize the Argument Parser
    parser = argparse.ArgumentParser(description="Fetch wildfire features from GEE and save to Parquet.")
    
    # 3. Add arguments
    # We use '--' to make them optional flags
    parser.add_argument('--start', type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument('--end', type=str, help="End date in YYYY-MM-DD format")
    
    args = parser.parse_args()

    # 4. Setup Environment
    initialize_gee()
    uk_geom = get_uk_aoi()

    # 5. Logic to decide which time window to use
    if args.start and args.end:
        # If the user provided dates, use them
        start_date = args.start
        end_date = args.end
        print(f"Running historical mode: {start_date} to {end_date}")
    else:
        # Default behavior: The last 24 hours
        today = datetime.datetime.now(datetime.timezone.utc).date()
        start_date = (today - datetime.timedelta(days=1)).isoformat()
        end_date = today.isoformat()
        print(f"Running default mode: {start_date} to {end_date}")

    # 6. Pass the chosen dates into your existing logic
    time_window = (start_date, end_date)
    
    # Note: Your current get_temporal_composites accepts (geometry, time_window)
    # which is exactly what we need.
    composite = get_temporal_composites(geometry=uk_geom, time_window=time_window)

    features = extract_features(composite, uk_geom)

    save_to_parquet(features, "data/")
    
if __name__ == "__main__":
    main()
