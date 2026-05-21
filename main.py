#!/bin/env
import time
import threading

from datetime import datetime, timedelta

from src.utils import *
from src.config import TICKER
    
from rich.console import Console 
from rich.live import Live

current_price = 0

def wait_candle():
    now = datetime.utcnow()

    next_minute = (now.minute // 5 + 1) * 5
    
    if next_minute == 60:
        next_candle = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    else:
        next_candle = now.replace(minute=next_minute, second=0, microsecond=0)

    sleep_time = (next_candle - now).total_seconds()

    time.sleep(sleep_time)

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
        trading.close_position()
        algo = FetchAlgo(timeframe="5m")
        #fetch_ai = FetchAI()
        ui = UI()

        threading.Thread(target=update_price, args=(trading,), daemon=True).start()
        
        with Live(ui.ui(), refresh_per_second=1) as live:
            ui.ticker = TICKER

            while True:
                ui.current_price = current_price

                if trading.has_position():
                    ui.entry_price = entry_price
                    ui.stop_price = stop_price
                    ui.tp_price = tp
                    if current_price:
                        ui.pnl = trading.calculate_pnl(ui.current_price)
                    
                    ui.wallet = trading.review_balance()
                    
                else:
                    trading.close_position()
                    signal, sl_price = algo.get_signal()#fetch_ai.get_signal()
                    ui.action = signal
                    ui.current_price = current_price

                    if signal == "HODL":
                        wait_candle()
                    
                    else:
                        entry_price = trading.make_position(signal)

                        #PoW
                        tp = entry_price + (entry_price - sl_price) * 1.5

                        difference_price = tp - entry_price
                        parts = difference_price / 2

                        activation_price = entry_price + parts
                        callback_rate = (parts / tp) * 100

                        callback_rate = round(callback_rate, 2)
                        stop_price = trading.stop_loss(sl_price)
                        trading.trailing_stop(callback_rate, activation_price)

                live.update(ui.ui())
                
    except KeyboardInterrupt:
        print("Script cancelado")
        trading.close_position()
