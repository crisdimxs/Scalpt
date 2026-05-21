# Scalpt 🚀

Automatic **crypto scalping bot for Binance Futures** built with Python.  
Scalpt uses technical indicators like **EMA 200**, **RSI**, and **Parabolic SAR** to detect trading opportunities and manage positions automatically using **Stop Loss** and **Trailing Stop** strategies.

---

## 📌 Features

- 📈 Automated Binance Futures trading
- ⚡ Scalping strategy based on:
  - EMA 200
  - RSI
  - Parabolic SAR
- 🛡️ Automatic risk management:
  - Stop Loss
  - Trailing Stop
- 💰 Real-time PnL calculation
- 🖥️ Beautiful terminal UI using `rich`
- 🔄 Live price updates via CCXT/WebSocket
- 🧪 Binance Testnet support

---

## 📂 Project Structure

```bash
Scalpt/
│
├── main.py
│
└── src/
    ├── config.py
    └── utils.py
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/crisdimxs/Scalpt.git
cd Scalpt
```

---

### 2️⃣ Create a virtual environment (optional but recommended)

```bash
python -m venv venv
```

#### Linux / macOS

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```
---

## 🔑 Configuration

Edit the following file:

```bash
src/config.py
```

Configure your API credentials and settings:

```python
API_KEY = "YOUR_API_KEY"
SECRET = "YOUR_SECRET_KEY"

IS_TEST = True

TICKER = "BTCUSDT"
LEVERAGE = 5
TIME_FRAME = "5m"
```
---

## ▶️ Run the bot

```bash
python main.py
```

---

## 🧠 Strategy

The current strategy looks for:

### 📈 LONG Entry

- Parabolic SAR trend reversal
- Price above EMA 200
- RSI > 50

If conditions are met:

- Open a position
- Calculate Stop Loss
- Configure Trailing Stop automatically

---

## 🖥️ Terminal Interface

The bot displays in real-time:

- Current price
- Position type
- Entry Price
- Take Profit
- Stop Loss
- PnL
- Total wallet balance

---

## 📦 Main Dependencies

- `ccxt`
- `pandas`
- `numpy`
- `rich`
- `websocket-client`

---

## 🔮 Future Improvements

- [ ] SHORT support
- [ ] Full FinRL integration
- [ ] AI-powered trading signals
- [ ] Backtesting system
- [ ] Web dashboard
- [ ] Multi-asset trading

---

## ⚠️ Disclaimer

This project is for educational purposes only.  
Cryptocurrency trading involves significant financial risk.  
Use it at your own responsibility.

---

## 👨‍💻 Author

Developed by **crisdimxs**

- GitHub: https://github.com/crisdimxs/Scalpt
- X/Twitter: https://x.com/crisdimxs

---

# ⭐ Support the Project

If you like this project, leave a star on GitHub and contribute 🚀

