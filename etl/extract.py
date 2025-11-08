import json
import pandas as pd
import urllib.request
import os

os.makedirs("data/raw", exist_ok=True)

RESOURCE_ID = "87843297-a6fa-46d4-ba5d-cb342fb2d3bb"
LIMIT = 5000  # fetch 5000 rows per request
URL = f"https://data.milwaukee.gov/api/3/action/datastore_search?resource_id={RESOURCE_ID}&limit={LIMIT}"

def extract_data():
    print("Fetching data from CKAN API...")
    fileobj = urllib.request.urlopen(URL)
    response_dict = json.loads(fileobj.read())

    # The data is in response_dict['result']['records']
    records = response_dict["result"]["records"]
    
    df = pd.DataFrame(records)
    
    df.to_csv("data/raw/crime_raw.csv", index=False)
    print(f"✅ Extracted {len(df)} rows to data/raw/crime_raw.csv")
    print("Columns:", df.columns.tolist())
    
    return df

if __name__ == "__main__":
    extract_data()