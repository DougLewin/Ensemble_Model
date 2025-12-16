# Streamlit Dashboard Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data (if you don't have NASDAQ.csv)
```bash
python generate_sample_data.py
```

### 3. Launch the Dashboard
```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📊 Dashboard Features

### Sidebar (Control Panel)

#### 📁 Data Source
- **CSV Filename**: Enter the path to your NASDAQ data file
- Default: `NASDAQ.csv`
- Format required: `Date, Ticker, Open, High, Low, Close, Volume`

#### 🎯 Ensemble Composition
Select which strategies to include:
- **Mean Reversion (QP)**: Contrarian strategy, buys undervalued assets
- **Trend Following**: Momentum strategy, follows trends
- **Random (Benchmark)**: Random signals for baseline comparison

You can select 1 or more strategies. The ensemble combines their signals.

#### 📐 Parameters

**Portfolio Settings:**
- **Max Positions**: Number of assets to hold simultaneously (3-20)
  - Lower = More concentrated portfolio
  - Higher = More diversified portfolio

**Strategy-Specific Settings:**

*Mean Reversion:*
- **MA Lookback** (20-200): Moving average period
  - Lower = Faster reaction to price changes
  - Higher = Smoother, less sensitive to noise
  
- **Volatility Lookback** (10-60): Recent volatility calculation window
  
- **Historical Vol Period** (50-500): Long-term volatility baseline

*Trend Following:*
- **SMA Period** (20-200): Simple moving average for trend detection
  - Lower = Faster trend signals, more trades
  - Higher = Slower trend signals, fewer trades

**Backtest Settings:**
- **Initial Capital**: Starting portfolio value
- **Commission**: Trading fees per transaction (%)
- **Slippage**: Price impact of trades (%)

#### 🚀 Run Backtest
Click this button to execute the ensemble with current settings.

### Main Page (Results)

#### 📈 Performance Summary
Four key metrics displayed prominently:

1. **Total Return**: Cumulative return over the period
   - Shows overall profitability

2. **Sharpe Ratio**: Risk-adjusted return
   - \> 1.0 = Good
   - \> 2.0 = Excellent
   - \> 3.0 = Outstanding

3. **Max Drawdown**: Largest peak-to-trough decline
   - Measures worst-case scenario
   - Lower is better (less risky)

4. **Win Rate**: Percentage of profitable trades
   - \> 50% = More winners than losers

**Detailed Metrics** (expandable):
- Annualized Return & Volatility
- Total Trades & Average Positions
- Final Value vs Initial Capital

#### 💰 Equity Curve
Interactive line chart showing portfolio value over time.

**Features:**
- Hover to see exact values
- Zoom in/out with mouse
- Pan by dragging
- Reset view with home button
- Dashed line shows initial capital

**Interpretation:**
- Upward slope = Profitable strategy
- Smooth curve = Stable returns
- Volatile curve = Risky strategy
- Curve above initial capital = Positive return

#### 📉 Drawdown Analysis (expandable)
Shows how much the portfolio has declined from its peak at any point.

**Interpretation:**
- Deeper dips = Larger losses before recovery
- Longer dips = Slower recovery time
- Frequent dips = High volatility
- Shallow dips = Consistent performance

#### 🔗 Strategy Correlation Matrix
Heatmap showing how correlated the selected strategies are.

**Color Scale:**
- **Blue** = Negative correlation (strategies move opposite)
- **White** = No correlation (independent)
- **Red** = Positive correlation (strategies move together)

**Numbers:**
- **-1.0**: Perfect negative correlation (perfect hedge)
- **0.0**: No correlation (ideal for diversification)
- **+1.0**: Perfect positive correlation (redundant)

**Guidelines:**
- Average correlation < 0.3 = Excellent diversification ✅
- Average correlation 0.3-0.6 = Moderate diversification ℹ️
- Average correlation > 0.6 = High correlation (consider more diverse strategies) ⚠️

#### 🏆 Top Holdings
Shows the assets selected in the last rebalance.

**Columns:**
- **Combined Score**: Sum of normalized signals from all strategies
- **Rank**: Position in the ranking (1 = highest score)
- **Weight**: Portfolio allocation (% of capital)

**Usage:**
- Higher combined score = Stronger conviction
- Rank 1 = Most attractive asset according to ensemble
- Weight shows actual capital allocation

#### 💾 Export Results
Download results for further analysis:

1. **Equity Curve**: Daily portfolio values
2. **Signals**: All ensemble signals and rankings

Files are timestamped for version tracking.

## 🎯 Usage Strategies

### Strategy 1: Conservative Portfolio
```
Strategies: Mean Reversion + Trend Following
Max Positions: 3-5
MA Lookback: 100-200 (longer)
SMA Period: 150-200 (longer)
Commission: 0.1-0.2%
```
**Best For:** Risk-averse investors, stable returns

### Strategy 2: Aggressive Portfolio
```
Strategies: All three (including Random for baseline)
Max Positions: 10-15
MA Lookback: 20-50 (shorter)
SMA Period: 50-100 (shorter)
Commission: 0.05-0.1%
```
**Best For:** Higher risk tolerance, capturing short-term opportunities

### Strategy 3: Diversified Ensemble
```
Strategies: Mean Reversion + Trend Following
Max Positions: 7-10
MA Lookback: 50-75 (medium)
SMA Period: 100-150 (medium)
Commission: 0.1%
```
**Best For:** Balanced risk/return, most market conditions

## 🔬 Experimentation Workflow

### 1. Baseline Run
- Start with default settings
- Select Mean Reversion + Trend Following
- Run backtest and note Sharpe Ratio

### 2. Strategy Isolation
- Run each strategy individually
- Compare individual vs ensemble performance
- Verify ensemble improves over single strategies

### 3. Parameter Sensitivity
- Vary one parameter at a time
- Observe impact on Sharpe Ratio and Max Drawdown
- Find optimal parameter ranges

### 4. Correlation Analysis
- Check strategy correlation matrix
- If correlation > 0.7, consider removing redundant strategy
- Aim for diverse, uncorrelated strategies

### 5. Transaction Cost Impact
- Test with different commission rates
- If Sharpe drops significantly with realistic costs, strategy may not be viable
- High turnover strategies suffer more from costs

## 📝 Tips & Best Practices

### Performance Tips

1. **Data Quality Matters**
   - Use clean, accurate historical data
   - Ensure no missing dates or prices
   - Check for corporate actions (splits, dividends)

2. **Start with Longer Backtests**
   - 500+ days recommended
   - Covers multiple market regimes
   - More reliable statistics

3. **Don't Overfit**
   - Avoid excessive parameter tuning
   - Test on out-of-sample data
   - If backtest is "too good", it's probably overfit

4. **Consider Transaction Costs**
   - Use realistic commission and slippage
   - High-frequency strategies may not be viable after costs
   - Account for spread and market impact

### Dashboard Usage Tips

1. **Use Cached Data**
   - Dashboard caches the CSV load
   - Changes to CSV require dashboard restart
   - Faster iteration on parameters

2. **Compare Multiple Runs**
   - Take screenshots or export results
   - Create a spreadsheet to track experiments
   - Note which configurations work best

3. **Focus on Risk-Adjusted Returns**
   - Sharpe Ratio > Total Return
   - Prefer consistent 15% with low drawdown over volatile 30%
   - Max Drawdown limits emotional stress

4. **Diversification is Key**
   - Low strategy correlation = better ensemble
   - Add strategies with different philosophies
   - Mean Reversion + Trend = complementary approaches

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check Streamlit installation
pip install --upgrade streamlit

# Try specifying port
streamlit run app.py --server.port 8502
```

