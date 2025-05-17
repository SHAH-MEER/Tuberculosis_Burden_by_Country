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
        st.metric(
            "Total Population",
            f"{round(df['population'].sum()/23):,}",
            help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
        )
    with col2:
        st.metric(
            "Total TB Prevalence",
            f"{round(df['tb_prevalence_total'].sum()/23):,}",
            help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
        )
    with col3:
        st.metric(
            "Total TB Deaths",
            f"{round(df['tb_deaths_total'].sum()/23):,}",
            help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
        )
    st.divider()

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
    st.divider()

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
    st.divider()

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
    # Metrics at the top
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Population", f"{round(df['population'].sum()/23):,}")
    with col2:
        st.metric("Total TB Prevalence", f"{round(df['tb_prevalence_total'].sum()/23):,}")
    with col3:
        st.metric("Total TB Deaths", f"{round(df['tb_deaths_total'].sum()/23):,}")
    st.divider()

    # Add dropdown for page purpose
    with st.expander("What is the purpose of this page?"):
        st.write("This page allows users to compare TB statistics across selected countries for a specific year.")

    # Add filter options to the Country Comparison page
    st.subheader("Filter Options")
    selected_year = st.selectbox("Select Year", sorted(df['year'].unique(), reverse=True))
    selected_country = st.multiselect("Select Country", df['country'].unique(), default=["India", "Pakistan", "China"])

    # Filtered data
    filtered_df = df[(df['year'] == selected_year) & (df['country'].isin(selected_country))]
    if st.button("Show Filtered Data"):
        st.write(filtered_df)

    # Add dropdown for metric explanation
    with st.expander("What do these metrics mean?"):
        st.write("""
        - **TB Incidence per Country**: The estimated number of TB cases per 100,000 population for each selected country.
        - **TB Mortality per Country**: The estimated number of TB deaths per 100,000 population for each selected country.
        """)

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
    st.divider()

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
    # Metrics at the top (for selected country)
    trend_country = st.selectbox("Select Country for Metrics", df['country'].unique(), key="trend_metrics")
    trend_df = df[df['country'] == trend_country]
    st.subheader(f"Key Metrics for {trend_country}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Population",
            f"{round(trend_df['population'].sum()/23):,}",
            help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
        )
    with col2:
        st.metric(
            "Total TB Prevalence",
            f"{round(trend_df['tb_prevalence_total'].sum()/23):,}",
            help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
        )
    with col3:
        st.metric(
            "Total TB Deaths",
            f"{trend_df['tb_deaths_total'].sum():,}"
        )
    st.divider()

    # Add tabs for different trend visualizations
    tab1, tab2 = st.tabs(["Incidence Trends", "Mortality Trends"])

    with tab1:
        st.subheader("Incidence Trends")
        trend_country = st.selectbox("Select Country for Incidence Trend", df['country'].unique())
        trend_df = df[df['country'] == trend_country]
        col1, col2, col3 = st.columns(3)
        with col2:
            st.metric("Average Incidence Rate", f"{trend_df['tb_incidence_100k'].mean():.2f} per 100k")
        fig_incidence = px.line(
            trend_df,
            x='year',
            y='tb_incidence_100k',
            title=f"TB Incidence Trend in {trend_country}",
            color_discrete_sequence=["#636EFA"]
        )
        st.plotly_chart(fig_incidence)
        

        # Add a bar chart for yearly incidence
        st.subheader("Yearly Incidence Distribution")
        bar_fig = px.bar(
            trend_df,
            x='year',
            y='tb_incidence_100k',
            title=f"Yearly TB Incidence in {trend_country}",
            color_discrete_sequence=["#636EFA"]
        )
        st.plotly_chart(bar_fig)

    with tab2:
        st.subheader("Mortality Trends")
        trend_country = st.selectbox("Select Country for Mortality Trend", df['country'].unique(), key="mortality_trend")
        trend_df = df[df['country'] == trend_country]
        col1, col2, col3 = st.columns(3)
        with col2:
            st.metric("Average Mortality Rate", f"{trend_df['tb_mortality_100k'].mean():.2f} per 100k")
        fig_mortality = px.line(
            trend_df,
            x='year',
            y='tb_mortality_100k',
            title=f"TB Mortality Trend in {trend_country}",
            color_discrete_sequence=["#EF553B"]
        )
        st.plotly_chart(fig_mortality)

        # Add a scatter plot for mortality vs. incidence
        st.subheader("Mortality vs. Incidence")
        scatter_fig = px.scatter(
            trend_df,
            x='tb_incidence_100k',
            y='tb_mortality_100k',
            title=f"Mortality vs. Incidence in {trend_country}",
            labels={"x": "Incidence per 100k", "y": "Mortality per 100k"},
            color_discrete_sequence=["#EF553B"]
        )
        st.plotly_chart(scatter_fig)

