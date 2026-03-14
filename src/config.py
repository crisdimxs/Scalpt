# This script has been created by crisdimxs
# This script use the library FinRL by FinancialAI
# You can use this script for financial pourposes btw



TICKER = "BTC/USD" #Here your symbol/token/TICKER
TIME_FRAME = "5m" #This the time frame, 5 minutes here because this is scalping bruh

#Indicators for Chains of Markov
#FinRL will use this parameters formake the arrayof probabilities
TECHNICAL_INDICATORS = [
    "macd", 
    "rsi_30",
    "cci_30",
    "dx_30",
    "adx",
    "boll_ub",
    "boll_lb",
    "kdjk",
    "wr_30",
    "atr"
]

#Config for trading enviroment
INITIAL_ACCOUNT_BALANCE = 10000
#Fees of Binance
TRANSACTION_FEE_PERCENT = 0.00075

#Data files
DATA_PATH = "data/btc_historical.csv"
TRAINED_MODEL_DIR = "models/"
