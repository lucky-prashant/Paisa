
import os
import requests
import pandas as pd
from app.config import TWELVE_API_KEY, CACHE_DIR

def fetch_latest_candle(pair):
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=5min&outputsize=1&apikey={TWELVE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "values" not in data:
        raise Exception(f"TwelveData error: {data.get('message', 'No data')}")
    candle = data["values"][0]
    return {
        "datetime": candle["datetime"],
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"]),
        "volume": float(candle["volume"]),
    }

def load_cache(pair):
    symbol = pair.replace("/", "")
    path = os.path.join(CACHE_DIR, f"{symbol}.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def save_cache(pair, df):
    symbol = pair.replace("/", "")
    path = os.path.join(CACHE_DIR, f"{symbol}.csv")
    df.to_csv(path, index=False)

def compute_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df.dropna()

def update_and_prepare(pair):
    latest = fetch_latest_candle(pair)
    df = load_cache(pair)
    if not df.empty and df.iloc[-1]["datetime"] == latest["datetime"]:
        return None
    df = pd.concat([df, pd.DataFrame([latest])], ignore_index=True)
    df = compute_indicators(df)
    save_cache(pair, df)
    return df.iloc[-1:]