elif selected_page == "Regional Analysis":
    st.title("🌎 Regional Analysis")
    selected_region = st.selectbox("Select Region", df['region'].unique())
    regional_df = df[df['region'] == selected_region]
    # Metrics at the top
    st.subheader(f"Key Metrics for {selected_region}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Population", f"{round(df['population'].sum()/23):,}")
    with col2:
        st.metric("Total TB Prevalence", f"{round(df['tb_prevalence_total'].sum()/23):,}")
    with col3:
        st.metric("Total TB Deaths", f"{round(df['tb_deaths_total'].sum()/23):,}")
    st.divider()

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

    # Add tabs for detailed statistics and trends
    tab1, tab2 = st.tabs(["Detailed Statistics", "Trends"])

    with tab1:
        selected_country_profile = st.selectbox("Select a Country", df['country'].unique())
        country_df = df[df['country'] == selected_country_profile]

        st.subheader(f"Key Metrics for {selected_country_profile}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Population",
                f"{round(country_df['population'].sum()/23):,}",
                help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
            )
        with col2:
            st.metric("Total TB Prevalence", f"{country_df['tb_prevalence_total'].sum():,}")
        with col3:
            st.metric("Total TB Deaths", f"{country_df['tb_deaths_total'].sum():,}")
        st.divider()

        st.subheader(f"Detailed Statistics for {selected_country_profile}")
        st.write(country_df)
        # Add a pie chart for prevalence, incidence, and mortality
        st.subheader("Proportion of TB Metrics")
        pie_data = {
            "Metric": ["Prevalence", "Incidence", "Mortality"],
            "Value": [
                country_df['tb_prevalence_total'].sum(),
                country_df['tb_incident_cases_total'].sum(),
                country_df['tb_deaths_total'].sum()
            ]
        }
        pie_fig = px.pie(
            pie_data,
            names="Metric",
            values="Value",
            title=f"Proportion of TB Metrics in {selected_country_profile}",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(pie_fig)

    with tab2:
        selected_country_profile = st.selectbox("Select a Country for Trends", df['country'].unique(), key="country_trends")
        country_df = df[df['country'] == selected_country_profile]

        st.subheader(f"Key Metrics for {selected_country_profile}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Population",
                f"{round(country_df['population'].sum()/23):,}",
                help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
            )
        with col2:
            st.metric(
                "Total TB Prevalence",
                f"{round(country_df['tb_prevalence_total'].sum()/23):,}",
                help="Normalized to a single year (data spans 23 years) to avoid unrealistic totals."
            )
        with col3:
            st.metric("Total TB Deaths", f"{country_df['tb_deaths_total'].sum():,}")
        st.divider()

        st.subheader(f"Trends for {selected_country_profile}")
        fig_trends = px.line(
            country_df,
            x='year',
            y=['tb_prevalence_100k', 'tb_mortality_100k', 'tb_incidence_100k'],
            title=f"Trends in TB Statistics for {selected_country_profile}",
            labels={"value": "Rate per 100k", "variable": "Metric"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_trends)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Prevalence Rate", f"{country_df['tb_prevalence_100k'].mean():.2f} per 100k")
        with col2:
            st.metric("Average Mortality Rate", f"{country_df['tb_mortality_100k'].mean():.2f} per 100k")
        with col3:
            st.metric("Average Incidence Rate", f"{country_df['tb_incidence_100k'].mean():.2f} per 100k")

        # Add a bar chart for yearly trends
        st.subheader("Yearly Trends")
        bar_trends = px.bar(
            country_df,
            x='year',
            y=['tb_prevalence_100k', 'tb_mortality_100k', 'tb_incidence_100k'],
            title=f"Yearly Trends in TB Metrics for {selected_country_profile}",
            labels={"value": "Rate per 100k", "variable": "Metric"},
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(bar_trends)

elif selected_page == "Interactive Data Explorer":
    st.title("🔍 Interactive Data Explorer")
     # Add dropdown for page purpose
    with st.expander("What is the purpose of this page?"):
        st.write("This page allows users to explore the dataset interactively by applying filters and custom queries. It also provides visualizations based on the filtered data.")

    # Add filters for interactive exploration
    selected_region = st.multiselect("Select Region", df['region'].unique(), default=df['region'].unique())
    selected_years = st.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

    explorer_df = df[(df['region'].isin(selected_region)) & (df['year'].between(*selected_years))]

    # Add dropdown for metric explanation
    with st.expander("What do these metrics mean?"):
        st.write("""
        - **Region**: The geographical region to which the country belongs.
        - **Year Range**: The range of years for which data is displayed.
        - **Custom Query Results**: Results based on user-defined conditions applied to the dataset.
        """)

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
    if st.button("Show Filtered Data"):
        st.write(explorer_df)
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

    ### How to Use:
    1. Use the sidebar to navigate between pages.
    2. Filter data by year and country using the sidebar filters.
    3. Explore interactive visualizations and insights on each page.

    ### Data Source:
    - World Health Organization (WHO)

    ### Contact:
    For questions or feedback, please contact [shahmeershahzad67@gmail.com].
    """)


