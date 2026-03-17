import ccxt
import pandas as pd
import time

from rich.console import Console
from src.config import TICKER, TIME_FRAME, DATA_PATH

process = ["[ x ]", "[ + ]", "[ ! ]", "[ * ]"]

def fetch_historical_data(limit=10000, show_status=True):
    exchange = ccxt.binance()
    
    def download():
        ohlcv = exchange.fetch_ohlcv(TICKER, timeframe=TIME_FRAME, limit=limit)
    
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna()
        df['tic'] = TICKER
        df = df[["date", "open", "high", "low", "close", "volume", "tic"]]

        df.to_csv(DATA_PATH, index=False)    
        
        return df

    if show_status:
        with Console().status(f"[bold white] Connecting to Binance for download {limit} candles for {TICKER}..."):
            df = download()
        
        Console().print(f"[bold green]{process[1]} " + "[bold white]Succesfully connected to Binance")
        Console().print(f"[bold green]{process[1]}" + f"[bold white] Data saved in  {DATA_PATH}")

    else:
        return download()

if __name__ == "__main__":
    fetch_historical_data()
