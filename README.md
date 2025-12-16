# Ensemble Trading System - Modular Architecture

## 🎯 Overview
A modular, object-oriented, event-driven framework for combining multiple trading strategies into an ensemble. Built following "The Bitter Lesson" (simple, scalable components) and "Learning to Rank" (relative comparison of signals).

## 📁 Project Structure

```
Ensemble Model/
├── strategy_base.py              # Abstract base class for all strategies
├── mean_reversion_strategy.py    # Strategy A: Mean Reversion (Murphy's Law)
├── trend_strategy.py              # Strategy B: Simple Trend Following
├── portfolio_manager.py           # Ensemble Engine (combines strategies)
├── backtest_engine.py             # Event-driven backtesting system
├── main.py                        # Main execution script
└── README.md                      # This file
```

## 🏗️ Architecture

### 1. Strategy Base Class (`Strategy`)
All strategies inherit from this abstract class and must implement:
- `generate_signals(data) -> pd.DataFrame`
- Returns standardized signals: -1.0 (strong sell) to +1.0 (strong buy)

### 2. Strategy Implementations

#### Mean Reversion (MeanReversionQP)
- **Logic**: Buy when QPI (Quality-Price Indicator) is low
- **Signal**: Inverse normalized QPI
- **Parameters**: `lookback_ma`, `lookback_vol`, `historical_vol_period`

#### Simple Trend (SimpleTrend)
- **Logic**: Buy when price > SMA
- **Signal**: Distance from SMA (tanh scaled)
- **Parameters**: `sma_period`

### 3. Portfolio Manager (Ensemble Engine)
- **Combines** multiple strategies
- **Normalizes** signals using z-score
- **Ranks** assets by combined score
- **Selects** top N assets
- **Reports** strategy correlation matrix

### 4. Backtest Engine
- Event-driven simulation
- Includes commission & slippage
- Tracks equity curve, drawdown, trades
- Generates performance metrics

## 🚀 Quick Start

### Installation
```bash
pip install pandas numpy matplotlib
```

### Run the System
```bash
python main.py
```

## 🔧 Adding a New Strategy (Strategy C)

**Step 1**: Create your strategy class

```python
# momentum_strategy.py
from strategy_base import Strategy
import pandas as pd
import numpy as np

class MomentumStrategy(Strategy):
    def __init__(self, name="Momentum", lookback=20):
        super().__init__(name)
        self.lookback = lookback
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate momentum
        df['momentum'] = df.groupby(level='ticker')['close'].pct_change(self.lookback)
        
        # Normalize to [-1, 1]
        df['signal'] = np.tanh(df['momentum'] * 10)
        df['signal'] = df['signal'].fillna(0.0)
        
        df['confidence'] = 0.8
        
        return df[['signal', 'confidence']]
```

**Step 2**: Add to `main.py`

```python
from momentum_strategy import MomentumStrategy

# In main():
momentum = MomentumStrategy(name="Momentum", lookback=20)

portfolio_manager = PortfolioManager(
    strategies=[mean_reversion, trend_following, momentum],  # Add here!
    config=config
)
```

That's it! The ensemble automatically incorporates the new strategy.

## 📊 Output

The system produces:

1. **Console Output**
   - Strategy correlation matrix
   - Top assets per day
   - Performance metrics (Sharpe, Drawdown, Win Rate)

2. **Visualization** (`ensemble_backtest_results.png`)
   - Equity curve
   - Drawdown chart
   - Number of positions over time

## 🧠 Key Insights

### Strategy Correlation Matrix
Shows how correlated strategies are:
- **Low correlation** → Good diversification
- **High correlation** → Redundant strategies

### Combined Score
The ensemble sums normalized signals:
- If MeanReversion = +0.8 and Trend = +0.5 → Combined = +1.3
- Higher combined score → Higher conviction

### Learning to Rank
Rather than predicting absolute returns, we rank assets relatively:
- Top 5 combined scores → Portfolio selection
- This is more robust than trying to predict exact prices

## ⚙️ Configuration

```python
# In main.py
config = PortfolioConfig(
    top_n_assets=5,              # Select top N assets
    rebalance_frequency='daily',  # Rebalancing frequency
    equal_weight=True,            # Equal or proportional weighting
    long_only=True                # Long-only or long/short
)

backtest = BacktestEngine(
    initial_capital=100000.0,
    commission=0.001,             # 0.1% commission
    slippage=0.0005               # 0.05% slippage
)
```

## 🎓 Philosophy

### The Bitter Lesson (Rich Sutton)
- Keep components simple
- Let the system scale with data
- Avoid hand-crafted complexity

### Learning to Rank
- Focus on relative comparison, not absolute prediction
- Rank assets against each other
- Top-N selection is more robust than binary buy/sell

## 📈 Performance Metrics

- **Total Return**: Cumulative portfolio return
- **Sharpe Ratio**: Risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Annualized Return & Volatility**

## 🔬 Future Enhancements

1. **More Strategies**: Momentum, Volume, Sentiment, ML-based
2. **Optimization**: Grid search for parameters
3. **Risk Management**: Position sizing, stop-loss
4. **Live Trading**: Connect to broker API
5. **Real Data**: Integrate with Yahoo Finance, Alpha Vantage
6. **Advanced Combination**: Weighted average, meta-learning

## 📝 License
MIT License - Feel free to extend and modify!

## 👨‍💻 Author
Lead Quantitative Software Architect  
Date: December 16, 2025
