import websocket
import pandas
import numpy
import json
import ccxt
import csv
import os

from src.config import TICKER, LEVERAGE, API_KEY, SECRET, IS_TEST, TIME_FRAME
from src.data_fetcher import fetch_historical_data
"""
if MANUAL:
    from src.agent_logic import get_signal_manual

else:
    print("Sorry, only support no deterministic mode")
    exit()
"""
from rich.console import Console
from rich.table import Table



VERSION = '0.9.0-beta'

exchange = ccxt.binanceusdm({
        "apiKey": API_KEY,
        "secret": SECRET,
        "enableRateLimit": True,
        "timeout": 30000
})

exchange.enableDemoTrading(IS_TEST)

url_websocket = f"wss://stream.binance.com:9443/ws/{TICKER.replace('/', '').lower()}@trade"
#url_websocket =  f"wss://stream.testnet.binance.vision:9443/ws/{TICKER.replace('/', '').lower()}@trade"

def banner():
    Console().print(f"""
         _____________________      #######   ########   #######   #          ######   ########
        |                     |    #         #          #       #  #         #      #     #
        |[bold red]  Buy Bitcoin, HODL[/bold red]  |     ######   #          # ##### #  #         # #####      #
        |[bold red]    and FUCK BANKS [/bold red]  |           #  #          #       #  #         #            #
        |___________________  \\    #######    ########  #       #   #######  #            #
                            \\_\\
                                \   ^__^            [bold cyan]By:[/bold cyan] [bold green]crisdimxs[/bold green]
                                 \  (OO)\_______    [bold cyan]Github:[/bold cyan] [bold blue]https://github.com/crisdimxs/Scalpt[/bold blue]
                                    (__)\       )\/ [bold cyan]X:[/bold cyan] [bold blue]https://x.com/crisdimxs[/bold blue]
                                        ||----w |
                                        ||     ||   [bold cyan]Powered by:[/bold cyan] [bold yellow]FinRL[/bold yellow]
M__MMM___M_MM_MM_MM__M_MMM_MMM___MMM___MMM__MM_MM__ [bold cyan]Version:[/bold cyan] [bold green]{VERSION}[/bold green]                                         
""")


def log_trade(date, price, action):
    file = "data/data.csv"
    exist = os.path.isfile(file)
    columns = ["date", "price", "action"]

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)

        if not exist:
            writer.writeheader()

        writer.writerow({
            'date': date,
            'price': price,
            'action': action,
        })

