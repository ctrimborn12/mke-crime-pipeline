import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

#file reader helper function
def read_csv_file(path):
    return pd.read_csv(path)

#concatonate crime data and read neighborhoods data
def read_raw_data(current_crime_path, historical_crime_path, neighborhood_path):
    current = read_csv_file(current_crime_path)
    historical = read_csv_file(historical_crime_path)
    crime = pd.concat([current, historical], ignore_index=True)
    
    neighborhoods = gpd.read_file(neighborhood_path)
    return crime, neighborhoods

#add geometry column to geodf
def add_geometry(crime_df):
    crime_df = crime_df.dropna(subset=["RoughX", "RoughY"])
    geometry = [Point(xy) for xy in zip(crime_df["RoughX"], crime_df["RoughY"])]
    return gpd.GeoDataFrame(crime_df, geometry=geometry, crs="EPSG:32054")

#join neighborhoods data with crime data
def spatial_join(crime_gdf, neighborhoods):
    crime_joined = gpd.sjoin(crime_gdf, neighborhoods, how="left", predicate="within")
    name_col = "NEIGHBORHD"
    return crime_joined, name_col


# add time features
def add_time_features(df):
    df["ReportedDateTime"] = pd.to_datetime(df["ReportedDateTime"], errors="coerce")
    df["Year"] = df["ReportedDateTime"].dt.year
    df["Month"] = df["ReportedDateTime"].dt.month
    df["Hour"] = df["ReportedDateTime"].dt.hour
    df["Weekday"] = df["ReportedDateTime"].dt.day_name()
    return df

# transform
def transform_data(current_crime_path="data/raw/api/crime_raw_current.csv",
                   historical_crime_path="data/raw/api/crime_raw_historical.csv",
                   neighborhood_path="data/raw/geo/neighborhood/neighborhood.shp"):
    
    crime, neighborhoods = read_raw_data(current_crime_path, historical_crime_path, neighborhood_path)
    crime_gdf = add_geometry(crime)
    crime_joined, name_col = spatial_join(crime_gdf, neighborhoods)
    crime_joined = add_time_features(crime_joined)
    crime_joined["ReportUID"] = range(1, len(crime_joined) + 1)
    
    summaries = {"crimes_joined": crime_joined}
    return summaries