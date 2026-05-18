# This script has been created by crisdimxs
# You can use this script for financial pourposes btw
# Sorry for my bad english :(

#Note: I will recommend you use firstly test,
#if the strategy works, you can change to False.
#On the other hand, your API should be correct,
#remeber that demo trading API is diferent to real trading API.
API_KEY = "Here_your_API_key"
SECRET = "Here_your_SECRET_key"
IS_TEST = True

TICKER = "BTCUSDT" #Here your symbol/token/TICKER
LEVERAGE = 5 # Here your leverage (2, 5, 10, 30) the leverage depends of the crypto

TIME_FRAME = "5m" #This is the time frame, 5 minutes here because this is scalping bruh, but the strategy with 30m or 15m works better than 5m.

###################
# DONT CHANGE PLS #
###################
#The next lines will be use with FinRL for trading with AI

#Indicators for Chains of Markov
#FinRL will use this parameters formake the arrayof probabilities
#TECHNICAL_INDICATORS = [
#    "macd", 
#    "rsi_30",
#    "cci_30",
#    "dx_30",
#    "adx",
#    "boll_ub",
#    "boll_lb",
#    "kdjk",
#    "wr_30",
#    "atr"
#]

#DETERMINISTIC = False
#MANUAL = True


#INITIAL_ACCOUNT_BALANCE = 10000
#TRANSACTION_FEE_PERCENT = 0.00075

#Data files
DATA_PATH = "data/btc_historical.csv"
#TRAINED_MODEL_DIR = "models/"
