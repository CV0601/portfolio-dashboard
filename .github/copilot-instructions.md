# AI Coding Agent Instructions for Einder Investments Portfolio Dashboard

## Project Overview
A Streamlit-based portfolio dashboard that fetches real-time trading data from Interactive Brokers (IBKR) API and displays portfolio performance metrics. The application integrates with MySQL for historical data storage and Gmail for automated notifications.

## Architecture & Data Flow

### Core Components
- **`streamlit_app.py`**: Interactive frontend displaying portfolio metrics with Plotly visualizations. Uses CSV files (`code/data/`) containing pre-exported portfolio snapshots from TWS/IB Gateway.
- **`main.py`**: IBKR API integration layer implementing the `TradingApp` class (EWrapper + EClient). Manages real-time portfolio data collection via account summaries, PnL queries, and position tracking.
- **`ibapi/`**: Official Interactive Brokers Python API client library (3rd-party, included locally). Use `EClient` for requests, override `EWrapper` methods to handle callbacks.
- **`setup_database.py`**: MySQL connection utility using environment variables for credentials.
- **`send_email.py`**: Gmail SMTP integration for automated portfolio alerts using email templates.

### Data Flow Pipeline
1. **IB API Connection** → `TradingApp` (in `main.py`) establishes connection to TWS/IB Gateway on `127.0.0.1:7496`
2. **Request Callbacks** → `reqAccountSummary()`, `reqPnL()`, `reqPositions()` trigger asynchronous responses
3. **DataFrame Accumulation** → Wrapper methods (`accountSummary()`, `pnl()`, `position()`) append data to internal dictionaries
4. **Daily Update** → `daily_update()` function sends portfolio email via `send_email()`
5. **UI Rendering** → CSV files manually exported from TWS feed `streamlit_app.py` visualizations

## Critical Developer Workflows

### Running the Streamlit App
```bash
pip install -r requirements.txt
streamlit run code/streamlit_app.py
```
The app expects CSV files in `code/data/` (manually exported from TWS). Update `DATA_FILENAME` path in streamlit_app.py to switch datasets.

### IB API Integration
1. **Prerequisites**: TWS/IB Gateway must be running and logged in on `localhost:7496`
2. **Connection Test**: The `TradingApp` constructor validates connection—raises `ConnectionError` if TWS isn't running
3. **Threading**: API runs on separate thread via `Thread(target=self.run)`. Always call `disconnect_api()` to cleanly shutdown
4. **Request/Response Pattern**: Requests are async; use `time.sleep()` after requests to allow callback accumulation before reading dataframes

### Database & Email Setup
- **Environment Variables** (.env file): `host_db`, `user_db`, `password_db`, `database_db`, `GMAIL_ADDRESS`, `GMAIL_PASSWORD`, `RECEIVING_MAIL_ADDRESS`
- Current `.env` path hardcoded in files (needs refactoring): `C:\Users\caspe\Documents\python projects\tws trading\.env`
- Email extraction logic in `send_email()` parses dataframe columns by tag name: `df_summary.loc[df_summary['Tag'] == 'NetLiquidationByCurrency', 'Value']`

## Project-Specific Conventions & Patterns

### CSV Parsing (Critical)
The CSV files from TWS are malformed with variable column counts per row. Three-stage parsing in `streamlit_app.py`:
1. **Safe CSV Loading**: `safe_read_csv()` tries standard pandas.read_csv; falls back to `load_padded_csv()` if ParserError
2. **Padded DataFrame**: `load_padded_csv()` normalizes columns by padding rows with empty strings
3. **Section Extraction**: Data organized by sections identified in column 0; "Header" row marks actual column names (skip columns 0-1 which contain metadata)
4. **Clean Output**: Strip duplicate columns, drop metadata columns, remove NaN columns

### IBKR API Wrapper Pattern
The `TradingApp` class follows the official IB API pattern:
- Inherit from both `EWrapper` (callbacks) and `EClient` (requests)
- Store data in `self.dataframes` dictionary with keys: `"acc_summary"`, `"pnl_summary"`, `"pos_summary"`
- Use `_append_to_dataframe()` helper to accumulate responses
- Always use matching reqId between request and callback (e.g., `reqAccountSummary(1, ...)` paired with responses having `reqId: 1`)

### Data Visualization
All charts use Plotly (`plotly.express` and `plotly.graph_objects`). Streamlit caching via `@st.cache_data` decorator prevents redundant CSV parsing.

## Integration Points & Dependencies

### External Services
- **Interactive Brokers TWS/IB Gateway**: Requires manual login; API available on `127.0.0.1:7496` (configurable in `main.py` constructor)
- **MySQL Database**: Connection details in environment variables; used by `setup_database.py` (currently appears unused in main flow)
- **Gmail SMTP**: `smtp.gmail.com:587` with app-specific password (not regular Gmail password)

### Key Dependencies (from requirements.txt)
- `streamlit`: Dashboard UI
- `pandas`: Data manipulation and DataFrame management
- `plotly`: Interactive visualizations
- `mysql-connector-python`: Database connections
- `python-dotenv`: Environment variable loading
- `numpy`: Numerical operations (imported in streamlit_app.py but may be unused)

## Important Notes & Gotchas

1. **Hardcoded File Paths**: Dotenv loading uses absolute Windows paths (e.g., `C:\Users\caspe\...`). Needs environment-specific configuration for cross-machine deployment.
2. **Threading & Timing**: IB API callbacks are async. Insufficient `time.sleep()` between requests and dataframe reads causes empty/incomplete data collection.
3. **CSV Format Inconsistency**: TWS export format is unstable—padding logic is defensive but may need updating if TWS changes output structure.
4. **Manual Data Export Workflow**: Streamlit app currently depends on manually exporting CSVs from TWS, not live streaming from IB API (example in `example/stream_data.py` uses `ib_insync` library, not the included `ibapi`).
5. **Email Body Parsing**: `send_email()` raises `ValueError` if dataframes are empty; this blocks main flow if API collection fails silently.

## Code Organization Rules

- Place IB API request/callback logic in `main.py` (extend `TradingApp` class)
- Place UI/visualization code in `streamlit_app.py`
- Keep CSV loading logic in `streamlit_app.py` (already optimized for Streamlit caching)
- New database operations go in `setup_database.py` and import from there
- Email template changes go in `send_email.py` (currently plain text, could be HTML)
