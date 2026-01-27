# Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json

st.set_page_config(layout="wide")

CSS_STYLES = """
<style>
.stApp {
    background: radial-gradient(circle at top,
        #0B1625 0%,
        #070E18 60%,
        #050B14 100%);
    color: #E6EEF6;
}

.block-container {
    padding-top: 1.5rem !important;
}

.mke-card {
    background: linear-gradient(
        180deg,
        rgba(24,45,68,0.95),
        rgba(15,28,45,0.95)
    );
    border-radius: 16px;
    padding: 1px;
    border: 1px solid rgba(88,163,255,0.35);
    box-shadow:
        0 0 18px rgba(88,163,255,0.15),
        inset 0 0 12px rgba(88,163,255,0.06);
    overflow: hidden;
    margin-bottom: 10px;
    height: 70vh;
}

.mke-chart {
    overflow: hidden;
    height: 20vh;
}

.kpi-label {
    font-size: 13px;
    color: #9FB7D6;
    letter-spacing: 0.4px;
    margin-bottom: 2px;     /* reduces spacing below the label */
    line-height: 1.1;
}

.kpi-value {
    font-size: 34px;
    line-height: 1.1;       /* tighter line height */
    margin-bottom: 1px;
    font-weight: 700;
    color: #F5EEDC;
}
</style>
"""

# Constants 
OFFENSE_COLS = [
    "Arson","AssaultOffense","Burglary","CriminalDamage","Homicide",
    "LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"
]

OFFENSE_COLORS = {
    "Arson": "#FF6F61",
    "AssaultOffense": "#C44536",
    "Burglary": "#7A5195",
    "CriminalDamage": "#8C4A3A",
    "Homicide": "#000000",
    "LockedVehicle": "#FFD700",
    "Robbery": "#FFB400",
    "SexOffense": "#FF69B4",
    "Theft": "#D4A373",
    "VehicleTheft": "#4A6FA5"
}

MILWAUKEE_THEME = {
    "text": "#E8E6DF",
    "cream": "#F1E9D2",
    "grid": "#22384A"
}

# Helper functions
def apply_css():
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def apply_mke_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=MILWAUKEE_THEME["text"]),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(color=MILWAUKEE_THEME["cream"], size=15)
        ),
        margin=dict(t=36, b=24, l=24, r=24)
    )
    fig.update_xaxes(gridcolor=MILWAUKEE_THEME["grid"])
    fig.update_yaxes(gridcolor=MILWAUKEE_THEME["grid"])
    return fig
    
# Load the dashboards data
@st.cache_data(show_spinner=False)
def load_crime_data(crimes_path="data/processed/crimes_joined.csv",
                    year=None):
    df = pd.read_csv(crimes_path)
    return df


@st.cache_resource
def load_neighborhoods(path="data/raw/geo/neighborhood/neighborhood.shp"):
    return gpd.read_file(path).to_crs(epsg=4326)
    
# Kpis
def compute_kpis(df, df_year, selected_year):
    total_crimes = len(df)
    this_year_count = len(df_year)
    
    previous_year = selected_year - 1
    percent_html, color, sign = "none", "transparent", ""
    
    if previous_year in df['Year'].values:
        prev_count = len(df[df['Year']==previous_year])
        percent_change = ((this_year_count - prev_count) / prev_count) * 100
        if percent_change >= 0:
            color, sign = "red", "+"
        else:
            color, sign = "green", ""
        percent_html = f'({sign}{percent_change:.1f}%)'
    
    return total_crimes, this_year_count, percent_html, color

def create_kpi_cards(total_crimes, this_year_count, percent_html, color):
    kpi_md = f"""
    <div class="mke-card" style="display:flex; align-items:center; padding:8px 12px; height:95px;">
        <div>
            <div class="kpi-label">Total Crimes</div>
            <div class="kpi-value">{total_crimes:,}</div>
        </div>
    </div>
    
    <div class="mke-card" style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; height:95px;">
        <div>
            <div class="kpi-label">Crimes in Selected Year</div>
            <div class="kpi-value">{this_year_count:,}</div>
        </div>
        <div style="font-size:18px; font-weight:700; color:{color};">
            {percent_html}
        </div>
    </div>
    """
    st.markdown(kpi_md, unsafe_allow_html=True)

# Heatmap
def create_heatmap(df):
    month_abbr = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    heat_data = df.groupby(["Year","Month"]).size().reset_index(name="Count")
    heat_data["MonthName"] = heat_data["Month"].apply(lambda m: month_abbr[m-1])
    all_years = sorted(df["Year"].unique())
    heat_data["Year"] = pd.Categorical(heat_data["Year"], categories=all_years, ordered=True)

    fig = px.density_heatmap(
        heat_data,
        x="MonthName",
        y="Year",
        z="Count",
        title="Incidents by Month & Year",
        color_continuous_scale="RdBu_r"
        
    )
    fig.update_yaxes(type='category', dtick=1)
    zmin, zmax = heat_data["Count"].min(), heat_data["Count"].max()
    fig.update_coloraxes(
        colorbar=dict(
            title=None,
            tickvals=[zmin, zmax],
            orientation="h",   # horizontal colorbar
            thickness=8,      # height in pixels
            len=0.88,           # width relative to plot
            #x=0.5,
            xanchor="center",
            y=1,           # push below the plot
            tickmode="array",
            ticks="outside",
            ticklabelposition="outside top"
        )
    )

    fig.update_layout(margin=dict(b=80), height=400)
    fig.update_xaxes(title_text="Month",showgrid=False)
    return apply_mke_theme(fig)

