import pandas
import os

from src.utils import banner
from rich.console import Console
from stable_baselines3 import PPO
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from src.config import DATA_PATH, TECHNICAL_INDICATORS, TRANSACTION_FEE_PERCENT, TRAINED_MODEL_DIR

process = ["[ x ]", "[ + ]", "[ ! ]", "[ * ]"]

def train_model():
    with Console().status(f"Loading data from {DATA_PATH}..."):
        df = pandas.read_csv(DATA_PATH)

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
            "print_verbosity": 1
        }

        e_train_gym = StockTradingEnv(df=processed_df, **env_kwargs)
        env_train, _ = e_train_gym.get_sb_env()

    with Console().status("Making model PPO with Stable Baselines 3..."):    
        policy_kwargs = dict(
            net_arch=dict(pi=[256, 256, 256], vf=[256, 256, 256]) 
        )

        model = PPO(
            policy="MlpPolicy",
            env=env_train,
            learning_rate=0.00002,
            n_steps=4096,
            batch_size=256,
            ent_coef=0.05,
            policy_kwargs=policy_kwargs,
            verbose=0,
            device="cpu"
        )

    with Console().status("Training model 256x256x256 (This process will take a while, please check back later)"):
        model.learn(total_timesteps=1500000, tb_log_name="ppo_btc_5m_v1")

    Console().print(f"[bold green]{process[1]} " + "[bold white] Model succesfully trained!")
    
    if not os.path.exists(TRAINED_MODEL_DIR):
        os.makedirs(TRAINED_MODEL_DIR)

    model.save(f"{TRAINED_MODEL_DIR}/markov_btc_model")
    
    Console.print(f"[bold cyan]{process[3]}" + f"[bold white] Model saved in {TRAINED_MODEL_DIR}")

if __name__ == "__main__":
    banner()
    train_model()