class TradingService:
    def __init__(self, symbol=TICKER, leverage=LEVERAGE, url=url_websocket):
        self.symbol = symbol
        self.leverage = leverage
        self.url = url

        self.amount = 110 #self.review_balance() * 0.75
        self.total_amount = 0
        self.action = None
        self.entry_price = 0
        self.breakeven = 0

    def make_position(self, action):
        self.action = action
        exchange.set_leverage(self.leverage, self.symbol)
        
        ticker = exchange.fetch_ticker(self.symbol)
        price = ticker["last"]

        self.total_amount = (self.amount * self.leverage) / price
        
        order = exchange.create_order(
            self.symbol,
            "market",
            self.action,
            self.total_amount
        )

        order_id = order["id"]
        self.entry_price = order["average"]

        return self.entry_price

    def stop_loss(self):
        risk_amount = self.amount * 0.025
        price_move = risk_amount / self.total_amount

        if self.action == "buy":
            stop_price = self.entry_price - price_move
            sl_side = "sell"

        else:
            stop_price = self.entry_price + price_move
            sl_side = "buy"

        stop_price = float(exchange.price_to_precision(self.symbol, stop_price))
        amount = float(exchange.amount_to_precision(self.symbol, self.total_amount))

        order = exchange.create_order(
            symbol=self.symbol,
            side=sl_side,
            amount=amount,
            type="STOP_MARKET",
            params={
                'stopLossPrice': stop_price,
                'reduceOnly': True
                }
        )

        return stop_price
    def take_profit(self):
        profit_amount = self.amount * 0.05   # 5% CAPITAL
        price_move = profit_amount / self.total_amount

        if self.action == "buy":
            tp_price = self.entry_price + price_move
            tp_side = "sell"

        else:
            tp_price = self.entry_price - price_move
            tp_side = "buy"

        tp_price = float(exchange.price_to_precision(self.symbol, tp_price))
        amount = float(exchange.amount_to_precision(self.symbol, self.total_amount))

        order = exchange.create_order(
            symbol=self.symbol,
            side=tp_side,
            amount=amount,
            type="TAKE_PROFIT_MARKET",
            params={
                "takeProfitPrice": tp_price,
                "reduceOnly": True
            }
        )

        return tp_price
    
    def trailing_stop(self):
        side = "buy" if self.action == "sell" else "sell"

        if side == "buy":
            self.breakeven = self.entry_price * 0.9992

        else:
            self.breakeven = self.entry_price * 1.0008

        callback_rate = 0.5

        if side == "buy":
            activation_price = self.breakeven / (1 + (callback_rate/100))

        else:
            activation_price = self.breakeven / (1 - (callback_rate/100))

        exchange.create_order(
            symbol=self.symbol,
            type="TRAILING_STOP_MARKET",
            side=side,
            amount=self.total_amount,
            params={
                "callbackRate": callback_rate,
                "activationPrice": activation_price,
                "workingType": "MARK_PRICE",
                "reduceOnly": True
            }
        )

    def has_position(self):
        try:
            exchange.load_markets()

            balance = exchange.fetch_balance()
            positions = balance['info']['positions']

            for pos in positions:
                if pos['symbol'] == self.symbol.replace("/", "") and float(pos['positionAmt']) != 0:
                    return True
                
            return False
            
        except Exception as e:
            print(f"Fuck, un error: {e}")



    def close_position(self):
        try:
            exchange.load_markets()
        
            balance = exchange.fetch_balance()
            positions = balance['info']['positions']
        
            for pos in positions:
                if pos['symbol'] == self.symbol.replace("/", "") and float(pos['positionAmt']) != 0:
                    amt = float(pos['positionAmt'])
                    side = 'SELL' if amt > 0 else 'BUY'
                    
                    exchange.cancel_all_orders(
                        symbol=self.symbol,
                        params={
                            "trigger": True   
                        }
                    )

                    exchange.create_market_order(
                        symbol=self.symbol,
                        side=side.lower(),
                        amount=abs(amt),
                        params={'reduceOnly': True}
                    )

                    #self.exit_price = order["average"]
                    #self.pnl = (self.exit_price - self.entry_price) * amt
                    
                    return True

        except Exception as e:
            print(f"Error: {e}")
    
    def review_balance(self):
        try:
            balance = exchange.fetch_balance()
            
            usdt_balance = balance['USDT']

            return usdt_balance['total']
        
        except Exception as e:
            return 0
    
    def fetch_ws(self):
        current_price = None

        def on_message(ws, msg):
            nonlocal current_price
            
            try:
                current_price = float(json.loads(msg)['p'])

            except:
                current_price = None

            ws.close()

        ws = websocket.WebSocketApp(
                self.url,
                on_message=on_message,
                on_error=lambda ws, err: None
        )

        ws.run_forever()

        return current_price
    
    def fetch_ccxt(self):
        current_price = exchange.fetch_ticker(self.symbol)['last']

        return current_price

    def calculate_pnl(self, current_price):
        fee_percent = 0.0004
        total_fee = self.amount * self.leverage * 2 * fee_percent
        
        if current_price is not None:
            if self.action == "buy":
                pnl_raw = self.amount * self.leverage * (current_price - self.entry_price) / self.entry_price
                

            else:
                pnl_raw = self.amount * self.leverage * (self.entry_price - current_price) / self.entry_price
                
            pnl = pnl_raw - total_fee

            return pnl

        return 0

