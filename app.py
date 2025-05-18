import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/combined_tb_data_1990_2023.csv")
    # Rename columns to shorter and more suitable names
    df = df.rename(columns={
        "country": "country",
        "iso2": "iso2",
        "iso3": "iso3",
        "iso_numeric": "iso_num",
        "region": "region",
        "year": "year",
        "population": "population",
        "incidence_rate": "tb_incidence_100k",
        "incidence_rate_lo": "tb_incidence_100k_low",
        "incidence_rate_hi": "tb_incidence_100k_high",
        "incidence_num": "tb_incident_cases_total",
        "incidence_num_lo": "tb_incident_cases_low",
        "incidence_num_hi": "tb_incident_cases_high",
        "mort_rate_no_hiv": "tb_mortality_100k",
        "mort_rate_no_hiv_lo": "tb_mortality_100k_low",
        "mort_rate_no_hiv_hi": "tb_mortality_100k_high",
        "hiv_in_tb_percent": "hiv_in_tb_percent",
        "hiv_in_tb_percent_lo": "hiv_in_tb_percent_lo",
        "hiv_in_tb_percent_hi": "hiv_in_tb_percent_hi",
        "detection_rate": "detection_rate",
        "detection_rate_lo": "detection_rate_lo",
        "detection_rate_hi": "detection_rate_hi"
    })
    return df


# Add latitude and longitude columns using geopy (asynchronous version)

df = load_data()

# Ensure latitude and longitude columns are added to the DataFrame


# Sidebar navigation
st.sidebar.title("Navigation")
pages = ["Documentation", "Global Overview", "Country Comparison", "Trends Over Time", "Regional Analysis", "Country Profiles", "Interactive Data Explorer", "Country Similarity Analysis", "Interactive Maps"]
selected_page = st.sidebar.radio("Go to", pages)

