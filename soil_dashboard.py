"""
SoilHive — Global Soil Intelligence Dashboard
Professional geospatial analytics for global soil properties
"""

import warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="SoilHive — Global Soil Intelligence",
    layout="wide",
)

# ------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------
DEFAULT_DATA_PATH = "./data/combined_output_data_points.csv"

DEPTH_BINS   = [0, 5, 15, 30, 60, 100, 200, 10000]
DEPTH_LABELS = ["0-5", "5-15", "15-30", "30-60", "60-100", "100-200", ">200"]

COLOR_SEQ = "Viridis"
COLOR_DISC = px.colors.qualitative.Vivid

# ------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, low_memory=False)

    for col in ["sampling_date", "publication_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "sampling_date" in df.columns:
        df["year"] = df["sampling_date"].dt.year
    elif "publication_date" in df.columns:
        df["year"] = df["publication_date"].dt.year

    df["depth_mid"] = (df["upper_depth_cm"].fillna(0) + df["lower_depth_cm"].fillna(0)) / 2

    df["depth_interval"] = pd.cut(
        df["upper_depth_cm"].fillna(0),
        bins=DEPTH_BINS,
        labels=DEPTH_LABELS,
        right=False
    )

    return df

# ------------------------------------------------------------
# EXECUTIVE OVERVIEW
# ------------------------------------------------------------



@st.cache_data
def enrich_geography(df):

    if "lat" not in df.columns or "lon" not in df.columns:
        return df

    # URL officielle Natural Earth
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    world = gpd.read_file(url)

    world = world[["geometry", "ADMIN", "CONTINENT"]]
    world = world.rename(columns={
        "ADMIN": "country",
        "CONTINENT": "continent"
    })

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326"
    )

    joined = gpd.sjoin(gdf, world, how="left", predicate="within")

    joined["country"] = joined["country"].fillna("Unknown")
    joined["continent"] = joined["continent"].fillna("Unknown")

    return pd.DataFrame(
        joined.drop(columns=["geometry", "index_right"], errors="ignore")
    )
def render_executive_overview(df):

    st.subheader("Executive Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Countries", df["country"].nunique())
    c3.metric("Properties", df["property"].nunique())
    c4.metric("Years Covered", df["year"].nunique())

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        top_countries = (
            df.groupby("country")
              .size()
              .sort_values(ascending=False)
              .head(15)
              .reset_index(name="Records")
        )

        fig = px.bar(
            top_countries,
            x="Records",
            y="country",
            orientation="h",
            title="Top Countries by Records"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        feature_dist = (
            df.groupby("property")
              .size()
              .sort_values(ascending=False)
              .reset_index(name="Records")
        )

        fig2 = px.bar(
            feature_dist,
            x="property",
            y="Records",
            title="Global Property Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------
# GLOBAL COVERAGE
# ------------------------------------------------------------
def render_global_coverage(df):

    st.subheader("Global Temporal Coverage")

    df_year = df.dropna(subset=["year"])

    pivot = (
        df_year.groupby(["property", "year"])
               .size()
               .unstack(fill_value=0)
    )

    pivot_log = np.log1p(pivot)

    fig = px.imshow(
        pivot_log,
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(x="Year", y="Property", color="log(1 + count)")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    df_time = (
        df_year.groupby(["year", "property"])
               .size()
               .reset_index(name="Count")
    )

    fig2 = px.area(
        df_time,
        x="year",
        y="Count",
        color="property",
        title="Global Property Activity Over Time"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------
# COUNTRY INTELLIGENCE
# ------------------------------------------------------------
def render_country_intelligence(df):

    st.subheader("Country Intelligence")

    col_left, col_right = st.columns([1, 4])

    with col_left:
        countries = sorted(df["country"].unique())
        selected_country = st.selectbox("Select Country", countries)

        df_country = df[df["country"] == selected_country]

        st.metric("Records", f"{len(df_country):,}")
        st.metric("Properties", df_country["property"].nunique())
        st.metric("Years", df_country["year"].nunique())

    with col_right:

        df_map = df_country.dropna(subset=["lat", "lon"])

        fig = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            color="property",
            zoom=4,
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)

        df_time = (
            df_country.groupby(["year", "property"])
                      .size()
                      .reset_index(name="Count")
        )

        fig2 = px.area(
            df_time,
            x="year",
            y="Count",
            color="property"
        )

        st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------
# DEPTH ANALYSIS
# ------------------------------------------------------------
def render_depth_analysis(df):

    st.subheader("Depth Analysis")

    df_d = df.dropna(subset=["depth_interval"])

    fig = px.box(
        df_d,
        x="depth_interval",
        y="value",
        color="depth_interval"
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# SPATIAL INTELLIGENCE
# ------------------------------------------------------------
def render_spatial_intelligence(df):

    st.subheader("Spatial Intelligence")

    country_mean = (
        df.groupby("country")["value"]
          .mean()
          .reset_index()
    )

    fig = px.choropleth(
        country_mean,
        locations="country",
        locationmode="country names",
        color="value",
        color_continuous_scale="Viridis",
        projection="natural earth"
    )

    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    st.sidebar.title("SoilHive")
    data_path = st.sidebar.text_input("Data Path", DEFAULT_DATA_PATH)

    try:
        df = load_data(data_path)
        df = enrich_geography(df)
    except Exception as e:
        st.error("Error while loading dataset:")
        st.exception(e)
        st.stop()

    st.title("SoilHive — Global Soil Intelligence Dashboard")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Executive Overview",
        "Global Coverage",
        "Country Intelligence",
        "Depth Analysis",
        "Spatial Intelligence"
    ])

    with tab1:
        render_executive_overview(df)

    with tab2:
        render_global_coverage(df)

    with tab3:
        render_country_intelligence(df)

    with tab4:
        render_depth_analysis(df)

    with tab5:
        render_spatial_intelligence(df)

if __name__ == "__main__":
    main()