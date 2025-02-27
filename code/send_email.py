import os
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import datetime as dt
import pandas as pd

def send_email(df_summary, df_pnl):
    # load environment variables
    dotenv_path = Path(r'C:\Users\caspe\Documents\python projects\tws trading\.env')
    load_dotenv(dotenv_path=dotenv_path)
    # Retrieve email details and credentials from environment variables
    from_email = os.getenv('GMAIL_ADDRESS')
    to_email = os.getenv('RECEIVING_MAIL_ADDRESS')
    subject = f'Portfolio overview of IBKR Portfolio on {dt.date.today()}'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.getenv('GMAIL_ADDRESS')
    smtp_password = os.getenv('GMAIL_PASSWORD')
    
    # write the body of the text using ingested df
    portfolio_value = round(float(df_summary.loc[df_summary['Tag'] == 'NetLiquidationByCurrency', 'Value']),1)
    daily_pnl = round(float(df_pnl.loc[0, 'DailyPnL']),1)
    unrealized_pnl = round(float(df_pnl.loc[0, 'UnrealizedPnL']),1)
    body = f'Hello Casper,\n\nYour current portfolio value is €{portfolio_value}, with a daily PnL of €{daily_pnl}.\nThe current overall unrealized PnL of the portfolio is €{unrealized_pnl}. \nHopefully you have a good day! \nKind regards,\n\nInteractive Brokers API'

    if from_email is None or smtp_password is None:
        print('Environment variables for email credentials are not set')
        exit(1)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to secure
        server.login(smtp_username, smtp_password)
        
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        return print('Email sent successfully')
    except Exception as e:
        return print(f'Failed to send email: {e}')
    finally:
        server.quit()
