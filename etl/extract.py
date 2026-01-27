import json
import pandas as pd
import urllib.request
import os

CURRENT_RESOURCE_ID = "87843297-a6fa-46d4-ba5d-cb342fb2d3bb" 
HISTORICAL_RESOURCE_ID = "395db729-a30a-4e53-ab66-faeb5e1899c8"

def fetch_resource(resource_id, limit=5000):
    all_records = []
    offset = 0

    while True:
        url = (
            "https://data.milwaukee.gov/api/3/action/datastore_search"
            f"?resource_id={resource_id}&limit={limit}&offset={offset}"
        )

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())

        records = data["result"]["records"]
        if not records:
            break

        all_records.extend(records)
        offset += limit

    return pd.DataFrame(all_records)


def extract_data():
    os.makedirs("data/raw/api", exist_ok=True)

    print("Fetching current data...")
    df_current = fetch_resource(CURRENT_RESOURCE_ID)
    df_current.to_csv("data/raw/api/crime_raw_current.csv", index=False)
    print("Current rows:", len(df_current))

    print("Fetching historical data...")
    df_hist = fetch_resource(HISTORICAL_RESOURCE_ID)
    df_hist.to_csv("data/raw/api/crime_raw_historical.csv", index=False)
    print("Historical rows:", len(df_hist))

    return df_current, df_hist
