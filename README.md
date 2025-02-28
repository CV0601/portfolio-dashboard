# 📊: Einder Investments Portfolio Dashboard

A simple Streamlit app showing the portfolio performance of Einder Investments using IBKR API.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://einderinvestments-portfolio.streamlit.app/?utm_medium=oembed)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```
2. Install IB API manually:
   - Open a virtual environment
   - move to directory $ cd /portfolio-dashboard/code/pythonclient/
   - Run the setup.py provided by IBKR

   ```
   $ python setup.py install
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