### "File Not Found" Error
```bash
# Ensure NASDAQ.csv is in the same directory as app.py
ls  # or dir on Windows

# Generate sample data
python generate_sample_data.py
```

### Slow Performance
```bash
# Clear Streamlit cache
streamlit cache clear

# Reduce data size (fewer tickers or shorter period)
# Edit generate_sample_data.py and regenerate
```

### Correlation Matrix Not Showing
- Need at least 2 strategies selected
- Ensure backtest has completed successfully
- Check browser console for errors

### Poor Performance Results
- Verify data quality and date range
- Ensure sufficient lookback periods
- Try different parameter combinations
- Some strategies work better in certain market regimes

## 🔗 Integration with Real Data

### Using Yahoo Finance Data
```python
import yfinance as yf
import pandas as pd

# Download data
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
data = []

for ticker in tickers:
    df = yf.download(ticker, start='2020-01-01', end='2024-12-31')
    df['Ticker'] = ticker
    df = df.reset_index()
    df = df.rename(columns={'index': 'Date'})
    data.append(df)

df = pd.concat(data, ignore_index=True)

# Save as NASDAQ.csv
df.to_csv('NASDAQ.csv', index=False)
```

### Using Alpha Vantage
```python
import requests
import pandas as pd

API_KEY = 'your_api_key'
tickers = ['AAPL', 'MSFT', 'GOOGL']

data = []

for ticker in tickers:
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={API_KEY}&outputsize=full'
    r = requests.get(url)
    daily_data = r.json()['Time Series (Daily)']
    
    for date, values in daily_data.items():
        data.append({
            'Date': date,
            'Ticker': ticker,
            'Open': float(values['1. open']),
            'High': float(values['2. high']),
            'Low': float(values['3. low']),
            'Close': float(values['4. close']),
            'Volume': int(values['6. volume'])
        })

df = pd.DataFrame(data)
df.to_csv('NASDAQ.csv', index=False)
```

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **README.md**: Architecture and strategy details
- **QUICK_REFERENCE.md**: Code customization guide

---

**Version**: 1.0  
**Last Updated**: December 16, 2025  
**Questions?** Check the code comments in `app.py` for implementation details.
