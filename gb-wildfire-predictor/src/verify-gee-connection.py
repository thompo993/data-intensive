'''
# verify-gee-connection.py

## Description:
This script serves to verify the connection between blue pebble and GEE, and is a first step for
determining if I can connect to GEE, and also serves as a first debugging step.

## Usage:
python verify-gee-connection.py

## AI Attribution:
This script was written with RedOne Gemma.
'''


import ee
import os

def verify_gee_connection():
    # 1. Retrieve the path to the JSON key from an environment variable
    # This is a best practice for security and containerization
    key_path = os.getenv('GEE_SERVICE_ACCOUNT_KEY')

    if not key_path:
        print("ERROR: Environment variable 'GEE_SERVICE_ACCOUNT_KEY' not set.")
        print("Please set it using: export GEE_SERVICE_ACCOUNT_KEY='/path/to/your/key.json'")
        return False

    try:
        print(f"Attempting to authenticate using: {key_path}")
        
        # 2. Initialize the Earth Engine API with the service account
        # The credentials argument handles the service account authentication
        credentials = ee.ServiceAccountCredentials(
            'bp-gee-data-pipeline@uk-wildfire-predictor.iam.gserviceaccount.com', 
            key_path
        )
        ee.Initialize(credentials)
        
        print("Successfully initialized Earth Engine!")

        # 3. The 'Proof of Life' test: Request metadata from a common dataset
        # We use MODIS Terra Vegetation Indices (MOD13Q1) as a test
        test_collection = ee.ImageCollection("MODIS/061/MOD13Q1")
        first_image = test_collection.first()
        
        # Get the system ID to prove we actually communicated with the server
        image_id = first_image.get('system:index').getInfo()
        
        print(f"VERIFICATION SUCCESS: Connection established.")
        print(f"Successfully retrieved metadata for test image ID: {image_id}")
        return True

    except Exception as e:
        print(f"VERIFICATION FAILED: An error occurred during connection.")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    verify_gee_connection()