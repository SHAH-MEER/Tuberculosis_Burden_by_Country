# TB Burden Dashboard

A Streamlit web application for exploring, visualizing, and analyzing the global burden of Tuberculosis (TB) using data from the World Health Organization (WHO).

## Features
- **Global Overview:** Interactive map visualizing global TB metrics over time, along with regional and country comparisons, incidence/mortality relationships, and population vs. incidence trends.
- **Country Comparison:** Compare key TB metrics, trends, heatmaps, and total cases/deaths for selected countries over a chosen year or range.
- **Trends Over Time:** Analyze incidence and mortality trends, yearly distributions, total cases over time, detection rate trends, and HIV in TB trends for a selected country.
- **Regional Analysis:** Visualize regional TB metrics with bars, pies, and boxes, explore population vs. mortality relationships, and view average incidence trends over time for a selected region.
- **Country Profiles:** Get a detailed look at a single country with key metrics, the full data table, proportion of metrics, total metrics bar chart, and trends including incidence, mortality, total cases, detection rate, and HIV in TB vs. detection rate over years.
- **Interactive Data Explorer:** Filter, query, and create custom plots (scatter, line, bar, histogram, box, violin) on the dataset. Includes regional prevalence violin plot and average prevalence over years line chart.
- **Country Similarity Analysis:** Discover countries with similar TB profiles based on key metrics from the most recent year using cosine similarity. Includes a bar chart of similarity scores, a bar chart comparing metrics with similar countries, and a radar chart for profile comparison.
- **Interactive Maps:** Visualize the global distribution of various TB metrics over time with an animated choropleth map.

## Data Source
- World Health Organization (WHO)
- Data file: `data/combined_tb_data_1990_2023.csv` (Updated data file)

## How to Run
1. **Clone the repository (if applicable):**
   ```zsh
   # If your project is in a Git repository
   # git clone <repository_url>
   # cd <repository_folder>
   ```
2. **Install dependencies:**
   Make sure you have Python installed. Then navigate to the project directory in your terminal and run:
   ```zsh
   pip install -r requirements.txt
   ```
3. **Run the Streamlit app:**
   From the project directory, run:
   ```zsh
   streamlit run app.py
   ```
   The app will open in your web browser.

## Folder Structure
```
TB_burden/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── combined_tb_data_1990_2023.csv
```

## Customization
- You can add or update the data in `data/combined_tb_data_1990_2023.csv`.
- Modify `app.py` to add new visualizations, metrics, or analytics as needed.

## Contact
For questions or feedback, please contact [shahmeershahzad67@gmail.com](mailto:shahmeershadzad67@gmail.com).
