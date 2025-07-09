import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt

logo_url = 'https://einderinvestments.nl/wp-content/uploads/2024/09/Verticaal-Wit.png'
date_today = dt.date.today()
formatted_date_today = date_today.strftime('%d-%m-%Y')
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Einder Investments Portfolio Dashboard',
    page_icon= logo_url, # This is an emoji shortcode. Could be a URL too.
    layout="wide"
)
# Load and parse the CSV into a dictionary of DataFrames
@st.cache_data
def load_data():
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/data_test_24052025.csv'
    raw_df = pd.read_csv(DATA_FILENAME, header = None)
    section_col = raw_df.columns[0]
    section_names = raw_df[section_col].dropna().unique()

    df_dict = {}
    for section in section_names:
        section_df = raw_df[raw_df[section_col] == section].copy().reset_index(drop=True)

        # Try to find header row
        header_row = section_df[section_df[1] == 'Header']
        if not header_row.empty:
            header_idx = header_row.index[0]
            headers = section_df.iloc[header_idx].values[2:]
            data = section_df.iloc[header_idx + 1:].copy()
            data.columns = ['Meta', 'Type'] + list(headers)
            data = data.loc[:, ~data.columns.duplicated()].copy()
            data = data.drop(columns=['Meta', 'Type'], errors='ignore')
            data = data.loc[:, data.columns.notna()]
            df_dict[section] = data.reset_index(drop=True)
        else:
            df_dict[section] = section_df

    return df_dict

# Load data
df_dict = load_data()

# Streamlit layout
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

# Layout
top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)

# Top Left: Holdings
with top_left:
    st.subheader("💼 Current Holdings")
    holdings_df = df_dict.get("Open Position Summary", pd.DataFrame()).copy()
    if not holdings_df.empty:
        holdings_df = holdings_df.dropna(axis=1, how='all')
        st.dataframe(holdings_df)
    else:
        st.warning("No holdings data available.")

# Top Right: Performance Chart
with top_right:
    st.subheader("📈 Portfolio Performance")
    show_portfolio = st.checkbox("Show Portfolio", value=True)
    show_benchmark = st.checkbox("Show MSCI ACWI", value=True)

    perf_df = df_dict.get("Time Period Benchmark Comparison", pd.DataFrame()).copy()
    if not perf_df.empty:
        perf_df = perf_df.dropna(axis=1, how='all')
        if 'Date' in perf_df.columns:
            perf_df['Date'] = pd.to_datetime(perf_df['Date'], errors='coerce')
            perf_df = perf_df.dropna(subset=['Date'])

            if show_portfolio and 'U14552292Return' in perf_df.columns:
                perf_df['U14552292Return'] = pd.to_numeric(perf_df['U14552292Return'], errors='coerce')
                perf_df['Portfolio'] = (1 + perf_df['U14552292Return'] / 100).cumprod()

            if show_benchmark and 'BM1Return' in perf_df.columns:
                perf_df['BM1Return'] = pd.to_numeric(perf_df['BM1Return'], errors='coerce')
                perf_df['MSCI ACWI'] = (1 + perf_df['BM1Return'] / 100).cumprod()

            chart_data = perf_df.set_index('Date')[[col for col in ['Portfolio', 'MSCI ACWI'] if col in perf_df.columns]]
            if not chart_data.empty:
                st.line_chart(chart_data)
            else:
                st.info("Please select at least one line to display.")
        else:
            st.warning("Date column not found in performance data.")
    else:
        st.warning("No performance data available.")


# Bottom Left: Summary Stats
with bottom_left:
    st.subheader("📊 Summary Statistics")
    key_stats_df = df_dict.get("Key Statistics", pd.DataFrame()).copy()
    risk_df = df_dict.get("Risk Measures Benchmark Comparison", pd.DataFrame()).copy()
    if not key_stats_df.empty:
        key_stats_df = key_stats_df.dropna(axis=1, how='all')
        st.markdown("**Key Statistics**")
        st.dataframe(key_stats_df)
    else:
        st.warning("No key statistics available.")
    if not risk_df.empty:
        risk_df = risk_df.dropna(axis=1, how='all')
        st.markdown("**Risk Measures**")
        st.dataframe(risk_df)
    else:
        st.warning("No risk measures available.")

# Bottom Right: Placeholder
with bottom_right:
    st.subheader("🧩 Coming Soon")
    st.write("This space is reserved for future features.")


