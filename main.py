import time
import pandas
import shutil
import os
import sys

from src.utils import banner, log_trade

from rich.console import Console
from colorama import init, Fore, Back, Style
from src.data_fetcher import fetch_historical_data

init(autoreset=True)

width = shutil.get_terminal_size().columns
line = "-" * width

process = ["[ x ]", "[ + ]", "[ ! ]", "[ * ]"]

def run_bot():
    print(line)
    Console().print("[bold green]SELECT STRATEGY[/bold green]".center(width + 20))
    print(line)

    print("""
    1. Deterministic (The Cold Analysis)
It acts as a purely mathematical analyst that only signal if indicators
        align with high-confidence patterns. Being predictable and stable, 
        it avoids impulsive trades from markerts noise, but risks being too slow
        for fast scalping moves.

    2. No Deterministic (The Risk Taker)
        It introduces a probability factor allowing the AI to "take risks"
        and explore signals based on the model's statistical intuition.
        It is much more reactive and sensitive to small price changes,
        catching early momentum at the cost of more false signals or erratic entries.\n""")
        
    while True:
        choice = input("\nSelect strategy number: ")

        if choice == "1":
            from src.agent_logic import get_signal_manual
            is_deterministic = True
            is_manual = True
            
            print("Mode Deterministic selected")
            print(line)
            
            break

        elif choice == "2":
            is_deterministic = False
            
            print("Mode No Deterministic selected\n")
            print("""
    m -> Sensitive Manual Mode (Sniper)
            That operates as a high-precison "Sniper (by this his name)",
            specifically optimized to filter market noise and priorizate 
            signals with force equal or greater than 0.85. This reduce 
            drastically the number of trades, consumes minimal RAM by 
            using a direct model cache. This mode in latest tests, can make a 
            winrate of approximately 66%.

    g -> Stable Gym Mode (Machine Gun)
            That react to every micro-fluctuation, which, while faithful to
            the training environment, results in "fee bleeding" that can
            wipe out your profits in just a few hours of sideways markets movements.\n""")
            
            while True:
                choice = input("Do you want manual mode or gym mode? (m/g)")

                if choice == "m":
                    from src.agent_logic import get_signal_manual
                    is_manual = True
                    
                    print("Mode manual selected\n")
                    print(line)

                    break

                elif choice == 'g':
                    from src.agent_logic import get_signal_gym
                    is_manual = False

                    print("Mode gym selected\n")
                    print(line)
                    
                    break

                else:
                    print("Select a valid option")

            break

        else:
            print("Select a valid strategy")

    while True:
        try:
            hour = time.strftime("%H:%M:%S", time.localtime())
            
            with Console().status("Analysing market..."):
                if is_manual == True:
                    df = fetch_historical_data(limit=500, show_status=False)
                    force = get_signal_manual(df, is_deterministic)

                elif is_manual == False:
                    df = fetch_historical_data(limit=500, show_status=False)
                    force = get_signal_gym(df, is_deterministic)

                current_price = df.iloc[-1]["close"]
            
            if df is not None:
                if force >= 0.9:
                    Console().print(f"SIGNAL: BUY (FORCE {force:.4f}) PRICE: {current_price}| TIME: {hour}\n ")
                    action = "BUY"

                elif force <= -0.9:
                    Console().print(f"SIGNAL: SELL (FORCE: {force:.4f}) PRICE: {current_price} | TIME: {hour}\n")
                    action = "SELL"

                else:
                    Console().print(f"SIGNAL: HODL (FORCE: {force:.4f}) PRICE: {current_price} | TIME: {hour}\n")
                    action = "HODL"

            log_trade(hour, current_price, action, force)
            time.sleep(300)

        except Exception as e:
            print(f"Damn, a fucking error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    banner()
    run_bot()
    
