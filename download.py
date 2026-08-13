import time
import pandas as pd
import yfinance as yf

USE_SP500 = True

TICKERS = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "NVDA",
    "TSLA",
    "AMZN",
    "META",
    "AMD",
    "AVGO",
    "NFLX"
]

SP500_URL - https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv

def safe_last(series):
    """Return the latest valid numeric value from a pandas Series."""
    if series is None or len(series) == 0:
        return None
value = series.iloc[-1]
return None if pd.isna(value) else float(value)
def -norandey fiance utundex columns and return standard OHLEV columns...
if df is None or df. empty:
return of if isinstance(df.columns, pd.MultiIndex):
df.columns - df.columns.get_level_values(®)
return d
def safe_download(ticker, period-"ly", interval-"1d", retries-3, SLeep_seconds-):
***Download market data with retry, empty-data protection and Close validation."** for attempt in range(retries):
try:
printf"(ticker): attempt (attempt + 1)")
df = yf.download(
tickers period-period, interval-interval, auto_adjust-True, progress-False,
af -_normalise_yfinance_columns(df)
if df is None or df. empty:
print(f"(ticker): empty download")
continue
if "Close" not in df. columns:
print(f"(ticker): Missing Close")
continue
if df["Close"].isna().all():
print(f"(ticker): ALL Close NaN")
continue
return df
except Exception as error:
print(f"(ticker) download error: (error))
time.sleep(sleep_seconds)