class FetchAlgo:
    def __init__(self, symbol=TICKER, timeframe=TIME_FRAME, limit=300):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit

        self.last_psar_trend = None

    def fetch_ohlcv(self):
        ohlcv = exchange.fetch_ohlcv(
            self.symbol,
            timeframe=self.timeframe,
            limit=self.limit
        )

        df = pandas.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        return df

    def calculate_ema(self, df, period=200):
        return df["close"].ewm(span=period).mean()

    def calculate_rsi(self, df, period=14):
        delta = df["close"].diff()

        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_psar(self, df, step=0.02, max_step=0.2):
        high = df["high"].values
        low = df["low"].values

        psar = numpy.zeros(len(df))
        bull = True

        af = step
        ep = low[0]
        psar[0] = low[0]

        for i in range(1, len(df)):
            prev_psar = psar[i - 1]

            if bull:
                psar[i] = prev_psar + af * (ep - prev_psar)
                if low[i] < psar[i]:
                    bull = False
                    psar[i] = ep
                    ep = low[i]
                    af = step
                else:
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + step, max_step)
            else:
                psar[i] = prev_psar + af * (ep - prev_psar)
                if high[i] > psar[i]:
                    bull = True
                    psar[i] = ep
                    ep = high[i]
                    af = step
                else:
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + step, max_step)

        return pandas.Series(psar, index=df.index)

    # =========================
    # 🎯 SIGNAL
    # =========================
    def get_signal(self):
        try:
            df = self.fetch_ohlcv()

            # indicadores
            df["ema200"] = self.calculate_ema(df)
            df["rsi"] = self.calculate_rsi(df)
            df["psar"] = self.calculate_psar(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            price = last["close"]
            ema200 = last["ema200"]
            rsi = last["rsi"]
            psar = last["psar"]

            current_trend = "bullish" if psar < price else "bearish"
            prev_trend = "bullish" if prev["psar"] < prev["close"] else "bearish"

            psar_flip = prev_trend == "bearish" and current_trend == "bullish"

            if psar_flip and price > ema200 and rsi > 50:
                return "buy"

            return "HODL"

        except Exception as e:
            print(f"Error en FetchAlgo: {e}")
            return "HODL"

#This class will work with FinRL, i'm still work in that
"""
class FetchAI:
    def __init__(self, deterministic=DETERMINISTIC, manual=MANUAL):
        self.deterministic = deterministic
        self.manual = manual

    def get_signal(self):
        df = fetch_historical_data(limit=500, show_status=False)
        force = get_signal_manual(df, self.deterministic)

        current_price = df.iloc[-1]["close"]

        if df is not None:
            if force >= 0.95:
                return "buy"

            #elif force <= -0.95:
            #   return "sell"

            else:
                return "HODL"
"""
class UI:
    def __init__(self):
        self.ticker = None
        self.current_price = 0
        self.action = None
        self.entry_price = 0
        self.tp_price = 0
        self.stop_price = 0
        self.pnl = 0
        self.wallet = 0

    def ui(self):
        table = Table(title="Scalpt", expand=True, border_style="cyan")

        table.add_column("CRYPTO", justify="center")
        table.add_column("PRICE", justify="center")
        table.add_column("POSITION", justify="center")
        table.add_column("ENTRY PRICE", justify="center")
        table.add_column("TP PRICE", justify="center")
        table.add_column("SL PRICE", justify="center") 
        table.add_column("PNL ($)", justify="center")
        table.add_column("TOTAL WALLET", justify="center")

        color_pnl = "green" if self.pnl >= 0 else "red"

        table.add_row(
            str(self.ticker),
            f"{self.current_price:.2f}",
            f"[bold yellow]{self.action}[/]",
            f"[bold yellow]{self.entry_price:.2f}[/]",
            f"[bold green]{self.tp_price:.2f}",
            f"[bold red]{self.stop_price:.2f}[/]",
            f"[{color_pnl}]{self.pnl:.2f}[/]",
            f"[bold green]{self.wallet:.2f}[/]"
        )

        return table

