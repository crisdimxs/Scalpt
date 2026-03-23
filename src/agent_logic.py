import pandas
import numpy 
import os
import sys

from stable_baselines3 import PPO
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from src.config import TECHNICAL_INDICATORS, TRAINED_MODEL_DIR, TRANSACTION_FEE_PERCENT

def get_signal(df):
    sys.stdout = open(os.devnull, "w")

    fe = FeatureEngineer(
        use_technical_indicator=True,
        tech_indicator_list=TECHNICAL_INDICATORS,
        use_vix=False,
        use_turbulence=False
    )

    processed_df = fe.preprocess_data(df)

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
    
    model_path = os.path.join(TRAINED_MODEL_DIR, "markov_btc_model")
    
    sys.stdout = sys.__stdout__

    try:
        trained_model = PPO.load(model_path, env=env_sb)
    
    except Exception as e:
        print(f"Damn bro, this is a fucking error: {e}")
        return 0

    obs = env_sb.reset()

    action, _states = trained_model.predict(obs, deterministic=False)
    
    final_action = action[0]
    if isinstance(final_action, (list, numpy.ndarray)):
        final_action = final_action[0]

    return float(final_action)
