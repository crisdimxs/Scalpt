import ccxt
import pandas as pd
import time

from src.config import TICKER, TIME_FRAME, DATA_PATH

def fetch_historical_data(limit=2000):
    exchange = ccxt.binance()
    print(f"Conecting to Binance for download {limit} candles for {TICKER}...")
    
    # Download OHLCV (Open, High, Low, Close, Volume)
    ohlcv = exchange.fetch_ohlcv(TICKER, timeframe=TIME_FRAME, limit=limit)
    
    # Make DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert timestamp to format readable for FinRL
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.drop(columns=['timestamp'])
    
    # Add column 'tic' required for FinRL
    df['tic'] = TICKER
    
    # Save data in folder data/
    df.to_csv(DATA_PATH, index=False)
    print(f"Data saved in  {DATA_PATH}")
    return df

if __name__ == "__main__":
    fetch_historical_data()
