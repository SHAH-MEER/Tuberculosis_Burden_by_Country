import streamlit as st
import pandas as pd
import plotly.express as px


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


# Add latitude and longitude columns using geopy (asynchronous version)

df = load_data()

# Ensure latitude and longitude columns are added to the DataFrame


# Add a custom theme and improve layout aesthetics
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar navigation
st.sidebar.title("Navigation")
pages = ["Documentation", "Global Overview", "Country Comparison", "Trends Over Time", "Regional Analysis", "Country Profiles", "Interactive Data Explorer"]
selected_page = st.sidebar.radio("Go to", pages)

if selected_page == "Global Overview":
    st.title("🌍 Global Overview")
    st.markdown("""
    This page provides a global overview of TB prevalence and mortality.
    """)

    # Add dropdown for page purpose
    with st.expander("What is the purpose of this page?"):
        st.write("This page provides a high-level summary of global TB statistics, including total population, TB prevalence, and TB deaths. It also includes visualizations to explore TB distribution by region and country.")

    # Display key metrics
    st.subheader("Global Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Population", f"{round(df['population'].sum()/23):,}") 
    with col2:
        st.metric("Total TB Prevalence", f"{round(df['tb_prevalence_total'].sum()/23):,}")
    with col3:
        st.metric("Total TB Deaths", f"{round(df['tb_deaths_total'].sum()/23):,}")

    # Add dropdown for metric explanation
    with st.expander("What do these metrics mean?"):
        st.write("""
        - **Total Population**: The total population across all countries in the dataset.
        - **Total TB Prevalence**: The total number of TB cases (all forms) across all countries.
        - **Total TB Deaths**: The total number of deaths caused by TB (excluding HIV) across all countries.
        """)

    # Update the Plotly map to color the countries instead of using blobs
    st.subheader("Global TB Prevalence Map")
    map_fig = px.choropleth(
        df,
        locations="iso3",
        color="tb_prevalence_100k",
        hover_name="country",
        projection="equirectangular",
        title="Global TB Prevalence by Country",
        color_continuous_scale=px.colors.sequential.Magma_r
    )
    st.plotly_chart(map_fig)

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

    # Add dropdown for page purpose
    with st.expander("What is the purpose of this page?"):
        st.write("This page allows users to compare TB statistics across selected countries for a specific year.")

    # Add filter options to the Country Comparison page
    st.subheader("Filter Options")
        color='country',
        color_discrete_sequence=px.colors.sequential.Plasma,
    )
    st.plotly_chart(top_bar)

elif selected_page == "Country Comparison":
    st.title("📊 Country Comparison")

    # Add filter options to the Country Comparison page
    st.subheader("Filter Options")
    selected_year = st.selectbox("Select Year", sorted(df['year'].unique(), reverse=True))
    selected_country = st.multiselect("Select Country", df['country'].unique(), default=["India", "Pakistan", "China"])

    # Filtered data
    filtered_df = df[(df['year'] == selected_year) & (df['country'].isin(selected_country))]
    if st.button("Show Filtered Data"):
        st.write(filtered_df)

    # Add visualizations
    st.subheader("TB Incidence per Country")
    fig1 = px.bar(
        filtered_df,
        x='country',
        y='tb_prevalence_100k',
        color='country',
        title="Estimated TB Incidence per 100,000",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig1)

    st.subheader("TB Mortality per Country")
    fig2 = px.bar(
        filtered_df,
        x='country',
        y='tb_mortality_100k',
        color='country',
        title="Estimated TB Mortality per 100,000",
        color_discrete_sequence=px.colors.sequential.Cividis
    )
    st.plotly_chart(fig2)

