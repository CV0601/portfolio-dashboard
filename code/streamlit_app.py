import streamlit as st
import pandas as pd
import math
import datetime as dt
from pathlib import Path
import mysql.connector
import numpy as np

logo_url = 'https://einderinvestments.nl/wp-content/uploads/2024/09/Verticaal-Wit.png'
date_today = dt.date.today()
formatted_date_today = date_today.strftime('%d-%m-%Y')
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Einder Investments Portfolio Dashboard',
    page_icon= logo_url, # This is an emoji shortcode. Could be a URL too.
    layout="wide"
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/data_test_24052025.csv'
    raw_df = pd.read_csv(DATA_FILENAME, header = None)
    first_col = raw_df.columns[0]
    # Create a dict of DataFrames, one for each unique value
    df_dict = {
        key: raw_df[raw_df[first_col] == key].copy()
        for key in raw_df[first_col].unique()
    }
    # Available keys:
    # ['Introduction', 'Profile', 
    # 'Key Statistics', 'Open Position Summary', 
    # 'Time Period Benchmark Comparison', 
    # 'Risk Measures Benchmark Comparison', 'Disclosure']

    return df_dict

df = get_data()

def clean_for_streamlit(df):
    df = df.copy()
    df.columns = df.columns.map(str)
    df = df.astype(object).where(pd.notnull(df), None)

    for col in df.columns:
        if df[col].dtype == 'float64' or df[col].dtype == 'int64':
            df[col] = df[col].astype(object)
        elif pd.api.types.is_numeric_dtype(df[col]):
             df[col] = df[col].apply(lambda x: float(x) if pd.notnull(x) else None)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)

    return df
# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.markdown(
    """
    <style>
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center; /* Centers content horizontally */
            text-align: center;
            margin-top: 20px; /* Adjust spacing from top */
        }
        .title-container img {
            width: 240px; /* Adjust logo size */
            margin-right: 30px; /* Space between logo and text */
        }
        .title-container h1 {
            margin: 0; /* Remove default margin */
            font-size: 2.5em; /* Adjust title size */
        }
        .content {
            text-align: left; /* Centers the rest of the text */
        }
    </style>
    
    <div class="title-container">
        <img src="https://einderinvestments.nl/wp-content/uploads/2024/09/Horizontaal-Wit.png">
        <h1>Dashboard</h1>
    </div>
    <br>
    <div class="content">
        <p>Browse portfolio data of Einder Investments. Updated regularly to reflect current market conditions, strategy changes, and performance.</p>
        <p>You can find a performance chart, portfolio statistics, and a table with all current holdings.</p>
        <p><strong>For inquiries:</strong> <a href="mailto:info@einderinvestments.nl">info@einderinvestments.nl</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
# creating 4 columns (quadrants)
col1, col2 = st.columns(2)
with col1: 
    st.subheader('Returns', divider = 'blue')
    selected_return = st.multiselect(
    'What returns would you like to view?',
    ['Daily', 'Monthly', 'Quarterly', 'Annual'])
    df['Time Period Benchmark Comparison'].columns = df['Time Period Benchmark Comparison'].iloc[1]
    df['Time Period Benchmark Comparison'] = df['Time Period Benchmark Comparison'][2:]
    df['Time Period Benchmark Comparison']['Date'] = pd.to_datetime(df['Time Period Benchmark Comparison']['Date'], errors = 'coerce')
    st.write('Content here')
# Add some spacing
''
''
with col2:
    st.subheader('Portfolio Returns over time', divider='blue')
    # min_value = df['Year'].min()
    # max_value = df['Year'].max()

    # from_year, to_year = st.slider(
    #     'Which years are you interested in?',
    #     min_value=min_value,
    #     max_value=max_value,
    #     value=[min_value, max_value])

    # countries = df['Country Code'].unique()

    # if not len(countries):
    #     st.warning("Select at least one country")

    # selected_countries = st.multiselect(
    #     'Which countries would you like to view?',
    #     countries,
    #     ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

    # ''
    # ''
    # ''

    # # Filter the data
    # filtered_df = df[
    #     (df['Country Code'].isin(selected_countries))
    #     & (df['Year'] <= to_year)
    #     & (from_year <= df['Year'])
    # ]

 

    # ''

    # st.line_chart(
    #     filtered_df,
    #     x='Year',
    #     y='GDP',
    #     color='Country Code',
    # )

''
''
col3, col4 = st.columns(2)
with col3:
    # first_year = df[df['Year'] == from_year]
    # last_year = df[df['Year'] == to_year]

    # st.subheader(f'Performance in {to_year}', divider='blue')

    ''

    # cols = st.columns(4)

    # for i, country in enumerate(selected_countries):
    #     col = cols[i % len(cols)]

    #     with col:
    #         first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
    #         last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

    #         if math.isnan(first_gdp):
    #             growth = 'n/a'
    #             delta_color = 'off'
    #         else:
    #             growth = f'{last_gdp / first_gdp:,.2f}x'
    #             delta_color = 'normal'

    #         st.metric(
    #             label=f'{country} GDP',
    #             value=f'{last_gdp:,.0f}B',
    #             delta=growth,
    #             delta_color=delta_color
    #         )
with col4:
    # 1. Set headers from row 1
    df_pos = df['Open Position Summary'].copy()
    df_pos.columns = df_pos.iloc[1]

    # 2. Remove header rows and reset index
    df_pos = df_pos.iloc[2:].reset_index(drop=True)

    # 3. Drop rows where Symbol is NaN and assign back
    df_pos = df_pos.dropna(subset=["Symbol"]).reset_index(drop=True)

    # 4. Drop 'Sector' column if exists
    if "Sector" in df_pos.columns:
        df_pos = df_pos.drop(columns=["Sector"])
 
    # 5. Slice columns by name if possible, otherwise by iloc carefully
    cols_wanted = df_pos.columns[5:12]
    df_unclean = df_pos.loc[:, cols_wanted].copy()

    # 6. Replace empty strings and fill NaNs
    df_unclean.replace(r'^\s*$', pd.NA, regex=True, inplace=True)

    # 7. Convert numeric-looking columns to native Python types
    numeric_cols = ['Quantity', 'ClosePrice', 'Value', 'Cost Basis', 'UnrealizedP&L']
    for col in numeric_cols:
        if col in df_unclean.columns:
            df_unclean[col] = pd.to_numeric(df_unclean[col], errors='coerce')

    # 8. Replace <NA> with None for Streamlit compatibility
    df_unclean = df_unclean.where(pd.notnull(df_unclean), None)

    # 9. Clean for Streamlit
    df_display = clean_for_streamlit(df_unclean)

    df_display = df_display.loc[:, df_display.columns.notna()]

    # 10. Display
    st.subheader(f'Holdings as of {formatted_date_today}', divider='blue')
    st.write(df_display)

