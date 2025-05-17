import pandas as pd

def merge_tb_data(csv1_path, csv2_path, output_path):
    # Load datasets with correct column types
    df_new = pd.read_csv(csv1_path, dtype={'year': int})  # 2000-2023 data
    df_old = pd.read_csv(csv2_path, dtype={'Year': int})   # 1990-2013 data

    # Standardize column names for both datasets
    column_mapping_new = {
        'country': 'country',
        'iso2': 'iso2',
        'iso3': 'iso3',
        'iso_numeric': 'iso_numeric',
        'g_whoregion': 'region',
        'year': 'year',
        'e_pop_num': 'population',
        'e_inc_100k': 'incidence_rate',
        'e_inc_100k_lo': 'incidence_rate_lo',
        'e_inc_100k_hi': 'incidence_rate_hi',
        'e_inc_num': 'incidence_num',
        'e_inc_num_lo': 'incidence_num_lo',
        'e_inc_num_hi': 'incidence_num_hi',
        'e_tbhiv_prct': 'hiv_in_tb_percent',
        'e_tbhiv_prct_lo': 'hiv_in_tb_percent_lo',
        'e_tbhiv_prct_hi': 'hiv_in_tb_percent_hi',
        'e_mort_exc_tbhiv_100k': 'mort_rate_no_hiv',
        'e_mort_exc_tbhiv_100k_lo': 'mort_rate_no_hiv_lo',
        'e_mort_exc_tbhiv_100k_hi': 'mort_rate_no_hiv_hi',
        'c_cdr': 'detection_rate',
        'c_cdr_lo': 'detection_rate_lo',
        'c_cdr_hi': 'detection_rate_hi'
    }

    column_mapping_old = {
        'Country or territory name': 'country',
        'ISO 2-character country/territory code': 'iso2',
        'ISO 3-character country/territory code': 'iso3',
        'ISO numeric country/territory code': 'iso_numeric',
        'Region': 'region',
        'Year': 'year',
        'Estimated total population number': 'population',
        'Estimated incidence (all forms) per 100 000 population': 'incidence_rate',
        'Estimated incidence (all forms) per 100 000 population, low bound': 'incidence_rate_lo',
        'Estimated incidence (all forms) per 100 000 population, high bound': 'incidence_rate_hi',
        'Estimated number of incident cases (all forms)': 'incidence_num',
        'Estimated number of incident cases (all forms), low bound': 'incidence_num_lo',
        'Estimated number of incident cases (all forms), high bound': 'incidence_num_hi',
        'Estimated HIV in incident TB (percent)': 'hiv_in_tb_percent',
        'Estimated HIV in incident TB (percent), low bound': 'hiv_in_tb_percent_lo',
        'Estimated HIV in incident TB (percent), high bound': 'hiv_in_tb_percent_hi',
        'Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population': 'mort_rate_no_hiv',
        'Estimated mortality of TB cases (all forms, excluding HIV), per 100 000 population, low bound': 'mort_rate_no_hiv_lo',
        'Estimated mortality of TB cases (all forms, excluding HIV), per 100 000 population, high bound': 'mort_rate_no_hiv_hi',
        'Case detection rate (all forms), percent': 'detection_rate',
        'Case detection rate (all forms), percent, low bound': 'detection_rate_lo',
        'Case detection rate (all forms), percent, high bound': 'detection_rate_hi'
    }

    # Apply column renaming
    df_new = df_new.rename(columns={k: v for k, v in column_mapping_new.items() if k in df_new.columns})
    df_old = df_old.rename(columns={k: v for k, v in column_mapping_old.items() if k in df_old.columns})

    # Define final column set
    final_columns = [
        'country', 'iso2', 'iso3', 'iso_numeric', 'region', 'year', 'population',
        'incidence_rate', 'incidence_rate_lo', 'incidence_rate_hi',
        'incidence_num', 'incidence_num_lo', 'incidence_num_hi',
        'hiv_in_tb_percent', 'hiv_in_tb_percent_lo', 'hiv_in_tb_percent_hi',
        'mort_rate_no_hiv', 'mort_rate_no_hiv_lo', 'mort_rate_no_hiv_hi',
        'detection_rate', 'detection_rate_lo', 'detection_rate_hi'
    ]

    # Add missing columns to both datasets
    for df in [df_new, df_old]:
        for col in final_columns:
            if col not in df.columns:
                df[col] = pd.NA

    # Merge datasets using outer join on iso3 + year
    merged = pd.merge(
        df_old[final_columns],
        df_new[final_columns],
        on=['iso3', 'year'],
        how='outer',
        suffixes=('_old', '_new')
    )

    # Combine columns preferring newer data where available
    for col in final_columns:
        if col in ['iso3', 'year']: continue  # Already used for merging
        merged[col] = merged[f'{col}_new'].combine_first(merged[f'{col}_old'])

    # Clean up and sort
    merged = merged[final_columns]
    merged = merged.sort_values(['iso3', 'year'])
    
    # Handle remaining NA values
    merged = merged.fillna('')
    
    # Save to CSV
    merged.to_csv(output_path, index=False)
    print(f"Merged data saved to {output_path}")
    return merged

# Usage
merge_tb_data(
    csv1_path='data/TB_Burden_Country.csv',      # Newer data (2000-2023)
    csv2_path='data/TB_burden_countries_2025-05-18.csv',  # Older data (1990-2013)
    output_path='data/combined_tb_data_1990_2023.csv'
)