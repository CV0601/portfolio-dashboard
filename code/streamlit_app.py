import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

logo_url = 'https://einderinvestments.nl/wp-content/uploads/2024/09/Verticaal-Wit.png'
date_today = dt.date.today()
DATA_FILENAME = Path(__file__).parent/'data/data_10_03_2025.csv'
formatted_date_today = date_today.strftime('%d-%m-%Y')
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Einder Investments Portfolio Dashboard',
    page_icon= logo_url, # This is an emoji shortcode. Could be a URL too.
    layout="wide"
)
# Load and parse the CSV into a dictionary of DataFrames
@st.cache_data
def load_padded_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    max_cols = max(len(line.strip().split(",")) for line in lines)
    padded_lines = [
        line.strip().split(",") + [""] * (max_cols - len(line.strip().split(",")))
        for line in lines
    ]
    return pd.DataFrame(padded_lines)

def safe_read_csv(file_path, **kwargs):
    try:
        return pd.read_csv(file_path, **kwargs)
    except pd.errors.ParserError:
        print("⚠️ ParserError encountered. Falling back to padded CSV loader.")
        return load_padded_csv(file_path)

@st.cache_data
def load_data(DATA_FILENAME):
    raw_df = safe_read_csv(DATA_FILENAME, header=None)

    section_col = raw_df.columns[0]
    section_names = raw_df[section_col].dropna().unique()

    df_dict = {}
    for section in section_names:
        section_df = raw_df[raw_df[section_col] == section].copy().reset_index(drop=True)

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

def load_returns_from_csv(file_path):
    df = safe_read_csv(file_path, header=None)
    section_col = df.columns[0]
    section_name = "Time Period Benchmark Comparison"
    section_df = df[df[section_col] == section_name].copy().reset_index(drop=True)

    header_row = section_df[section_df[1] == 'Header']
    if not header_row.empty:
        header_idx = header_row.index[0]
        headers = section_df.iloc[header_idx].values[2:]
        data = section_df.iloc[header_idx + 1:].copy()
        data.columns = ['Meta', 'Type'] + list(headers)
        data = data.drop(columns=['Meta', 'Type'], errors='ignore')
        data = data.loc[:, data.columns.notna()]
        return data.reset_index(drop=True)
    else:
        return pd.DataFrame()


def simulate_future_nav_paths_with_realized(returns_df, num_scenarios=1500, forecast_days=252):
    returns_df['Date'] = pd.to_datetime(returns_df['Date'], errors='coerce')
    returns_df['U14552292Return'] = pd.to_numeric(returns_df['U14552292Return'], errors='coerce') / 100
    returns_df = returns_df.dropna(subset=['Date', 'U14552292Return'])
    returns_df['Realized_NAV'] = (1 + returns_df['U14552292Return']).cumprod()

    last_date = returns_df['Date'].max()
    three_months_ago = last_date - pd.DateOffset(months=3)
    realized_df = returns_df[returns_df['Date'] >= three_months_ago].copy()

    mu = returns_df['U14552292Return'].mean()
    sigma = returns_df['U14552292Return'].std()
    last_nav = returns_df['Realized_NAV'].iloc[-1]

    dt = 1
    random_returns = np.random.normal(loc=mu * dt, scale=sigma * np.sqrt(dt), size=(forecast_days, num_scenarios))
    nav_paths = np.zeros_like(random_returns)
    nav_paths[0] = last_nav
    for t in range(1, forecast_days):
        nav_paths[t] = nav_paths[t - 1] * (1 + random_returns[t])

    percentiles = {
        '5th': np.percentile(nav_paths, 5, axis=1),
        '25th': np.percentile(nav_paths, 25, axis=1),
        '50th': np.percentile(nav_paths, 50, axis=1),
        '75th': np.percentile(nav_paths, 75, axis=1),
        '95th': np.percentile(nav_paths, 95, axis=1),
    }

    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=realized_df['Date'], y=realized_df['Realized_NAV'],
                             mode='lines', name='Realized NAV', line=dict(color='black', width=2)))
    fig.add_trace(go.Scatter(x=future_dates, y=percentiles['95th'], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_dates, y=percentiles['5th'], fill='tonexty',
                             fillcolor='rgba(0, 123, 255, 0.1)', line=dict(width=0), name='5th-95th Percentile'))
    fig.add_trace(go.Scatter(x=future_dates, y=percentiles['75th'], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_dates, y=percentiles['25th'], fill='tonexty',
                             fillcolor='rgba(0, 123, 255, 0.3)', line=dict(width=0), name='25th-75th Percentile'))
    fig.add_trace(go.Scatter(x=future_dates, y=percentiles['50th'],
                             line=dict(color='blue', width=2), name='Median Forecast'))

    fig.update_layout(
        title='Realized and Simulated Future NAV Paths',
        xaxis=dict(
            title=dict(text='Date', font=dict(color='black')),
            tickfont=dict(color='black'),
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=dict(text='NAV', font=dict(color='black')),
            tickfont=dict(color='black'),
            showgrid=True,
            gridcolor='lightgray'
        ),
        font=dict(color='black'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            font=dict(color='black'),
            bgcolor='white'
        )
    )
    return fig

