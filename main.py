#!/bin/env
import time
import threading

from src.utils import *
from src.config import TICKER
    
from rich.console import Console 
from rich.live import Live

current_price = 0

def update_price(trading):
    global current_price

    while True:
        try:
            current_price = trading.fetch_ccxt()

        except:
            pass

        time.sleep(0.2)

if __name__ == "__main__":
    try:
        banner()
    
        trading = TradingService()
        ui = UI()

        threading.Thread(target=update_price, args=(trading,), daemon=True).start()
        
        with Live(ui.ui(), refresh_per_second=1) as live:
            ui.ticker = TICKER

            while True:
                ui.current_price = current_price

                if trading.has_position():
                    ui.entry_price = entry_price
                    ui.stop_price = stop_price
                    ui.tp_price = take_price
                    if current_price:
                        ui.pnl = trading.calculate_pnl(ui.current_price)
                    
                    ui.wallet = trading.review_balance()
                    
                else:
                    signal = FetchAI().get_signal()
                    ui.action = signal
                    
                    if signal == "HODL":
                        time.sleep(300)
                    
                    else:
                        trading.close_position()
                        entry_price = trading.make_position(signal)
                        stop_price = trading.stop_loss()
                        take_price = trading.take_profit() 

                live.update(ui.ui())
    
    except KeyboardInterrupt:
        print("Script cancelado")
        trading.close_position()
