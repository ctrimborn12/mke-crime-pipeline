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
    
    
# add time features
def add_time_features(df):
    print("🔹 Extracting time features...")
    df["ReportedDateTime"] = pd.to_datetime(df["ReportedDateTime"], errors="coerce")
    df["Year"] = df["ReportedDateTime"].dt.year
    df["Month"] = df["ReportedDateTime"].dt.month
    df["Hour"] = df["ReportedDateTime"].dt.hour
    df["Weekday"] = df["ReportedDateTime"].dt.day_name()
    return df


def summarize_crimes_per_month(df):
    return (
        df.groupby(["Year", "Month"])
        .size()
        .reset_index(name="CrimeCount")
    )


def summarize_crimes_by_hour(df):
    return (
        df.groupby("Hour")
        .size()
        .reset_index(name="CrimeCount")
    )


def summarize_crimes_by_weekday(df):
    return (
        df.groupby("Weekday")
        .size()
        .reset_index(name="CrimeCount")
        .sort_values(by="CrimeCount", ascending=False)
    )


def summarize_crime_types(df, crime_types):
    melted = df.melt(value_vars=crime_types, var_name="CrimeType", value_name="Occurred")
    return (
        melted[melted["Occurred"] == 1]
        .groupby("CrimeType")
        .size()
        .reset_index(name="Count")
    )


def summarize_by_neighborhood(df, crime_types, name_col):
    # group by neighborhood
    grouped = df.groupby(name_col)[crime_types].sum()  
    # total crimes per neighborhood
    grouped['CrimeCount'] = grouped.sum(axis=1)
    return grouped[['CrimeCount']].reset_index()


def summarize_most_common_crime(df, crime_types, name_col):
    results = []

    # group by neighborhood
    grouped = df.groupby(name_col)

    for nhood, group in grouped:
        # sum occurrences per crime type
        counts = group[crime_types].sum()
        # pick the crime type with the highest count
        most_common = counts.idxmax()
        results.append({
            name_col: nhood,
            "CrimeType": most_common,
            "Count": counts[most_common]
        })

    return pd.DataFrame(results)


def transform_data(crime_path="data/raw/crime_raw.csv",
                   neighborhood_path="data/raw/neighborhood/neighborhood.shp",
                   output_dir="data/processed/"):
    os.makedirs(output_dir, exist_ok=True)

    crime, neighborhoods = load_data(crime_path, neighborhood_path)
    crime_joined, name_col = prepare_geodata(crime, neighborhoods)
    crime_joined = add_time_features(crime_joined)

    crime_types = [
        "Arson", "AssaultOffense", "Burglary", "CriminalDamage", "Homicide",
        "LockedVehicle", "Robbery", "SexOffense", "Theft", "VehicleTheft"
    ]

    # Generate summaries
    summaries = {
    "crimes_per_month": summarize_crimes_per_month(crime_joined),
    "crime_type_distribution": summarize_crime_types(crime_joined, crime_types),
    "crimes_per_neighborhood": summarize_by_neighborhood(crime_joined, crime_types, name_col),
    "most_common_crime_per_neighborhood": summarize_most_common_crime(crime_joined, crime_types, name_col),
    "crimes_by_hour": summarize_crimes_by_hour(crime_joined),
    "crimes_by_weekday": summarize_crimes_by_weekday(crime_joined),
    }
    
    for name, df in summaries.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        
        
if __name__ == "__main__":
    transform_data()