def calculate_cumulative_nav(df, start_date):
    df = df[df['Date'] >= start_date].copy()
    # set NAV value to 1 for correct comparison
    df['Portfolio'] = (1 + df['U14552292Return'] / 100).cumprod()
    df['MSCI ACWI'] = (1 + df['BM1Return'] / 100).cumprod()
    return df
# calling functions
df_dict = load_data(DATA_FILENAME)
#----------------------------------------------------------------------#
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

        if 'Date' in holdings_df.columns:
            holdings_df = holdings_df[~holdings_df['Date'].astype(str).str.contains("Total", na=False)]

        cols_to_drop = ['FinancialInstrument', 'Currency', 'Sector', 'Quantity', 'ClosePrice', 'FXRateToBase']
        holdings_df = holdings_df.drop(columns=[col for col in cols_to_drop if col in holdings_df.columns], errors='ignore')

        # Calculate NAV
        if 'Value' in holdings_df.columns:
            holdings_df['Value'] = pd.to_numeric(holdings_df['Value'], errors='coerce')
            total_value = holdings_df['Value'].sum()
            holdings_df['NAV_raw'] = holdings_df['Value'] / total_value
            holdings_df['NAV'] = holdings_df['NAV_raw'].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "")
            holdings_df = holdings_df.sort_values(by='NAV_raw', ascending=False)


        # Toggle between table and pie chart
        view_option = st.radio("Select view:", ["Table", "Pie Chart"], horizontal=True)

        if view_option == "Table":
            st.dataframe(holdings_df.drop(columns='NAV_raw'))
        else:
            name_col = 'Description' if 'Description' in holdings_df.columns else 'Symbol'
            if 'Value' in holdings_df.columns and name_col in holdings_df.columns:
                fig = px.pie(
                    holdings_df,
                    names=name_col,
                    values='Value',
                    title='NAV Distribution by Asset'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Required columns for pie chart not found.")
    else:
        st.warning("No holdings data available.")



# Top Right: Performance Chart
with top_right:
    st.subheader("📈 Portfolio Performance")

    # Toggles
    show_portfolio = st.checkbox("Show Portfolio", value=True)
    show_benchmark = st.checkbox("Show MSCI ACWI", value=True)

    # Timeframe selector (app-level so we can recompute and rebase properly)
    timeframe = st.radio(
        "Timeframe",
        options=["3M", "6M", "YTD", "1Y", "All"],
        index=2,  # default to YTD
        horizontal=True
    )

    perf_df = df_dict.get("Time Period Benchmark Comparison", pd.DataFrame()).copy()

    if not perf_df.empty:
        perf_df = perf_df.dropna(axis=1, how='all')

        if 'Date' not in perf_df.columns:
            st.warning("Date column not found in performance data.")
        else:
            # --- Helpers ---
            def get_window_start(last_dt: pd.Timestamp, tf: str) -> pd.Timestamp:
                if tf == "YTD":
                    return pd.Timestamp(year=last_dt.year, month=1, day=1)
                elif tf == "3M":
                    return last_dt - pd.DateOffset(months=3)
                elif tf == "6M":
                    return last_dt - pd.DateOffset(months=6)
                elif tf == "1Y":
                    return last_dt - pd.DateOffset(years=1)
                else:  # "All"
                    return pd.Timestamp.min  # we'll clamp to min available

            # --- Clean base dataframe ---
            perf_df['Date'] = pd.to_datetime(perf_df['Date'], errors='coerce')
            perf_df = perf_df.dropna(subset=['Date']).sort_values('Date')

            # Determine window and slice
            last_date = perf_df['Date'].max()
            start_date = get_window_start(last_date, timeframe)
            window_df = perf_df[perf_df['Date'] >= max(start_date, perf_df['Date'].min())].copy()

            # Build cumulative-from-window series
            series_cols = {}
            if show_portfolio and 'U14552292Return' in window_df.columns:
                window_df['U14552292Return'] = pd.to_numeric(window_df['U14552292Return'], errors='coerce') / 100.0
                series_cols['Portfolio'] = (1 + window_df['U14552292Return']).cumprod() - 1

            if show_benchmark and 'BM1Return' in window_df.columns:
                window_df['BM1Return'] = pd.to_numeric(window_df['BM1Return'], errors='coerce') / 100.0
                series_cols['MSCI ACWI'] = (1 + window_df['BM1Return']).cumprod() - 1

            # Assemble plotting frame
            if series_cols:
                chart_data = pd.DataFrame({'Date': window_df['Date']})
                for name, ser in series_cols.items():
                    chart_data[name] = ser.values
                chart_data = chart_data.set_index('Date').dropna(how='all')

                if chart_data.empty:
                    st.info("No valid data to display for the selected timeframe.")
                else:
                    fig = px.line(
                        chart_data,
                        title=f'Portfolio vs Benchmark — Cumulative Return (since {timeframe} start)',
                    )
                    # Format y-axis as percent and keep a rangeslider for convenience
                    fig.update_layout(
                        yaxis=dict(title='Cumulative Return', tickformat=".0%"),
                        xaxis=dict(
                            title='Date',
                            rangeslider=dict(visible=True),
                            # No rangeselector here—our app-level selector does the rebasing
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        legend=dict(bgcolor='white')
                    )
                    # Grid styling (optional)
                    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
                    fig.update_yaxes(showgrid=True, gridcolor='lightgray')

                    st.plotly_chart(fig, theme='streamlit', use_container_width=True)
            else:
                st.info("Please select at least one line to display.")
    else:
        st.warning("No performance data available.")


# Bottom Left: Summary Stats
with bottom_left:
    st.subheader("📊 Summary Statistics")

    risk_df = df_dict.get("Risk Measures Benchmark Comparison", pd.DataFrame()).copy()

    if not risk_df.empty:
        risk_df = risk_df.dropna(axis=1, how='all')
        # Extract metrics
        def get_metric(label, fmt):
            row = risk_df[risk_df.iloc[:, 0] == label]
            if label == "Beta:":
                value = row.iloc[0, 2]
            else:
                value = row.iloc[0, 4]
            
            try: 
                value = float(value)
                if fmt == "percent":
                    return f"{value:.2%}"
                if fmt == "volatility":
                    return f"{(value-1):.2%}"
                if fmt == "float":
                    return f"{value:.2f}"
            except:
                return "N/A"

        mean_return = get_metric("Mean Return:", "percent")
        volatility = get_metric("Standard Deviation:", "volatility")
        sharpe = get_metric("Sharpe Ratio:", "float")
        beta = get_metric("Beta:", "float")

        # Display in 2x2 layout
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Mean Return", value=mean_return)
        with col2:
            st.metric(label="Volatility", value=volatility)

        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Sharpe Ratio", value=sharpe)
        with col4:
            st.metric(label="Beta", value=beta)
    else:
        st.warning("No risk measures available.")


# Bottom Right: Placeholder
with bottom_right:
    st.subheader("🔮 Experimental: Future NAV Simulation")
    num_scenarios = 1500
    forecast_days = 252
    returns_df = load_returns_from_csv(DATA_FILENAME)
    fig = simulate_future_nav_paths_with_realized(returns_df, num_scenarios, forecast_days)
    st.plotly_chart(fig, use_container_width=True)

