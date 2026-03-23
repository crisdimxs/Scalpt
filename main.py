import time
import pandas
import os
import sys

from src.utils import banner
from rich.console import Console
from colorama import init, Fore, Back, Style
from src.data_fetcher import fetch_historical_data
from src.agent_logic import get_signal

init(autoreset=True)

process = ["[ x ]", "[ + ]", "[ ! ]", "[ * ]"]

def run_bot():
    while True:
        try:
            hour = time.strftime("%H:%M:%S", time.localtime())
            
            with Console().status("Analysing market..."):
                df = fetch_historical_data(limit=500, show_status=False)
                action = get_signal(df)

                current_price = df.iloc[-1]["close"]
            
            if df is not None:
                if action >= 0.5:
                    Console().print(f"SIGNAL: BUY (FORCE {action:.4f}) PRICE: {current_price}| TIME: {hour}\n ")
                elif action <= -0.5:
                    Console().print(f"SIGNAL: SELL (FORCE: {action:.4f}) PRICE: {current_price} | TIME: {hour}\n")
                else:
                    Console().print(f"SIGNAL: HODL (FORCE: {action:.4f}) PRICE: {current_price} | TIME: {hour}\n")

            time.sleep(3)

        except Exception as e:
            print(f"Damn, a fucking error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    banner()
    run_bot()
    
