---

# Milwaukee Crime Dashboard

An interactive data visualization dashboard built with Streamlit to explore reported crime incidents in Milwaukee since 2005. The project includes a complete ETL pipeline that extracts, transforms, and loads crime data for analysis and visualization.

---

## Project Overview

This dashboard allows users to:
- Explore crime trends over time
- Filter incidents by year or view all available years
- Analyze offense distributions
- View temporal patterns by month, day of week, and hour
- See the most common offense by neighborhood using a geospatial map

---

## Data Sources

### Crime Data
- Source: City of Milwaukee Open Data Portal (CKAN Data API)
- Data includes both current and historical crime incident records dating back to 2005
- Raw data is extracted via API and stored as CSV files

### Neighborhood Boundaries
- Source: City of Milwaukee Open Data Portal (https://data.milwaukee.gov/dataset/0f5695f6-bca1-46e9-832b-54d1d906d28e/resource/964353e8-a579-402a-a8e9-c50ea0ae3aa4/download/neighborhood.zip)
- Data provided as a neighborhood shapefile
- Used to associate crime incidents with neighborhoods via spatial join

---

## Data Processing and ETL Pipeline

The ETL pipeline is located in the `etl/` directory and consists of the following steps:

### Extract
- Downloads current and historical crime data from the Milwaukee CKAN API
- Saves raw CSV files to `data/raw/api/`

### Transform
- Combines current and historical crime data
- Drops rows with missing coordinates 
- Converts reported date/time into derived features:
  - Year
  - Month
  - Hour
  - Day of week
- Creates a GeoDataFrame using Rough X/Y coordinates
- Performs a spatial join between crime points and neighborhood polygons to assign each incident to a neighborhood
- Generates a cleaned, analysis-ready dataset

### Load
- Writes processed data to `data/processed/crimes_joined.csv`

**Notes:**
- Crime data was extracted via the City of Milwaukee CKAN Data API and transformed for analysis.
- Neighborhood shapefile from the City of Milwaukee Open Data Portal was joined to crime incidents based on spatial location (Rough X/Y coordinates) to assign each crime to a neighborhood.

---

## Project Structure

```

.
├── data
│   ├── processed
│   │   └── crimes_sample.csv       
│   └── raw
│       ├── api
│       │   ├── crime_raw_current.csv
│       │   └── crime_raw_historical.csv
│       └── geo
│           └── neighborhood
│               ├── neighborhood.cpg
│               ├── neighborhood.dbf
│               ├── neighborhood.idx
│               ├── neighborhood.prj
│               ├── neighborhood.sbn
│               ├── neighborhood.sbx
│               ├── neighborhood.shp
│               ├── neighborhood.shp.xml
│               └── neighborhood.shx
├── etl
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
├── LICENSE
├── mke-crime-dashboard.py
├── requirements.txt
└── README.md


````

Note: The neighborhood boundary data consists of multiple files that collectively form a single shapefile. All listed files must be present in the same directory for GeoPandas to load the neighborhood geometry correctly.

---

## Key Insights from the Data

This section summarizes the primary insights revealed through interactive exploration of the dashboard. These findings are based on aggregated trends, temporal patterns, and spatial distributions observed in the data.

### Temporal Trends
- Incident counts have almost always decreased or remained steady since 2005, with the exception of spikes in the years 2020 and 2021. 
- Crime incidents show clear seasonal patterns, with higher volumes during the summer months.
- Weekends consistently see higher incident counts compared to weekdays

### Geographic Patterns
- Across all years, assault offense incidents have dominated the nothern half of the city whereas theft incidents have dominated the southern half.
- Up until around 2013, theft was the most prevalent offense across Milwaukee neighborhoods. From 2013 on, assault offense incidents have been the most prevalent.

### Crime Type Distribution
- Assualt offenses make up the largest share of incidents, followed by theft, vehicle theft, and criminal damage.
- From 2005-2012, theft had the largest share of incidents, from 2012 on, assault offenses had the largest share. 

---

## Running the Dashboard Locally

### 1. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the ETL pipeline

```bash
python etl/pipeline.py
```

### 4. Run the Streamlit app

```bash
streamlit run mke-crime-dashboard.py
```

---

## Deployment Notes

* The ETL pipeline can be run locally to update the processed dataset before deployment.
* The neighborhood shapefile must be downloaded manually from the City of Milwaukee Open Data Portal and placed in the expected directory.

---

## Technologies Used

* Python
* Streamlit
* Pandas
* GeoPandas
* Plotly
* Shapely

---

## License

This project is licensed under the MIT License.

---
