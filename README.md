# TB Burden Dashboard

A Streamlit web application for exploring, visualizing, and analyzing the global burden of Tuberculosis (TB) using data from the World Health Organization (WHO).

## Features
- **Global Overview:** Interactive map, pie, bar, box, and scatter plots showing TB prevalence and mortality by country and region.
- **Country Comparison:** Compare TB metrics across selected countries and years with bar, line, and heatmap visualizations.
- **Trends Over Time:** Analyze incidence and mortality trends for any country, including dual-axis, histogram, and scatter plots.
- **Regional Analysis:** Visualize TB metrics by region with bar, pie, and box plots.
- **Country Profiles:** Detailed statistics and trends for individual countries, including pie, bar, and scatter plots.
- **Interactive Data Explorer:** Filter, query, and visualize the dataset with violin, line, and bar plots.

## Data Source
- World Health Organization (WHO)
- Data file: `data/TB_Burden_Country.csv`

## How to Run
1. **Install dependencies:**
   ```zsh
   pip install -r requirements.txt
   ```
2. **Navigate to the project folder:**
   ```zsh
   cd TB_burden
   ```
3. **Run the Streamlit app:**
   ```zsh
   streamlit run app.py
   ```

## Folder Structure
```
TB_burden/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── TB_Burden_Country.csv
```

## Customization
- You can add or update the data in `data/TB_Burden_Country.csv`.
- Modify `app.py` to add new visualizations or analytics as needed.

## Contact
For questions or feedback, please contact [shahmeershahzad67@gmail.com](mailto:shahmeershahzad67@gmail.com).
