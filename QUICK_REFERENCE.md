# Quick Reference Guide

## 📚 File Overview

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `strategy_base.py` | Abstract base class | `Strategy` |
| `mean_reversion_strategy.py` | Strategy A | `MeanReversionQP` |
| `trend_strategy.py` | Strategy B | `SimpleTrend` |
| `momentum_strategy.py` | Strategy C (optional) | `MomentumStrategy` |
| `portfolio_manager.py` | Ensemble engine | `PortfolioManager`, `PortfolioConfig` |
| `backtest_engine.py` | Backtesting system | `BacktestEngine` |
| `config.py` | Configuration management | `SystemConfig`, presets |
| `main.py` | Main execution script | `main()` |
| `test_system.py` | Verification tests | Test functions |
| `architecture.py` | Documentation | ASCII diagrams |

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full system
python main.py

# Run tests only (no matplotlib required)
python test_system.py

# View architecture
python architecture.py
```

## 🔧 Common Customizations

### 1. Change Number of Assets Selected
```python
# In main.py
config = PortfolioConfig(
    top_n_assets=10  # Change from 5 to 10
)
```

### 2. Adjust Strategy Parameters
```python
# Mean Reversion
mean_reversion = MeanReversionQP(
    lookback_ma=100,      # Longer moving average
    lookback_vol=30,      # More recent volatility
    historical_vol_period=200
)

# Trend Following
trend = SimpleTrend(
    sma_period=50  # Shorter SMA for faster signals
)
```

### 3. Add a New Strategy
```python
# 1. Create new_strategy.py
from strategy_base import Strategy

class MyStrategy(Strategy):
    def generate_signals(self, data):
        # Your logic
        return df[['signal', 'confidence']]

# 2. In main.py
from new_strategy import MyStrategy
my_strat = MyStrategy(name="Custom")

portfolio_manager = PortfolioManager(
    strategies=[mean_reversion, trend, my_strat]
)
```

### 4. Change Backtest Settings
```python
backtest = BacktestEngine(
    initial_capital=250000,  # $250k starting capital
    commission=0.002,        # 0.2% commission
    slippage=0.001           # 0.1% slippage
)
```

## 📊 Output Interpretation

### Strategy Correlation Matrix
```
                    signal_MeanReversion  signal_TrendFollowing
signal_MeanReversion                1.000                 -0.234
signal_TrendFollowing              -0.234                  1.000
```
- **Near 0**: Strategies are independent (good diversification)
- **Near +1**: Strategies are redundant (consider removing one)
- **Near -1**: Strategies are opposite (hedge each other)

### Performance Metrics
- **Sharpe Ratio**: Risk-adjusted return (> 1.0 is good, > 2.0 is excellent)
- **Maximum Drawdown**: Largest peak-to-trough decline (lower is better)
- **Win Rate**: % of profitable trades (> 50% is good)

### Combined Score
The sum of normalized signals from all strategies:
- **High positive**: Strong consensus to BUY
- **Near zero**: No consensus
- **High negative**: Strong consensus to SELL

## 🐛 Troubleshooting

### Issue: "No module named 'pandas'"
**Solution**: 
```bash
pip install pandas numpy matplotlib
```

### Issue: Signals are all zeros
**Cause**: Not enough data for lookback periods  
**Solution**: Increase `num_days` or decrease lookback periods

### Issue: Performance is poor
**Possible causes**:
1. Market regime doesn't match strategies
2. Transaction costs too high
3. Top N assets too many/few

**Solutions**:
- Try different strategy combinations
- Adjust parameters using `config.py`
- Test on real market data

## 📈 Advanced Usage

### Using Real Market Data
```python
# Instead of generate_mock_market_data(), load real data:
import yfinance as yf

tickers = ['AAPL', 'MSFT', 'GOOGL']
data = []

for ticker in tickers:
    df = yf.download(ticker, start='2020-01-01')
    df['ticker'] = ticker
    data.append(df)

market_data = pd.concat(data)
market_data = market_data.reset_index()
market_data = market_data.set_index(['Date', 'ticker'])
market_data.columns = market_data.columns.str.lower()
```

### Parameter Optimization
```python
# Grid search for best parameters
best_sharpe = 0
best_params = None

for top_n in [3, 5, 7, 10]:
    for ma_period in [20, 50, 100]:
        config = PortfolioConfig(top_n_assets=top_n)
        mr = MeanReversionQP(lookback_ma=ma_period)
        
        # Run backtest
        pm = PortfolioManager([mr, trend], config)
        signals = pm.generate_ensemble_signals(data)
        bt = BacktestEngine()
        bt.run(data, signals)
        
        metrics = bt.get_performance_metrics()
        sharpe = float(metrics['Sharpe Ratio'])
        
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (top_n, ma_period)

print(f"Best: top_n={best_params[0]}, ma={best_params[1]}, Sharpe={best_sharpe}")
```

### Live Trading Integration
```python
# Pseudocode for live trading
def live_trading_loop():
    while True:
        # Fetch latest market data
        current_data = fetch_live_data()
        
        # Generate signals
        signals = portfolio_manager.generate_ensemble_signals(current_data)
        
        # Get today's weights
        weights = portfolio_manager.get_portfolio_weights(today)
        
        # Execute trades via broker API
        for ticker, weight in weights.items():
            place_order(ticker, weight * portfolio_value)
        
        # Wait until next rebalance
        time.sleep(rebalance_interval)
```

## 💡 Best Practices

1. **Start Simple**: Test with 2-3 strategies before adding more
2. **Check Correlation**: Ensure strategies are diversified
3. **Validate on Out-of-Sample Data**: Don't overfit to training data
4. **Monitor Transaction Costs**: High turnover can kill performance
5. **Use Realistic Parameters**: Match commission/slippage to your broker
6. **Version Control**: Use git to track strategy changes
7. **Document Assumptions**: Note why you chose specific parameters

## 📞 Support

For questions or issues:
1. Check the README.md for architecture details
2. Run test_system.py to verify installation
3. Review architecture.py for component descriptions
4. Inspect individual strategy files for implementation details

---

**Version**: 1.0  
**Date**: December 16, 2025  
**Author**: Lead Quantitative Software Architect
