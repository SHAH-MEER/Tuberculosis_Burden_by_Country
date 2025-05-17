import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

st.set_page_config(layout="wide")
# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/TB_Burden_Country.csv")
    # Rename columns to shorter and more suitable names
    df = df.rename(columns={
        "Country or territory name": "country",
        "ISO 2-character country/territory code": "iso2",
        "ISO 3-character country/territory code": "iso3",
        "ISO numeric country/territory code": "iso_num",
        "Region": "region",
        "Year": "year",
        "Estimated total population number": "population",
        "Estimated prevalence of TB (all forms) per 100 000 population": "tb_prevalence_100k",
        "Estimated prevalence of TB (all forms) per 100 000 population, low bound": "tb_prevalence_100k_low",
        "Estimated prevalence of TB (all forms) per 100 000 population, high bound": "tb_prevalence_100k_high",
        "Estimated prevalence of TB (all forms)": "tb_prevalence_total",
        "Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population": "tb_mortality_100k",
        "Estimated mortality of TB cases (all forms, excluding HIV), per 100 000 population, low bound": "tb_mortality_100k_low",
        "Estimated mortality of TB cases (all forms, excluding HIV), per 100 000 population, high bound": "tb_mortality_100k_high",
        "Estimated number of deaths from TB (all forms, excluding HIV)": "tb_deaths_total",
        "Estimated number of deaths from TB (all forms, excluding HIV), low bound": "tb_deaths_low",
        "Estimated number of deaths from TB (all forms, excluding HIV), high bound": "tb_deaths_high",
        "Estimated incidence (all forms) per 100 000 population": "tb_incidence_100k",
        "Estimated incidence (all forms) per 100 000 population, low bound": "tb_incidence_100k_low",
        "Estimated incidence (all forms) per 100 000 population, high bound": "tb_incidence_100k_high",
        "Estimated number of incident cases (all forms)": "tb_incident_cases_total",
        "Estimated number of incident cases (all forms), low bound": "tb_incident_cases_low",
        "Estimated number of incident cases (all forms), high bound": "tb_incident_cases_high"
    })
    return df


df = load_data()


# Sidebar filters
st.sidebar.header("Filter Options")
years = df['year'].unique()
countries = df['country'].unique()

selected_year = st.sidebar.selectbox("Select Year", sorted(years, reverse=True))
selected_country = st.sidebar.multiselect("Select Country", countries, default=["India", "Pakistan", "China"])

# Filtered data
filtered_df = df[(df['year'] == selected_year) & (df['country'].isin(selected_country))]

# Sidebar navigation
st.sidebar.title("Navigation")
pages = ["Global Overview", "Country Comparison", "Trends Over Time", "Regional Analysis"]
selected_page = st.sidebar.radio("Go to", pages)

# Add a documentation page
if "Documentation" not in pages:
    pages.append("Documentation")

if selected_page == "Global Overview":
    st.title("🌍 Global Overview")
    st.markdown("""
    This page provides a global overview of TB prevalence and mortality.
    """)

    # Create a Folium map with Choropleth for TB prevalence
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add Choropleth layer for TB prevalence
    folium.Choropleth(
        geo_data=df.dropna(subset=['latitude', 'longitude']),
        data=df,
        columns=['country', 'tb_prevalence_100k'],
        key_on='feature.properties.country',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='TB Prevalence per 100k Population'
    ).add_to(m)

    # Add circle markers for each country
    valid_locations = df.dropna(subset=['latitude', 'longitude'])
    for _, row in valid_locations.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            popup=f"{row['country']}: {row['tb_prevalence_100k']} per 100k",
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    # Display the map
    st_folium(m, width=700, height=500)

    # Add a pie chart for TB prevalence by region
    st.subheader("TB Prevalence by Region")
    region_pie = px.pie(
        df.groupby('region').sum().reset_index(),
        names='region',
        values='tb_prevalence_total',
        title="TB Prevalence Distribution by Region",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(region_pie)

    # Add a bar chart for top 10 countries with highest TB prevalence
    st.subheader("Top 10 Countries with Highest TB Prevalence")
    top_countries = df.groupby('country').sum().reset_index().nlargest(10, 'tb_prevalence_total')
    top_bar = px.bar(
        top_countries,
        x='country',
        y='tb_prevalence_total',
        title="Top 10 Countries by TB Prevalence",
        color='country',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    st.plotly_chart(top_bar)

elif selected_page == "Country Comparison":
    st.title("📊 Country Comparison")
    st.subheader("TB Incidence per Country")
    fig1 = px.bar(filtered_df, x='country', y='tb_prevalence_100k', color='country', title="Estimated TB Incidence per 100,000")
    st.plotly_chart(fig1)

    st.subheader("TB Mortality per Country")
    fig2 = px.bar(filtered_df, x='country', y='tb_mortality_100k', color='country', title="Estimated TB Mortality per 100,000")
    st.plotly_chart(fig2)

elif selected_page == "Trends Over Time":
    st.title("📈 Trends Over Time")
    trend_country = st.selectbox("Select Country for Trend", countries)
    trend_df = df[df['country'] == trend_country]

    fig3 = px.line(trend_df, x='year', y='tb_incidence_100k', title=f"TB Incidence Trend in {trend_country}")
    st.plotly_chart(fig3)

elif selected_page == "Regional Analysis":
    st.title("🌎 Regional Analysis")
    selected_region = st.selectbox("Select Region", df['region'].unique())
    regional_df = df[df['region'] == selected_region]

    st.subheader("Regional TB Prevalence")
    region_fig = px.bar(regional_df, x='country', y='tb_prevalence_100k', color='country', title=f"TB Prevalence in {selected_region}")
    st.plotly_chart(region_fig)

    st.subheader("Regional TB Mortality")
    region_mortality_fig = px.bar(regional_df, x='country', y='tb_mortality_100k', color='country', title=f"TB Mortality in {selected_region}")
    st.plotly_chart(region_mortality_fig)

elif selected_page == "Documentation":
    st.title("📚 Documentation")
    st.markdown("""
    ## Global Tuberculosis (TB) Burden Dashboard

    This dashboard provides insights into the global burden of Tuberculosis (TB) using data from the World Health Organization (WHO).

    ### Features:
    - **Global Overview:** Interactive map showing TB prevalence and mortality by country.
    - **Country Comparison:** Bar charts comparing TB incidence and mortality across selected countries.
    - **Trends Over Time:** Line charts showing TB incidence trends for a selected country.
    - **Regional Analysis:** Bar charts analyzing TB prevalence and mortality by region.

    ### Recent Updates:
    - **[May 2025]** Added a Folium-based interactive map for the Global Overview page.
    - **[May 2025]** Integrated geocoding to fetch latitude and longitude for countries.
    - **[May 2025]** Added a Documentation page to track updates and features.

    ### How to Use:
    1. Use the sidebar to navigate between pages.
    2. Filter data by year and country using the sidebar filters.
    3. Explore interactive visualizations and insights on each page.

    ### Data Source:
    - World Health Organization (WHO)

    ### Contact:
    For questions or feedback, please contact [your_email@example.com].
    """)
