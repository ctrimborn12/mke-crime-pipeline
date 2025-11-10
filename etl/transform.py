import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# load data

def load_data(crime_path, neighborhood_path):
    crime = pd.read_csv(crime_path)
    neighborhoods = gpd.read_file(neighborhood_path)
    return crime, neighborhoods


# geocode join

def prepare_geodata(crime, neighborhoods):
    crime = crime.dropna(subset=["RoughX", "RoughY"])
    geometry = [Point(xy) for xy in zip(crime["RoughX"], crime["RoughY"])]
    crime_gdf = gpd.GeoDataFrame(crime, geometry=geometry, crs="EPSG:32054")

    crime_joined = gpd.sjoin(crime_gdf, neighborhoods, how="left", predicate="within")
    name_col = "NEIGHBORHD"

    return crime_joined, name_col
    