elif selected_page == "Trends Over Time":
    st.title("📈 Trends Over Time")
    trend_country = st.selectbox("Select Country for Trend", df['country'].unique())
    trend_df = df[df['country'] == trend_country]

    st.subheader(f"TB Incidence Trend in {trend_country}")
    fig3 = px.line(
        trend_df,
        x='year',
        y='tb_incidence_100k',
        title=f"TB Incidence Trend in {trend_country}",
        color_discrete_sequence=["#636EFA"]
    )
    st.plotly_chart(fig3)

    st.subheader(f"TB Mortality Trend in {trend_country}")
    fig4 = px.line(
        trend_df,
        x='year',
        y='tb_mortality_100k',
        title=f"TB Mortality Trend in {trend_country}",
        color_discrete_sequence=["#EF553B"]
    )
    st.plotly_chart(fig4)

    st.subheader("Heatmap of TB Prevalence by Region and Year")
    heatmap_data = df.groupby(['region', 'year'])['tb_prevalence_100k'].mean().reset_index()
    heatmap_fig = px.density_heatmap(
        heatmap_data,
        x='year',
        y='region',
        z='tb_prevalence_100k',
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Heatmap of TB Prevalence by Region and Year"
    )
    st.plotly_chart(heatmap_fig)

    st.subheader("Bubble Chart for TB Incidence vs. Mortality")
    bubble_fig = px.scatter(
        df,
        x='tb_incidence_100k',
        y='tb_mortality_100k',
        size='population',
        color='region',
        hover_name='country',
        title="Bubble Chart for TB Incidence vs. Mortality",
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(bubble_fig)

    st.subheader("Stacked Bar Chart for Regional TB Statistics")
    stacked_data = df.groupby('region')[['tb_prevalence_total', 'tb_incident_cases_total', 'tb_deaths_total']].sum().reset_index()
    stacked_fig = px.bar(
        stacked_data,
        x='region',
        y=['tb_prevalence_total', 'tb_incident_cases_total', 'tb_deaths_total'],
        title="Stacked Bar Chart for Regional TB Statistics",
        labels={"value": "Count", "variable": "Metric"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(stacked_fig)

elif selected_page == "Regional Analysis":
    st.title("🌎 Regional Analysis")
    selected_region = st.selectbox("Select Region", df['region'].unique())
    regional_df = df[df['region'] == selected_region]

    st.subheader(f"TB Prevalence in {selected_region}")
    region_fig = px.bar(
        regional_df,
        x='country',
        y='tb_prevalence_100k',
        color='country',
        title=f"TB Prevalence in {selected_region}",
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )
    st.plotly_chart(region_fig)

    st.subheader(f"TB Mortality in {selected_region}")
    region_mortality_fig = px.bar(
        regional_df,
        x='country',
        y='tb_mortality_100k',
        color='country',
        title=f"TB Mortality in {selected_region}",
        color_discrete_sequence=px.colors.sequential.OrRd
    )
    st.plotly_chart(region_mortality_fig)

elif selected_page == "Country Profiles":
    st.title("🌍 Country Profiles")
    selected_country_profile = st.selectbox("Select a Country", df['country'].unique())
    country_df = df[df['country'] == selected_country_profile]

    st.subheader(f"Detailed Statistics for {selected_country_profile}")
    st.write(country_df)

    st.subheader(f"Trends for {selected_country_profile}")
    fig = px.line(
        country_df,
        x='year',
        y=['tb_prevalence_100k', 'tb_mortality_100k', 'tb_incidence_100k'],
        title=f"Trends in TB Statistics for {selected_country_profile}",
        labels={"value": "Rate per 100k", "variable": "Metric"},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig)

elif selected_page == "Interactive Data Explorer":
    st.title("🔍 Interactive Data Explorer")
    st.markdown("""
    Use the filters below to explore the dataset interactively.
    """)

    # Add filters for interactive exploration
    selected_region = st.multiselect("Select Region", df['region'].unique(), default=df['region'].unique())
    selected_years = st.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

    explorer_df = df[(df['region'].isin(selected_region)) & (df['year'].between(*selected_years))]
    st.write(explorer_df)

    st.subheader("Custom Query Results")
    query = st.text_area("Enter a custom query (e.g., `tb_prevalence_100k > 100`)")
    if query:
        try:
            # Validate the query string before execution
            if any(keyword in query.lower() for keyword in ["import", "exec", "eval", "os.", "sys."]):
                raise ValueError("Invalid query: Potentially unsafe operations detected.")

            query_results = explorer_df.query(query)
            st.write(query_results)

            # Update visuals based on query results
            if not query_results.empty:
                st.markdown("### TB Prevalence by Region")
                region_fig = px.bar(
                    query_results.groupby('region').sum().reset_index(),
                    x='region',
                    y='tb_prevalence_total',
                    title="TB Prevalence by Region",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(region_fig)

                st.markdown("### TB Incidence vs. Mortality")
                bubble_fig = px.scatter(
                    query_results,
                    x='tb_incidence_100k',
                    y='tb_mortality_100k',
                    size='population',
                    color='region',
                    hover_name='country',
                    title="TB Incidence vs. Mortality",
                    size_max=60,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(bubble_fig)

                st.markdown("### Stacked Bar Chart for Regional TB Statistics")
                stacked_data = query_results.groupby('region')[['tb_prevalence_total', 'tb_incident_cases_total', 'tb_deaths_total']].sum().reset_index()
                stacked_fig = px.bar(
                    stacked_data,
                    x='region',
                    y=['tb_prevalence_total', 'tb_incident_cases_total', 'tb_deaths_total'],
                    title="Stacked Bar Chart for Regional TB Statistics",
                    labels={"value": "Count", "variable": "Metric"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(stacked_fig)
            else:
                st.warning("No data matches the query. Please adjust your query and try again.")
        except Exception as e:
            st.error(f"Error in query: {e}. Please ensure your query is valid and uses column names correctly.")

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
    - **Country Profiles:** Detailed statistics and trends for individual countries.
    - **Interactive Data Explorer:** Explore the dataset interactively with custom queries.

    ### Recent Updates:
    - **[May 2025]** Added a Plotly-based interactive map for the Global Overview page.
    - **[May 2025]** Integrated geocoding to fetch latitude and longitude for countries.
    - **[May 2025]** Added Country Profiles and Interactive Data Explorer pages.
    - **[May 2025]** Added heatmap, bubble chart, and stacked bar chart visuals.

    ### How to Use:
    1. Use the sidebar to navigate between pages.
    2. Filter data by year and country using the sidebar filters.
    3. Explore interactive visualizations and insights on each page.

    ### Data Source:
    - World Health Organization (WHO)

    ### Contact:
    For questions or feedback, please contact [shahmeershahzad67@gmail.com].
    """)