if selected_page == "Global Overview":
    st.title("🌍 Global Overview")
    st.markdown("""
    This page provides a global overview of TB prevalence and mortality, allowing you to explore the distribution and scale of TB across countries and regions. Use the interactive charts to identify high-burden areas and compare prevalence, mortality, and trends globally.
    """)
    with st.expander("What is the purpose of this page?"):
        st.write("""
        The Global Overview page summarizes TB statistics at a worldwide level. It includes:
        - **Key Metrics:** Normalized annual population, TB prevalence, and TB deaths for a realistic single-year snapshot.
        - **Interactive Map:** Visualize TB prevalence rates by country.
        - **Regional and Country Comparisons:** Pie, bar, box, and scatter plots to compare TB burden across regions and countries.
        - **Distribution Analysis:** Explore the spread and relationship between TB prevalence and mortality.
        Use this page to quickly identify global patterns and outliers in TB data.
        """)

    # Display key metrics
    st.subheader("Global Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Population",
            f"{round(df['population'].sum()/len(df['year'].unique())):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    with col2:
        st.metric(
            "Total TB Incidence",
            f"{round(df['tb_incident_cases_total'].sum()/len(df['year'].unique())):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    with col3:
        # Calculate actual deaths by using mortality rate and population, then normalize to a year
        total_deaths = (df['tb_mortality_100k'] * df['population'] / 100000).sum() / len(df['year'].unique())
        st.metric(
            "Total TB Deaths",
            f"{round(total_deaths):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    st.divider()

    # Add dropdown for metric explanation
    with st.expander("What do these metrics mean?"):
        st.write("""
        - **Total Population**: The total population across all countries in the dataset, normalized to a single year.
        - **Total TB Incidence**: The total number of new TB cases (all forms) across all countries, normalized to a single year.
        - **Total TB Deaths**: The total number of deaths caused by TB (excluding HIV) across all countries, normalized to a single year.
        """)

    # Update the Plotly map to color the countries instead of using blobs
    st.subheader("Global TB Incidence Map")
    map_fig = px.choropleth(
        df,
        locations="iso3",
        color="tb_incidence_100k",
        hover_name="country",
        projection="equirectangular",
        title="Global TB Incidence by Country",
        color_continuous_scale="Reds",
        range_color=[0, df['tb_incidence_100k'].quantile(0.95)],  # Cap at 95th percentile to highlight differences
        labels={"tb_incidence_100k": "Incidence per 100k"}
    )
    map_fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(map_fig, use_container_width=True)
    st.divider()

    # Add a pie chart for TB incidence by region
    st.subheader("TB Incidence by Region")
    # Use columns for side-by-side charts if space allows
    col_pie, col_top_bar = st.columns(2)
    with col_pie:
        st.subheader("TB Incidence by Region")
        region_pie = px.pie(
            df.groupby('region').sum().reset_index(),
            names='region',
            values='tb_incident_cases_total',
            title="TB Incidence Distribution by Region",
            color_discrete_sequence=px.colors.qualitative.Plotly, # Use Plotly qualitative palette
            hole=0.4  # Make it a donut chart
        )
        region_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(region_pie, use_container_width=True)

    # Add a bar chart for top 10 countries with highest TB incidence
    with col_top_bar:
        st.subheader("Top 10 Countries with Highest TB Incidence")
        top_countries = df.groupby('country').sum().reset_index().nlargest(10, 'tb_incident_cases_total')
        top_bar = px.bar(
            top_countries,
            x='country',
            y='tb_incident_cases_total',
            title="Top 10 Countries by TB Incidence",
            color='tb_incident_cases_total',
            color_continuous_scale="Viridis", # Use Viridis for sequential
            labels={"tb_incident_cases_total": "Total Cases", "country": "Country"}
        )
        top_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(top_bar, use_container_width=True)

    st.divider()

    # Add a box plot for TB Incidence distribution and scatter plot side-by-side
    col_box, col_scatter = st.columns(2)
    with col_box:
        st.subheader("TB Incidence Distribution by Region (Box Plot)")
        box_fig = px.box(
            df,
            x='region',
            y='tb_incidence_100k',
            color='region',
            title="TB Incidence per 100k by Region",
            points="outliers",
            color_discrete_sequence=px.colors.qualitative.Set3 # Use Set3 qualitative palette
        )
        box_fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(box_fig, use_container_width=True)

    with col_scatter:
        st.subheader("Incidence vs. Mortality (Scatter Plot)")
        scatter_fig = px.scatter(
            df,
            x='tb_incidence_100k',
            y='tb_mortality_100k',
            color='region',
            hover_name='country',
            title="TB Incidence vs. Mortality by Country",
            size='population',
            size_max=40,
            color_discrete_sequence=px.colors.qualitative.Set3, # Use Set3 qualitative palette
            labels={
                "tb_incidence_100k": "Incidence per 100k",
                "tb_mortality_100k": "Mortality per 100k"
            }
        )
        scatter_fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(scatter_fig, use_container_width=True)

    # Add a scatter plot for TB Mortality vs. HIV in TB globally
    st.subheader("Mortality vs. HIV in TB (Global Scatter Plot)")
    scatter_mortality_hiv = px.scatter(
        df,
        x='tb_mortality_100k',
        y='hiv_in_tb_percent',
        color='region',
        hover_name='country',
        title="TB Mortality vs. HIV in TB Percentage Globally",
        size='population', # Size points by population
        size_max=40,
        color_discrete_sequence=px.colors.qualitative.Set3, # Use Set3 qualitative palette
        labels={
            "tb_mortality_100k": "Mortality per 100k",
            "hiv_in_tb_percent": "HIV in TB (%)"
        }
    )
    scatter_mortality_hiv.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(scatter_mortality_hiv, use_container_width=True)

    # Add a scatter plot for Population vs. TB Incidence globally
    st.subheader("Population vs. TB Incidence (Global Scatter Plot)")
    scatter_pop_incidence = px.scatter(
        df,
        x='population',
        y='tb_incident_cases_total',
        color='region',
        hover_name='country',
        title="Population vs. Total TB Incident Cases Globally",
        size='tb_incidence_100k', # Size points by incidence rate
        size_max=40,
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={
            "population": "Population",
            "tb_incident_cases_total": "Total Incident Cases",
            "tb_incidence_100k": "Incidence per 100k"
        }
    )
    scatter_pop_incidence.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(scatter_pop_incidence, use_container_width=True)

elif selected_page == "Country Comparison":
    st.title("📊 Country Comparison")
    st.subheader("Key Metrics (Normalized)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Population", f"{round(df['population'].sum()/len(df['year'].unique())):,.0f}")
    with col2:
        st.metric("Total TB Incidence", f"{round(df['tb_incident_cases_total'].sum()/len(df['year'].unique())):,.0f}")
    with col3:
        # Calculate actual deaths for the country
        country_deaths = (df['tb_mortality_100k'] * df['population'] / 100000).sum() / len(df['year'].unique())
        st.metric("Total TB Deaths", f"{round(country_deaths):,.0f}")
    st.divider()

    with st.expander("What is the purpose of this page?"):
        st.write("""
        The Country Comparison page lets you select multiple countries and a specific year to compare TB statistics side by side. Features include:
        - **Key Metrics:** Normalized annual totals for the selected countries.
        - **Incidence and Mortality Charts:** Bar charts for direct comparison.
        - **Trends and Heatmaps:** Visualize how TB prevalence changes over time and across countries.
        - **Case and Death Comparison:** Stacked bar chart for total incident cases and deaths.
        Use this page to benchmark countries, spot leaders and laggards, and analyze year-specific TB data.
        """)

    st.subheader("Filter Options")
    selected_year = st.selectbox("Select Year", sorted(df['year'].unique(), reverse=True))
    selected_country = st.multiselect("Select Country", df['country'].unique(), default=["India", "Pakistan", "China"])

    filtered_df = df[(df['year'] == selected_year) & (df['country'].isin(selected_country))]
    if st.button("Show Filtered Data"):
        st.write(filtered_df)

    with st.expander("What do these metrics mean?"):
        st.write("""
        - **TB Incidence per Country:** Estimated new TB cases per 100,000 population for each selected country in the chosen year.
        - **TB Mortality per Country:** Estimated TB deaths per 100,000 population for each selected country in the chosen year.
        - **Trends/Heatmap:** Show how TB prevalence evolves over time and across countries.
        - **Total Cases and Deaths:** Total estimated incident cases and deaths for the selected countries in the chosen year.
        """)

    st.subheader("TB Incidence per Country")
    fig1 = px.bar(
        filtered_df,
        x='country',
        y='tb_incidence_100k',
        color='tb_incidence_100k',
        title="Estimated TB Incidence per 100,000",
        color_continuous_scale="Reds",
        labels={"tb_incidence_100k": "Incidence per 100k", "country": "Country"}
    )
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    st.subheader("TB Mortality per Country")
    fig2 = px.bar(
        filtered_df,
        x='country',
        y='tb_mortality_100k',
        color='tb_mortality_100k',
        title="Estimated TB Mortality per 100,000",
        color_continuous_scale="Reds",
        labels={"tb_mortality_100k": "Mortality per 100k", "country": "Country"}
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # Add a stacked bar chart for total cases and deaths
    st.subheader(f"Total Incident Cases and Deaths ({selected_year})")
    if not filtered_df.empty:
        # Calculate total cases and deaths for the selected year and countries
        compare_case_death_df = filtered_df.copy()
        compare_case_death_df['actual_deaths'] = compare_case_death_df['tb_mortality_100k'] * compare_case_death_df['population'] / 100000

        stacked_case_death = px.bar(
            compare_case_death_df,
            x='country',
            y=['tb_incident_cases_total', 'actual_deaths'],
            title=f"Total TB Incident Cases and Deaths in {selected_year}",
            labels={'value': 'Count', 'variable': 'Metric'},
            barmode='stack',
            color_discrete_sequence=['#636EFA', '#EF553B'] # Use distinct colors
        )
        st.plotly_chart(stacked_case_death, use_container_width=True)
    else:
        st.warning("No data available for the selected year and countries to compare total cases and deaths.")

    st.subheader("TB Incidence Trend for Selected Countries")
    if not filtered_df.empty:
        line_fig = px.line(
            df[df['country'].isin(selected_country)],
            x='year',
            y='tb_incidence_100k',
            color='country',
            title="TB Prevalence Trend for Selected Countries",
            labels={"tb_incidence_100k": "Incidence per 100k", "year": "Year"},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        line_fig.update_layout(
            xaxis=dict(
                tickmode='linear',
                tick0=1990,
                dtick=5
            )
        )
        st.plotly_chart(line_fig, use_container_width=True)
    st.divider()

    st.subheader("TB Incidence Heatmap")
    heatmap_data = df[df['country'].isin(selected_country)].pivot_table(
        index='country', 
        columns='year', 
        values='tb_incidence_100k'
    )
    heatmap_fig = px.imshow(
        heatmap_data,
        labels=dict(x="Year", y="Country", color="Incidence per 100k"),
        title="TB Incidence Heatmap (Country vs Year)",
        color_continuous_scale="Reds",
        aspect="auto"
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

elif selected_page == "Trends Over Time":
    st.title("📈 Trends Over Time")
    # Use a single selectbox for the entire page
    trend_country = st.selectbox(
        "Select Country",
        df['country'].unique(),
        index=df['country'].tolist().index('Afghanistan'),
        key="trends_country_selection"
    )
    trend_df = df[df['country'] == trend_country]
    st.subheader(f"Key Metrics for {trend_country}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Population",
            f"{round(trend_df['population'].sum()/len(trend_df['year'].unique())):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    with col2:
        st.metric(
            "Total TB Incidence",
            f"{round(trend_df['tb_incident_cases_total'].sum()/len(trend_df['year'].unique())):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    with col3:
        # Calculate actual deaths for the country
        country_deaths = (trend_df['tb_mortality_100k'] * trend_df['population'] / 100000).sum() / len(trend_df['year'].unique())
        st.metric(
            "Total TB Deaths",
            f"{round(country_deaths):,.0f}",
            help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
        )
    st.divider()

    with st.expander("What is the purpose of this page?"):
        st.write("""
        The Trends Over Time page allows you to analyze how TB incidence and mortality rates, detection rates, and HIV co-infection percentages have changed for any country over the dataset period. Features include:
        - **Key Metrics:** Normalized annual totals for the selected country.
        - **Incidence & Mortality Trends:** Line, bar, and dual-axis charts for time series analysis.
        - **Distribution & Correlation:** Histogram and scatter plots to explore rate distributions and relationships.
        Use this page to understand long-term progress, setbacks, and patterns in TB control for any country.
        """)

    tab1, tab2 = st.tabs(["Incidence Trends", "Mortality Trends"])

    with tab1:
        st.subheader("Incidence Trends")
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
        
        st.subheader("Yearly Incidence Distribution")
        bar_fig = px.bar(
            trend_df,
            x='year',
            y='tb_incidence_100k',
            title=f"Yearly TB Incidence in {trend_country}",
            color_discrete_sequence=["#636EFA"]
        )
        st.plotly_chart(bar_fig)

        # Add an Area Chart for Total Incident Cases over Time
        st.subheader("Total Incident Cases Over Time")
        area_fig_incidence = px.area(
            trend_df,
            x='year',
            y='tb_incident_cases_total',
            title=f"Total TB Incident Cases Over Time in {trend_country}",
            color_discrete_sequence=["#00CC96"],
            labels={'tb_incident_cases_total': 'Total Cases'}
        )
        st.plotly_chart(area_fig_incidence)

    with tab2:
        st.subheader("Mortality Trends")
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

        st.subheader("Mortality vs. Incidence (Scatter Plot)")
        scatter_fig = px.scatter(
            trend_df,
            x='tb_incidence_100k',
            y='tb_mortality_100k',
            title=f"Mortality vs. Incidence in {trend_country}",
            labels={"x": "Incidence per 100k", "y": "Mortality per 100k"},
            color_discrete_sequence=["#EF553B"]
        )
        st.plotly_chart(scatter_fig)

        st.subheader("Detection Rate Trend")
        fig_detection = px.line(
            trend_df,
            x='year',
            y='detection_rate',
            title=f"TB Detection Rate Trend in {trend_country}",
            color_discrete_sequence=["#00CC96"]
        )
        st.plotly_chart(fig_detection)

        st.subheader("HIV in TB Trend")
        fig_hiv = px.line(
            trend_df,
            x='year',
            y='hiv_in_tb_percent',
            title=f"HIV Percentage in TB Patients Trend in {trend_country}",
            color_discrete_sequence=["#FFA15A"]
        )
        st.plotly_chart(fig_hiv)

    st.subheader("Incidence vs. Mortality Over Time (Dual Axis Plot)")
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
    st.subheader(f"Key Metrics for {selected_region} (Normalized)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Population", f"{round(df['population'].sum()/len(df['year'].unique())):,.0f}")
    with col2:
        st.metric("Total TB Incidence", f"{round(df['tb_incident_cases_total'].sum()/len(df['year'].unique())):,.0f}")
    with col3:
        # Calculate actual deaths for the region
        region_deaths = (regional_df['tb_mortality_100k'] * regional_df['population'] / 100000).sum() / len(df['year'].unique())
        st.metric("Total TB Deaths", f"{round(region_deaths):,.0f}")
    st.divider()

    with st.expander("What is the purpose of this page?"):
        st.write("""
        The Regional Analysis page focuses on TB statistics within a selected region. Features include:
        - **Key Metrics:** Normalized annual totals for the region.
        - **Country Breakdown:** Bar, pie, and box plots for prevalence, mortality, and deaths by country.
        - **Distribution Analysis:** Explore the spread and variation of TB metrics within the region.
        Use this page to compare countries within a region and identify regional trends or disparities.
        """)

    st.subheader(f"TB Prevalence in {selected_region}")
    region_fig = px.bar(
        regional_df,
        x='country',
        y='tb_incidence_100k',
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
        color_discrete_sequence=px.colors.sequential.OrRd # Keep OrRd for mortality for distinction
    )
    st.plotly_chart(region_mortality_fig)

    st.subheader(f"TB Deaths by Country in {selected_region} (Pie Chart)")
    # Calculate actual deaths for each country
    regional_df['actual_deaths'] = regional_df['tb_mortality_100k'] * regional_df['population'] / 100000
    pie_deaths = px.pie(
        regional_df,
        names='country',
        values='actual_deaths',
        title=f"TB Deaths Distribution in {selected_region}",
        color_discrete_sequence=px.colors.qualitative.Pastel # Use Pastel qualitative palette
    )
    st.plotly_chart(pie_deaths)
    st.divider()

    st.subheader(f"TB Incidence Distribution in {selected_region} (Box Plot)")
    box_incidence = px.box(
        regional_df,
        y='tb_incidence_100k',
        points="all",
        title=f"TB Incidence per 100k in {selected_region} (Box Plot)",
        color_discrete_sequence=px.colors.qualitative.Plotly # Use Plotly qualitative palette
    )
    st.plotly_chart(box_incidence)

    st.subheader(f"Average TB Incidence Trend in {selected_region}")
    # Calculate average incidence per year for the selected region
    regional_yearly_avg = regional_df.groupby('year')['tb_incidence_100k'].mean().reset_index()
    region_trend_fig = px.line(
        regional_yearly_avg,
        x='year',
        y='tb_incidence_100k',
        title=f"Average TB Incidence Trend in {selected_region}",
        labels={"tb_incidence_100k": "Average Incidence per 100k", "year": "Year"}
    )
    st.plotly_chart(region_trend_fig)

    # Add a scatter plot to explore the relationship between Population and TB Mortality per 100k
    st.subheader(f"Population vs. TB Mortality in {selected_region} (Scatter Plot)")
    scatter_pop_mortality_region = px.scatter(
        regional_df,
        x='population',
        y='tb_mortality_100k',
        color='country',
        hover_name='country',
        title=f"Population vs. TB Mortality per 100k in {selected_region}",
        size='tb_incident_cases_total', # Size points by total incident cases
        size_max=40,
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={
            "population": "Population",
            "tb_mortality_100k": "Mortality per 100k",
            "tb_incident_cases_total": "Total Incident Cases"
        }
    )
    scatter_pop_mortality_region.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(scatter_pop_mortality_region, use_container_width=True)

elif selected_page == "Country Profiles":
    st.title("🌍 Country Profiles")

    # Use a single selectbox for the entire Country Profiles page
    selected_country_profile = st.selectbox(
        "Select a Country",
        df['country'].unique(),
        index=df['country'].tolist().index('Afghanistan'),
        key="country_profile_selection"
    )
    # Filter the main dataframe for the selected country
    country_df = df[df['country'] == selected_country_profile]

    tab1, tab2 = st.tabs(["Detailed Statistics", "Trends"])

    with tab1:
        # Remove duplicate selectbox, using the one from the top of the page
        # selected_country_profile = st.selectbox("Select a Country", df['country'].unique(), index=df['country'].tolist().index('Afghanistan'))
        # country_df = df[df['country'] == selected_country_profile]
        with st.expander("What is the purpose of this page?"):
            st.write(f"""
            The Country Profiles page provides a deep dive into all available TB statistics for **{selected_country_profile}**. Features include:
            - **Key Metrics:** Normalized annual population, TB prevalence, incidence, and deaths for the country.
            - **Detailed Table:** All raw data for the country.
            - **Pie & Bar Charts:** Visualize the proportion and totals of prevalence, incidence, and deaths.
            Use this page to get a comprehensive view of TB in a single country.
            """)

        st.subheader(f"Key Metrics for {selected_country_profile}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Population",
                f"{round(country_df['population'].sum()/len(country_df['year'].unique())):,.0f}",
                help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
            )
        with col2:
            st.metric("Total TB Incidence", f"{round(country_df['tb_incident_cases_total'].sum()/len(country_df['year'].unique())):,.0f}", help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals.")
        with col3:
            # Calculate actual deaths for the country
            country_deaths = (country_df['tb_mortality_100k'] * country_df['population'] / 100000).sum() / len(country_df['year'].unique())
            st.metric("Total TB Deaths", f"{round(country_deaths):,.0f}", help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals.")
        st.divider()

        st.subheader(f"Detailed Statistics for {selected_country_profile}")
        st.write(country_df)
        st.subheader("Proportion of TB Metrics (Normalized)")
        pie_data = {
            "Metric": ["Incidence", "Deaths"],
            "Value": [
                country_df['tb_incident_cases_total'].sum() / len(country_df['year'].unique()),
                (country_df['tb_mortality_100k'] * country_df['population'] / 100000).sum() / len(country_df['year'].unique())
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

        st.subheader("Total TB Metrics (Bar Chart)")
        bar_totals = px.bar(
            x=["Incidence", "Deaths"],
            y=[
                country_df['tb_incident_cases_total'].sum() / len(country_df['year'].unique()),
                (country_df['tb_mortality_100k'] * country_df['population'] / 100000).sum() / len(country_df['year'].unique())
            ],
            labels={"x": "Metric", "y": "Total"},
            title=f"Total TB Metrics for {selected_country_profile}"
        )
        st.plotly_chart(bar_totals)

        # Add a bar chart for average key metrics across all years
        st.subheader(f"Average Key Metrics for {selected_country_profile} (All Years)")
        average_metrics = country_df[['tb_incidence_100k', 'tb_mortality_100k', 'hiv_in_tb_percent', 'detection_rate']].mean().reset_index()
        average_metrics.columns = ['Metric', 'Average Value']

        average_metrics_bar = px.bar(
            average_metrics,
            x='Metric',
            y='Average Value',
            title=f"Average TB Metrics for {selected_country_profile} (1990-2023)",
            labels={'Average Value': 'Average Value'},
            color='Metric',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(average_metrics_bar, use_container_width=True)

    with tab2:
        # Remove duplicate selectbox, using the one from the top of the page
        # selected_country_profile = st.selectbox("Select a Country for Trends", df['country'].unique(), index=df['country'].tolist().index('Afghanistan'), key="country_trends")
        # country_df = df[df['country'] == selected_country_profile]
        with st.expander("What is the purpose of this page?"):
            st.write(f"""
            The Trends tab in Country Profiles shows how TB metrics have changed over time for **{selected_country_profile}**. Features include:
            - **Key Metrics:** Normalized annual totals and averages for the country.
            - **Trends & Yearly Charts:** Line, bar, and scatter plots for time series and correlation analysis.
            - **Additional Trends:** Plots for detection rate and HIV in TB percentage over time.
            Use this tab to analyze progress, setbacks, and patterns in TB control for the selected country.
            """)

        st.subheader(f"Key Metrics for {selected_country_profile}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Population",
                f"{round(country_df['population'].sum()/len(country_df['year'].unique())):,.0f}",
                help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals."
            )
        with col2:
            st.metric("Total TB Incidence", f"{round(country_df['tb_incident_cases_total'].sum()/len(country_df['year'].unique())):,.0f}", help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals.")
        with col3:
            # Calculate actual deaths for the country
            country_deaths = (country_df['tb_mortality_100k'] * country_df['population'] / 100000).sum() / len(country_df['year'].unique())
            st.metric("Total TB Deaths", f"{round(country_deaths):,.0f}", help="Normalized to a single year (data spans multiple years) to avoid unrealistic totals.")
        st.divider()

        st.subheader(f"Trends for {selected_country_profile}")
        fig_trends = px.line(
            country_df,
            x='year',
            y=['tb_incidence_100k', 'tb_mortality_100k', 'tb_incident_cases_total'],
            title=f"Trends in TB Statistics for {selected_country_profile}",
            labels={"value": "Rate per 100k", "variable": "Metric"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_trends)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Prevalence Rate", f"{country_df['tb_incidence_100k'].mean():.2f} per 100k")
        with col2:
            st.metric("Average Mortality Rate", f"{country_df['tb_mortality_100k'].mean():.2f} per 100k")
        with col3:
            st.metric("Average Incidence Rate", f"{country_df['tb_incident_cases_total'].mean():.2f} per 100k")

        st.subheader("Yearly Trends")
        bar_trends = px.bar(
            country_df,
            x='year',
            y=['tb_incidence_100k', 'tb_mortality_100k', 'tb_incident_cases_total'],
            title=f"Yearly Trends in TB Metrics for {selected_country_profile}",
            labels={"value": "Rate per 100k", "variable": "Metric"},
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(bar_trends)

        st.subheader("Prevalence vs. Incidence Over Years (Scatter Plot)")
        scatter_profile = px.scatter(
            country_df,
            x='tb_incidence_100k',
            y='tb_incident_cases_total',
            color='year',
            title=f"Prevalence vs. Incidence Over Years in {selected_country_profile}",
            labels={"x": "Prevalence per 100k", "y": "Incidence per 100k"}
        )
        st.plotly_chart(scatter_profile)

        st.subheader("Detection Rate Trend")
        fig_detection_profile = px.line(
            country_df,
            x='year',
            y='detection_rate',
            title=f"TB Detection Rate Trend in {selected_country_profile}",
            color_discrete_sequence=["#00CC96"]
        )
        st.plotly_chart(fig_detection_profile)

        st.subheader("HIV in TB Trend")
        fig_hiv_profile = px.line(
            country_df,
            x='year',
            y='hiv_in_tb_percent',
            title=f"HIV Percentage in TB Patients Trend in {selected_country_profile}",
            color_discrete_sequence=["#FFA15A"]
        )
        st.plotly_chart(fig_hiv_profile)

        # Add a scatter plot showing HIV in TB Percentage vs. Detection Rate over years
        st.subheader("HIV in TB vs. Detection Rate Over Years")
        scatter_hiv_detection = px.scatter(
            country_df,
            x='detection_rate',
            y='hiv_in_tb_percent',
            color='year',
            title=f"HIV in TB Percentage vs. Detection Rate Over Years in {selected_country_profile}",
            labels={
                "detection_rate": "Detection Rate (%)",
                "hiv_in_tb_percent": "HIV in TB (%)"
            },
            hover_name='year'
        )
        st.plotly_chart(scatter_hiv_detection, use_container_width=True)

elif selected_page == "Interactive Data Explorer":
    st.title("🔍 Interactive Data Explorer")
    with st.expander("What is the purpose of this page?"):
        st.write("""
        The Interactive Data Explorer lets you filter, query, and visualize the TB dataset however you like. Features include:
        - **Key Metrics:** Totals for your filtered selection.
        - **Custom Query:** Enter your own conditions to filter the data.
        - **Flexible Visualizations:** Violin, line, bar, and scatter plots update based on your filters and queries.
        Use this page for custom analysis, hypothesis testing, or to answer specific questions about the data.
        """)

    # Add more filtering options
    col1, col2 = st.columns(2)
    with col1:
        selected_region = st.multiselect("Select Region", df['region'].unique(), default=df['region'].unique())
    with col2:
        selected_countries_explorer = st.multiselect("Select Countries", df['country'].unique(), default=[])

    selected_years = st.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

    # Apply initial filters
    explorer_df = df[(df['region'].isin(selected_region)) & (df['year'].between(*selected_years))]

    # Apply country filter if any countries are selected
    if selected_countries_explorer:
        explorer_df = explorer_df[explorer_df['country'].isin(selected_countries_explorer)]

    with st.expander("What do these metrics mean?"):
        st.write("""
        - **Region:** The WHO region to which the country belongs.
        - **Year Range:** The years included in your current filter.
        - **Custom Query Results:** Data that matches your custom filter or query.
        - **All metrics are normalized to a single year where noted.**
        """)

    st.subheader("Custom Query Results")
    query = st.text_area("Enter a custom query (e.g., `tb_incidence_100k > 100`). Available columns: " + ", ".join(explorer_df.columns))
    if query:
        try:
            if any(keyword in query.lower() for keyword in ["import", "exec", "eval", "os.", "sys."]):
                raise ValueError("Invalid query: Potentially unsafe operations detected.")

            query_results = explorer_df.query(query)
            st.write(query_results)

            if not query_results.empty:
                st.markdown("### TB Prevalence by Region")
                region_fig = px.bar(
                    query_results.groupby('region').sum().reset_index(),
                    x='region',
                    y='tb_incident_cases_total',
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
                # Calculate actual deaths for each region
                query_results['actual_deaths'] = query_results['tb_mortality_100k'] * query_results['population'] / 100000
                stacked_data = query_results.groupby('region')[['tb_incident_cases_total', 'actual_deaths']].sum().reset_index()
                stacked_fig = px.bar(
                    stacked_data,
                    x='region',
                    y=['tb_incident_cases_total', 'actual_deaths'],
                    title="Stacked Bar Chart for Regional TB Statistics",
                    labels={"value": "Count", "variable": "Metric"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(stacked_fig)
            else:
                st.warning("No data matches the query. Please adjust your query and try again.")
        except Exception as e:
            st.error(f"Error in query: {e}. Please ensure your query is valid and uses column names correctly.")

    # Allow users to create custom plots
    st.subheader("Create Custom Plot")
    if not explorer_df.empty:
        plot_type = st.selectbox("Select Plot Type", ["scatter", "line", "bar", "histogram", "box", "violin"])
        all_columns = explorer_df.columns.tolist()

        if plot_type in ["scatter", "line", "bar"]:
            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("Select X-axis", all_columns)
            with col_y:
                y_axis = st.selectbox("Select Y-axis", all_columns)

            if plot_type == "scatter":
                custom_fig = px.scatter(explorer_df, x=x_axis, y=y_axis, hover_name='country', title=f"{y_axis} vs. {x_axis}")
            elif plot_type == "line":
                custom_fig = px.line(explorer_df, x=x_axis, y=y_axis, color='country', title=f"{y_axis} over {x_axis}")
            elif plot_type == "bar":
                 custom_fig = px.bar(explorer_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            st.plotly_chart(custom_fig, use_container_width=True)

        elif plot_type in ["histogram", "box", "violin"]:
            selected_column = st.selectbox("Select Column", all_columns)
            if plot_type == "histogram":
                custom_fig = px.histogram(explorer_df, x=selected_column, title=f"Distribution of {selected_column}")
            elif plot_type == "box":
                custom_fig = px.box(explorer_df, y=selected_column, title=f"Distribution of {selected_column} (Box Plot)")
            elif plot_type == "violin":
                 custom_fig = px.violin(explorer_df, y=selected_column, box=True, points="all", title=f"Distribution of {selected_column} (Violin Plot)")
            st.plotly_chart(custom_fig, use_container_width=True)
    else:
        st.warning("No data available for plotting. Please adjust your filters or query.")

    st.subheader("Filtered Data Table")
    if st.button("Show Filtered Data"):
        st.write(explorer_df)

    # Bring back the deleted plots
    st.subheader("TB Prevalence by Region (Violin Plot)")
    violin_fig = px.violin(
        explorer_df,
        x='region',
        y='tb_incidence_100k',
        box=True,
        points="all",
        title="TB Prevalence by Region (Violin Plot)"
    )
    st.plotly_chart(violin_fig)
    st.divider()

    st.subheader("Average TB Prevalence Over Years (Filtered)")
    if not explorer_df.empty:
        avg_year = explorer_df.groupby('year')['tb_incidence_100k'].mean().reset_index()
        avg_line = px.line(
            avg_year,
            x='year',
            y='tb_incidence_100k',
            title="Average TB Prevalence Over Years (Filtered)"
        )
        st.plotly_chart(avg_line)

elif selected_page == "Country Similarity Analysis":
    st.title("🌎 Country Similarity Analysis")
    st.markdown("""
    This page allows you to explore the similarity between countries based on their TB profiles. 
    Using key TB metrics from the most recent year, we calculate cosine similarity to identify countries with similar patterns in incidence, mortality, detection, and HIV co-infection rates.
    """)

    # Country Similarity Analysis
    st.subheader("Country Similarity Analysis")
    # The markdown explanation for similarity is updated above in the main page markdown.

    # Select relevant numerical features for similarity calculation
    similarity_cols = [
        'tb_incidence_100k',
        'tb_mortality_100k',
        'hiv_in_tb_percent',
        'detection_rate',
    ]

    # Prepare data for similarity - use data from the most recent year
    latest_year = df['year'].max()
    country_features = df[df['year'] == latest_year][['country'] + similarity_cols].set_index('country')

    # Drop countries with any NaN values in the selected features
    country_features = country_features.dropna()

    if not country_features.empty:
        # Calculate cosine similarity matrix
        cosine_sim_matrix = cosine_similarity(country_features)

        # Convert to a pandas DataFrame for easier handling
        cosine_sim_df = pd.DataFrame(
            cosine_sim_matrix,
            index=country_features.index,
            columns=country_features.index
        )

        st.write(f"Select a country to find others with similar TB profiles based on metrics from the most recent year ({latest_year}).")

        # Dropdown to select a country
        selected_country_similarity = st.selectbox(
            "Select a Country",
            cosine_sim_df.index.unique(),
            key="similarity_country_selection"
        )

        if selected_country_similarity:
            # Get similarity scores for the selected country
            similarity_scores = cosine_sim_df[selected_country_similarity]

            # Sort countries by similarity score (excluding the selected country itself)
            sorted_similar_countries = similarity_scores.sort_values(ascending=False).drop(selected_country_similarity)

            st.subheader(f"Countries Most Similar to {selected_country_similarity}")

            # Display the top N similar countries
            num_similar_countries = st.slider("Number of similar countries to show", 5, 20, 10)
            
            # Get data for the selected country and the top similar countries for the latest year
            compare_countries = [selected_country_similarity] + sorted_similar_countries.head(num_similar_countries).index.tolist()
            compare_df = df[(df['year'] == latest_year) & (df['country'].isin(compare_countries))]

            if not compare_df.empty:
                # Display similar countries in a formatted way (Bar chart for scores)
                similar_countries_df = sorted_similar_countries.head(num_similar_countries).reset_index()
                similar_countries_df.columns = ['Country', 'Cosine Similarity Score']
                # st.dataframe(similar_countries_df) # Remove the table display

                # Add a bar chart for similarity scores
                st.subheader("Cosine Similarity Scores")
                similarity_bar_chart = px.bar(
                    similar_countries_df,
                    x='Country',
                    y='Cosine Similarity Score',
                    title=f"Cosine Similarity Scores for Countries Most Similar to {selected_country_similarity}",
                    labels={'Cosine Similarity Score': 'Score'}
                )
                st.plotly_chart(similarity_bar_chart, use_container_width=True)

                # Melt the DataFrame to long format for easy plotting (Define compare_melted here)
                compare_melted = compare_df.melt(id_vars=['country', 'year'], value_vars=similarity_cols, var_name='Metric', value_name='Value')

                # Add visual comparison: Bar chart comparing metrics of selected country and similar countries
                st.subheader("Metric Comparison with Similar Countries")

                # Create a grouped bar chart
                comparison_bar = px.bar(
                    compare_melted, 
                    x='Metric',
                    y='Value',
                    color='country',
                    barmode='group',
                    title=f"Comparison of TB Metrics for {selected_country_similarity} and Similar Countries ({latest_year})",
                    labels={'Value': 'Metric Value'}
                )
                st.plotly_chart(comparison_bar, use_container_width=True)

                # Add a Radar Chart for comparison
                st.subheader("Radar Chart Comparison")

                # Radar chart requires a specific data structure
                # We already have compare_melted which is in long format, suitable for radar chart
                radar_chart = px.line_polar(
                    compare_melted, 
                    r='Value', 
                    theta='Metric', 
                    color='country',
                    line_close=True,
                    title=f"Radar Chart of TB Metrics for {selected_country_similarity} and Similar Countries ({latest_year})",
                    # Add line tension for smoother lines
                    line_shape='linear' # line_shape IS valid for line_polar
                )
                # Customize radar chart layout
                radar_chart.update_traces(fill='toself')
                st.plotly_chart(radar_chart, use_container_width=True)

                # Add a Scatter Matrix for selected country and similar countries
                st.subheader("Metric Scatter Matrix Comparison")

                # Add multiselect for choosing metrics for scatter matrix
                selected_scatter_metrics = st.multiselect(
                    "Select Metrics for Scatter Matrix",
                    similarity_cols, # Use the same metrics defined for similarity calculation
                    default=similarity_cols # Default to showing all similarity metrics
                )

                if selected_scatter_metrics:
                    scatter_matrix_fig = px.scatter_matrix(
                        compare_df, # Use compare_df which contains data for selected and similar countries
                        dimensions=selected_scatter_metrics, # Use only the selected metrics
                        color='country', # Color by country
                        title=f"Scatter Matrix of Selected TB Metrics for {selected_country_similarity} and Similar Countries ({latest_year})"
                    )
                    # Remove invalid layout property
                    # scatter_matrix_fig.update_layout(
                    #     diagonal_visible=False # Hide diagonal histograms for clarity
                    # )
                    st.plotly_chart(scatter_matrix_fig, use_container_width=True)
                else:
                    st.info("Please select at least one metric for the scatter matrix.")

            else:
                st.warning("Not enough data to compare metrics for the selected country and similar countries for the selected year.") # Refined warning message

    else:
        st.warning("Not enough data to perform similarity analysis after handling missing values.")

elif selected_page == "Interactive Maps":
    st.title("🗺️ Interactive Maps")
    st.markdown("""
    Explore the global distribution of various TB metrics using interactive maps. Select a metric and a year to visualize the data across countries.
    """)

    # Placeholder for map visualization
    st.subheader("Global Map Visualization")

    # Select metric and year for the map
    metric_to_map = st.selectbox(
        "Select Metric to Map",
        ['tb_incidence_100k', 'tb_mortality_100k', 'hiv_in_tb_percent', 'detection_rate'],
        format_func=lambda x: x.replace('tb_', 'TB ').replace('_', ' ').title()
    )

    # Use the full dataframe for animation
    map_df = df.copy()

    if not map_df.empty:
        # Create the choropleth map with animation_frame
        map_fig = px.choropleth(
            map_df,
            locations="iso3",
            color=metric_to_map,
            hover_name="country",
            animation_frame="year", # Animate based on the year column
            projection="equirectangular",
            title=f"Global {metric_to_map.replace('tb_', 'TB ').replace('_', ' ').title()} Over Time", # General title for animation
            color_continuous_scale="Viridis", # Use Viridis for sequential data
            labels={metric_to_map: metric_to_map.replace('tb_', 'TB ').replace('_', ' ').title()}
        )
        map_fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=700, # Further increase map height
            width=1200 # Further increase map width
        )
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.warning("Not enough data to display map for the selected options.")

elif selected_page == "Documentation":
    st.title("📚 Documentation")
    st.markdown("""
    # Global Tuberculosis (TB) Burden Dashboard

    This Streamlit dashboard provides interactive analytics and visualizations for the global burden of Tuberculosis (TB) using data from the World Health Organization (WHO) from 1990 to 2023.

    ## Features
    - **Global Overview:** Explore global TB distribution with interactive maps, regional and country comparisons, incidence/mortality relationships, and population vs. incidence trends. Key metrics like Total Population, Total TB Incidence, and Total TB Deaths are normalized to a single year for realistic representation.
    - **Country Comparison:** Compare key TB metrics (Incidence per 100k, Mortality per 100k), trends over time (line chart), and a heatmap for selected countries and a specific year or range. Includes a stacked bar chart for total incident cases and deaths.
    - **Trends Over Time:** Analyze incidence and mortality trends over the years for a selected country with line and bar charts, dual-axis plots for incidence vs. mortality, a histogram for incidence rate distribution, total incident cases area chart, detection rate trend, and HIV in TB trend.
    - **Regional Analysis:** Visualize regional TB metrics (Incidence per 100k, Mortality per 100k, Deaths) using bar, pie, and box plots. Explore the relationship between population and mortality and view the average incidence trend over time for a selected region. Also includes a scatter plot for Incidence vs. Detection Rate.
    - **Country Profiles:** Get a detailed look at a single country. The **Detailed Statistics** tab provides key normalized metrics, the full data table for the country across all years, proportion of metrics (Incidence, Deaths), a total metrics bar chart, and average key metrics across all years bar chart. The **Trends** tab shows yearly trends for incidence, mortality, total cases, detection rate, and a scatter plot for HIV in TB vs. detection rate over years.
    - **Interactive Data Explorer:** A flexible tool to filter the dataset by region, country, and year range. Enter custom queries to filter data further. Create custom plots (scatter, line, bar, histogram, box, violin) by selecting plot type and axes. Also includes pre-defined violin plot for regional prevalence and line chart for average prevalence over years.
    - **Country Similarity Analysis:** Discover countries with similar TB profiles based on key metrics (Incidence per 100k, Mortality per 100k, HIV in TB %, Detection Rate) from the most recent year using cosine similarity. Includes a bar chart of similarity scores, a bar chart comparing metrics with similar countries, and a radar chart for profile comparison.
    - **Interactive Maps:** Visualize the global distribution of various TB metrics (Incidence per 100k, Mortality per 100k, HIV in TB %, Detection Rate) over time with an animated choropleth map for the years 1990-2023.

    ## Data Source
    - World Health Organization (WHO)
    - Data file: `data/combined_tb_data_1990_2023.csv`

    ## How to Use
    1. Use the sidebar navigation to access different analysis pages.
    2. Utilize the interactive widgets (selectboxes, sliders, multiselects, text area) on each page to filter data and customize visualizations.
    3. Hover over plot elements for tooltips with specific data points.
    4. Use the zoom and pan controls on the plots to explore details.

    ## Normalization Note
    - Some key metrics (Total Population, Total TB Incidence, Total TB Deaths) are normalized to a single year by dividing the sum across all years by the total number of years in the dataset (33 years).

    ## Customization
    - To use updated or different data, replace the `data/combined_tb_data_1990_2023.csv` file with your new dataset. Ensure it has similar columns or update the `load_data` function and plot configurations accordingly.
    - To add new visualizations or analysis, modify the `app.py` file. Refer to the existing code for examples using Streamlit and Plotly Express.

    ## Contact
    For questions or feedback, please contact [shahmeershahzad67@gmail.com](mailto:shahmeershahzad67@gmail.com).
    """)