# Pie chart
def create_pie_chart(df_year, selected_year):
    offense_totals = df_year[OFFENSE_COLS].sum().reset_index()
    offense_totals.columns = ["Offense", "Count"]

    title_suffix = f"in {selected_year}" if selected_year != "All years" else "(All Years)"

    fig = px.pie(
        offense_totals,
        names="Offense",
        values="Count",
        color="Offense",
        color_discrete_map=OFFENSE_COLORS,
        hole=0.6,
        title=f"Offense Distribution {title_suffix}"
    )

    fig.update_layout(
        height=220,
        legend_title_text="Offense Type",
        legend=dict(
            font=dict(size=10, color="#9FB7D6"),
            orientation="v",
            yanchor="top",
            y=0.1,
            x=1.2,
            xanchor="left",
            traceorder="normal"
        ),
        margin=dict(t=50, b=50, l=20, r=20)
    )
    fig = apply_mke_theme(fig)
    
    return fig

# Day chart
def create_day_chart(df_year, selected_year):
    weekday_order = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    
    day_counts = df_year["Weekday"].value_counts().reindex(weekday_order).reset_index()
    day_counts.columns = ["Day","Count"]

    title_suffix = f"in {selected_year}" if selected_year != "All years" else "(All Years)"

    fig = px.bar(
        day_counts,
        x="Count",
        y="Day",
        orientation="h",
        title=f"Incidents Reported by Day {title_suffix}"
    )

    fig.update_layout(height=190)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(title_text="# of Incidents", showgrid=False)

    return apply_mke_theme(fig)

# Hour chart
def create_hour_chart(df_year, selected_year):

    hour_counts = df_year["Hour"].value_counts().sort_index().reset_index()
    hour_counts.columns = ["Hour","Count"]

    title_suffix = f"in {selected_year}" if selected_year != "All years" else "(All Years)"

    fig = px.bar(
        hour_counts,
        x="Hour",
        y="Count",
        title=f"Incidents Reported by Hour of Day {title_suffix}"
    )

    fig.update_layout(height=190)
    fig.update_yaxes(title_text="# of Incidents", showgrid=False)
    fig.update_xaxes(showgrid=False)

    return apply_mke_theme(fig)

# Map
def create_map(df_year, selected_year, neighborhoods):
    geojson = json.loads(neighborhoods.to_json())

    neigh_totals = df_year.groupby("NEIGHBORHD")[OFFENSE_COLS].sum()
    top_offense = neigh_totals.idxmax(axis=1).reset_index()
    top_offense.columns = ["Neighborhood", "Most Common Offense"]

    bounds = neighborhoods.total_bounds
    center = {"lat": (bounds[1] + bounds[3]) / 2, "lon": (bounds[0] + bounds[2]) / 2}

    title_suffix = f"in {selected_year}" if selected_year != "All years" else "(All Years)"

    fig = px.choropleth_mapbox(
        top_offense,
        geojson=geojson,
        locations="Neighborhood",
        featureidkey="properties.NEIGHBORHD",
        color="Most Common Offense",
        color_discrete_map=OFFENSE_COLORS,
        mapbox_style="carto-darkmatter",
        zoom=9.3,
        center=center,
        opacity=0.65,
        title=f"Most Common Offense in Neighborhoods {title_suffix}"
    )
    fig.update_layout(
        height=600,
        legend_title_text="Offense Type",
        legend=dict(font=dict(size=10, color="#9FB7D6"))
    )

    return apply_mke_theme(fig)

# Create Dashboard
def main():
    #Apply css
    apply_css()

    #Header 
    title_col, filter_col = st.columns([5, 1])
    with title_col:
        st.markdown("<h1 style='margin:0;'>Milwaukee Crime Dashboard</h1>", unsafe_allow_html=True)

    #Year filter 
    df = load_crime_data()
    all_years = sorted(df["Year"].unique())
    year_options = ["All years"] + all_years
    
    with filter_col:
        selected_year = st.selectbox("Year", year_options, index=len(year_options)-1)  # default latest year

    neighborhoods = load_neighborhoods()
    
    if selected_year == "All years":
        df_year = df.copy()
    else:
        df_year = df[df["Year"] == int(selected_year)]
    
    #KPIs and Heatmap
    if selected_year == "All years":
        total_crimes, this_year_count = len(df), len(df_year)
        percent_html, color = "none", "transparent"  # hide percent change
    else:
        total_crimes, this_year_count, percent_html, color = compute_kpis(df, df_year, int(selected_year))

    
    left_col, center_col, right_col = st.columns([1.0, 1.2, 1.4], border=True, vertical_alignment="top")
    
    with left_col:
        create_kpi_cards(total_crimes, this_year_count, percent_html, color)
        st.plotly_chart(create_heatmap(df))
        
    #Charts
    with center_col:
        st.plotly_chart(create_pie_chart(df_year, selected_year))
        st.plotly_chart(create_day_chart(df_year, selected_year))
        st.plotly_chart(create_hour_chart(df_year, selected_year))
    #Map
    with right_col:
        st.plotly_chart(create_map(df_year, selected_year, neighborhoods))

if __name__ == "__main__":
    main()