import pandas
import numpy
import os
import sys

from stable_baselines3 import PPO
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from src.config import TECHNICAL_INDICATORS, TRAINED_MODEL_DIR, TRANSACTION_FEE_PERCENT

MODEL_PATH = os.path.join(TRAINED_MODEL_DIR, "markov_btc_model")
_MODEL_CACHE = None

def get_signal_manual(df, is_deterministic):
    global _MODEL_CACHE
    
    sys.stdout = open(os.devnull, "w")

    try:
        df_recent = df.tail(200).copy()
        
        df_recent.reset_index(drop=True, inplace=True)

        fe = FeatureEngineer(
            use_technical_indicator=True,
            tech_indicator_list=TECHNICAL_INDICATORS,
            use_vix=False,
            use_turbulence=False
        )
        processed_df = fe.preprocess_data(df_recent)
        
        last_row = processed_df.iloc[-1]
        current_price = float(last_row['close'])

        state = [
            1.0,
            1.0,
            0.0
        ]
        
        for tech in TECHNICAL_INDICATORS:
            val = float(last_row[tech])
            
            if "boll" in tech or "atr" in tech:
                state.append(val / current_price)

            else:
                state.append(val / 100.0)

        obs_array = numpy.array([state], dtype=numpy.float32)

        if _MODEL_CACHE is None:
            _MODEL_CACHE = PPO.load(MODEL_PATH)

        action, _ = _MODEL_CACHE.predict(obs_array, deterministic=is_deterministic)

        sys.stdout = sys.__stdout__

        final_action = action[0]
        
        if isinstance(final_action, (numpy.ndarray, list)):
            final_action = final_action[0]

        return float(final_action)

    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"\n[!] Error en normalización/predicción: {e}")
        return 0.0

def get_signal_gym(df, is_deterministic):
    global _MODEL_CACHE

    sys.stdout = open(os.devnull, "w")

    df_recent = df.tail(30).copy() #
    df_recent.reset_index(drop=True, inplace=True) #

    fe = FeatureEngineer(
        use_technical_indicator=True,
        tech_indicator_list=TECHNICAL_INDICATORS,
        use_vix=False,
        use_turbulence=False
    )

    processed_df = fe.preprocess_data(df_recent)

    env_kwargs = {
        "stock_dim": 1,
        "hmax": 100,
        "initial_amount": 10000,
        "num_stock_shares": [0],
        "buy_cost_pct": [TRANSACTION_FEE_PERCENT],
        "sell_cost_pct": [TRANSACTION_FEE_PERCENT],
        "reward_scaling": 1e-2,
        "state_space": len(TECHNICAL_INDICATORS) + 3,
        "action_space": 1,
        "tech_indicator_list": TECHNICAL_INDICATORS,
        "print_verbosity": 0
    }

    e_predict_gym = StockTradingEnv(df=processed_df, **env_kwargs)
    env_sb, _ = e_predict_gym.get_sb_env()

    sys.stdout = sys.__stdout__

    try:
        trained_model = PPO.load(MODEL_PATH, env=env_sb)

    except Exception as e:
        print(f"Damn bro, this is a fucking error: {e}")
        return 0

    obs = env_sb.reset()

    action, _states = trained_model.predict(obs, deterministic=is_deterministic)

    final_action = action[0]
    if isinstance(final_action, (list, numpy.ndarray)):
        final_action = final_action[0]

    return float(final_action)
