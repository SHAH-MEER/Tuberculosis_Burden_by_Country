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

    # Add a box plot for TB Prevalence distribution
    st.subheader("Distribution of TB Prevalence (Box Plot)")
    box_fig = px.box(
        df,
        x='region',
        y='tb_prevalence_100k',
        color='region',
        title="TB Prevalence per 100k by Region (Box Plot)",
        points="all"
    )
    st.plotly_chart(box_fig)
    st.divider()

    # Add a scatter plot for TB Prevalence vs. Mortality
    st.subheader("Prevalence vs. Mortality (Scatter Plot)")
    scatter_fig = px.scatter(
        df,
        x='tb_prevalence_100k',
        y='tb_mortality_100k',
        color='region',
        hover_name='country',
        title="TB Prevalence vs. Mortality by Country",
        size='population',
        size_max=40
    )
    st.plotly_chart(scatter_fig)

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

    # Add a line chart for TB Prevalence trend for selected countries
    st.subheader("TB Prevalence Trend (Line Chart)")
    if not filtered_df.empty:
        line_fig = px.line(
            df[df['country'].isin(selected_country)],
            x='year',
            y='tb_prevalence_100k',
            color='country',
            title="TB Prevalence Trend for Selected Countries"
        )
        st.plotly_chart(line_fig)
    st.divider()

    # Add a heatmap for TB Prevalence by country and year
    st.subheader("TB Prevalence Heatmap")
    heatmap_data = df[df['country'].isin(selected_country)].pivot_table(index='country', columns='year', values='tb_prevalence_100k')
    heatmap_fig = px.imshow(
        heatmap_data,
        labels=dict(x="Year", y="Country", color="Prevalence per 100k"),
        title="TB Prevalence Heatmap (Country vs Year)"
    )
    st.plotly_chart(heatmap_fig)

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

    # Add a dual-axis line chart for Incidence and Mortality
    st.subheader("Incidence vs. Mortality (Dual Axis)")
    if not trend_df.empty:
        dual_axis_fig = px.line(
            trend_df,
            x='year',
            y=['tb_incidence_100k', 'tb_mortality_100k'],
            title=f"Incidence vs. Mortality Over Time in {trend_country}",
            labels={"value": "Rate per 100k", "variable": "Metric"}
        )
        st.plotly_chart(dual_axis_fig)
    st.divider()

    # Add a histogram for TB Incidence
    st.subheader("Incidence Rate Distribution (Histogram)")
    hist_fig = px.histogram(
        trend_df,
        x='tb_incidence_100k',
        nbins=20,
        title=f"Distribution of TB Incidence Rates in {trend_country}"
    )
    st.plotly_chart(hist_fig)

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

    # Add a pie chart for TB Deaths by country in the region
    st.subheader(f"TB Deaths by Country in {selected_region} (Pie Chart)")
    pie_deaths = px.pie(
        regional_df,
        names='country',
        values='tb_deaths_total',
        title=f"TB Deaths Distribution in {selected_region}"
    )
    st.plotly_chart(pie_deaths)
    st.divider()

    # Add a box plot for TB Incidence in the region
    st.subheader(f"TB Incidence Distribution in {selected_region} (Box Plot)")
    box_incidence = px.box(
        regional_df,
        y='tb_incidence_100k',
        points="all",
        title=f"TB Incidence per 100k in {selected_region} (Box Plot)"
    )
    st.plotly_chart(box_incidence)

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

        # Add a bar chart for deaths, prevalence, and incidence totals
        st.subheader("Total TB Metrics (Bar Chart)")
        bar_totals = px.bar(
            x=["Prevalence", "Incidence", "Deaths"],
            y=[country_df['tb_prevalence_total'].sum(), country_df['tb_incident_cases_total'].sum(), country_df['tb_deaths_total'].sum()],
            labels={"x": "Metric", "y": "Total"},
            title=f"Total TB Metrics for {selected_country_profile}"
        )
        st.plotly_chart(bar_totals)

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

        # Add a scatter plot for Prevalence vs. Incidence over years
        st.subheader("Prevalence vs. Incidence Over Years (Scatter Plot)")
        scatter_profile = px.scatter(
            country_df,
            x='tb_prevalence_100k',
            y='tb_incidence_100k',
            color='year',
            title=f"Prevalence vs. Incidence Over Years in {selected_country_profile}",
            labels={"x": "Prevalence per 100k", "y": "Incidence per 100k"}
        )
        st.plotly_chart(scatter_profile)

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

    # Add a violin plot for TB Prevalence by region
    st.subheader("TB Prevalence by Region (Violin Plot)")
    violin_fig = px.violin(
        explorer_df,
        x='region',
        y='tb_prevalence_100k',
        box=True,
        points="all",
        title="TB Prevalence by Region (Violin Plot)"
    )
    st.plotly_chart(violin_fig)
    st.divider()

    # Add a line chart for average TB Prevalence over years (filtered)
    st.subheader("Average TB Prevalence Over Years (Filtered)")
    if not explorer_df.empty:
        avg_year = explorer_df.groupby('year')['tb_prevalence_100k'].mean().reset_index()
        avg_line = px.line(
            avg_year,
            x='year',
            y='tb_prevalence_100k',
            title="Average TB Prevalence Over Years (Filtered)"
        )
        st.plotly_chart(avg_line)

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


