import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd

st.set_page_config(
    page_title="Soil Dataset Analytical Dashboard",
    layout="wide"
)

# ------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, low_memory=False)

    # Create year column safely
    if "sampling_date" in df.columns:
        df["year"] = pd.to_numeric(df["sampling_date"], errors="coerce")

    return df

DATA_PATH = "/home/agbelgaid/Documents/WORKSPACE/DataCollection/SoilHive/data/combined_output_data_points.csv"

def add_country_information(df):

    if "lat" not in df.columns or "lon" not in df.columns:
        raise ValueError("lat/lon columns are required")

    world = gpd.read_file(
        "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    )

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

    return joined.drop(columns=["geometry", "index_right"], errors="ignore")

df = load_data(DATA_PATH)
df = add_country_information(df)
# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------
st.sidebar.title("Filters")

year_min = int(df["year"].min())
year_max = int(df["year"].max())

selected_year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

df = df[
    (df["year"] >= selected_year_range[0]) &
    (df["year"] <= selected_year_range[1])
]

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.title("Global Soil Dataset — Analytical Dashboard")
st.caption("Professional overview of geographic, structural, and temporal characteristics")


# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
(tab1,) = st.tabs([
    "Executive Overview",
])

# ============================================================
# TAB 1 — EXECUTIVE OVERVIEW
# ============================================================
with tab1:

    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", f"{len(df):,}")

    if "country" in df.columns:
        col2.metric("Countries", df["country"].nunique())
    else:
        col2.metric("Countries", "Not available")

    col3.metric("Features", df["property"].nunique())
    col4.metric(
        "Years Covered",
        f"{int(df['year'].min())}–{int(df['year'].max())}"
    )

    st.markdown("---")

    # ---------------------------------------------------
    # Top 10 Countries
    # ---------------------------------------------------
    top_countries = (
        df.groupby("country")
        .size()
        .reset_index(name="records")
        .sort_values("records", ascending=False)
        .head(10)
    )

    fig1 = px.bar(
        top_countries,
        x="records",
        y="country",
        orientation="h",
        title="Top 10 Countries by Records"
    )

    fig1.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------
    # Feature Distribution — Top 10 Countries
    # ---------------------------------------------------
    st.subheader("Feature Distribution — Top 10 Countries")

    top_10_countries = (
        df.groupby("country")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .index
    )

    df_top10 = df[df["country"].isin(top_10_countries)]

    feature_country = (
        df_top10
        .groupby(["country", "property"])
        .size()
        .reset_index(name="records")
    )

    fig = px.bar(
        feature_country,
        x="records",
        y="property",
        color="records",
        orientation="h",
        facet_col="country",
        facet_col_wrap=2,
        color_continuous_scale="Viridis",
        title="Feature Distribution per Country"
    )

    fig.update_layout(height=1200, showlegend=False)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------
    # Country Deep Dive
    # ---------------------------------------------------
    st.header("Country Deep Dive")

    country_list = (
        df.groupby("country")
        .size()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    selected_country = st.selectbox(
        "Select a Country",
        country_list
    )

    df_country = df[df["country"] == selected_country]

    st.markdown("### Country Summary")

    colA, colB, colC = st.columns(3)

    colA.metric("Total Records", f"{len(df_country):,}")
    colB.metric("Number of Features", df_country["property"].nunique())
    colC.metric(
        "Years Covered",
        f"{int(df_country['year'].min())} – {int(df_country['year'].max())}"
    )

    col_left, col_right = st.columns(2)

    # LEFT — Feature Distribution
    with col_left:
        st.subheader("Feature Distribution")

        feature_counts = (
            df_country
            .groupby("property")
            .size()
            .reset_index(name="records")
            .sort_values("records", ascending=False)
        )

        fig_features = px.bar(
            feature_counts,
            x="records",
            y="property",
            orientation="h",
            color="records",
            color_continuous_scale="Viridis",
            text="records",
            title=f"{selected_country} — Records by Feature"
        )

        fig_features.update_layout(
            yaxis=dict(autorange="reversed"),
            height=500
        )

        fig_features.update_traces(textposition="outside")

        st.plotly_chart(fig_features, use_container_width=True)

    # RIGHT — Temporal Evolution
    with col_right:
        st.subheader("Temporal Evolution")

        yearly_counts = (
            df_country
            .groupby("year")
            .size()
            .reset_index(name="records")
            .sort_values("year")
        )

        fig_year = px.line(
            yearly_counts,
            x="year",
            y="records",
            markers=True,
            title=f"{selected_country} — Records per Year"
        )

        fig_year.update_layout(height=500)

        st.plotly_chart(fig_year, use_container_width=True)

    # Feature × Year Evolution
    st.subheader("Feature Evolution Over Time")

    feature_year = (
        df_country
        .groupby(["year", "property"])
        .size()
        .reset_index(name="records")
    )

    fig_feature_year = px.area(
        feature_year,
        x="year",
        y="records",
        color="property",
        title=f"{selected_country} — Feature Contribution Over Time"
    )

    fig_feature_year.update_layout(height=500)

    st.plotly_chart(fig_feature_year, use_container_width=True)