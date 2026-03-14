import ccxt
import pandas as pd
import time

from rich.console import Console
from src.config import TICKER, TIME_FRAME, DATA_PATH

def fetch_historical_data(limit=10000):
    exchange = ccxt.binance()
    
    with Console().status(f"[bold white] Connecting to Binance for download {limit} candles for {TICKER}..."):
        ohlcv = exchange.fetch_ohlcv(TICKER, timeframe=TIME_FRAME, limit=limit)
        
    Console().print(f"[bold green]\[ + ] Succesfully connected to Binance")
    
    with Console().status("[bold white] Processing data and saving to CSV..."):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna() 
        df['tic'] = TICKER
        df = df[["date", "open", "high", "low", "close", "volume", "tic"]]
        
        df.to_csv(DATA_PATH, index=False)

    Console().print(f"[bold green]\[ + ] Data saved in  {DATA_PATH}")
    return df

if __name__ == "__main__":
    fetch_historical_data()
