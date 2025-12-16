# 🚀 Getting Started Checklist

## ✅ Installation & Setup

### Step 1: Verify Python Installation
```bash
python --version
# Should be Python 3.8 or higher
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected packages:**
- pandas
- numpy
- matplotlib
- streamlit
- plotly

### Step 3: Generate Sample Data
```bash
python generate_sample_data.py
```

**What this does:**
- Creates `NASDAQ.csv` with 20 tickers
- Generates 500 days of synthetic data
- Uses realistic OHLCV patterns

**Expected output:**
```
✅ Successfully generated NASDAQ.csv
   Total rows: 10,000
   Date range: 2022-01-01 to 2023-11-30
   Tickers: AAPL, MSFT, GOOGL, AMZN, NVDA...
```

---

## 🎯 First Run

### Option A: Windows Quick Launch
```bash
# Double-click: launch_dashboard.bat
# OR from command line:
launch_dashboard.bat
```

### Option B: Manual Launch
```bash
streamlit run app.py
```

**Expected behavior:**
1. Terminal shows: "You can now view your Streamlit app in your browser"
2. Browser opens automatically to `http://localhost:8501`
3. Dashboard loads with welcome screen

---

## 🧪 Verify Installation

### Test Checklist:

- [ ] **Dashboard loads** without errors
- [ ] **Data preview** shows in welcome screen
- [ ] **Sidebar** displays controls
- [ ] **Strategy selection** shows 3 options
- [ ] **Parameter sliders** are interactive
- [ ] **"Run Backtest" button** is visible

### Run First Backtest:

1. [ ] Keep default strategy selection (Mean Reversion + Trend)
2. [ ] Keep default parameters (Max Positions = 5)
3. [ ] Click "🚀 Run Backtest" button
4. [ ] Wait ~5-10 seconds for processing
5. [ ] Verify success message appears

### Check Results:

- [ ] **Performance metrics** display (4 boxes)
- [ ] **Equity curve chart** renders
- [ ] **Correlation heatmap** shows (2x2 matrix)
- [ ] **Top holdings table** displays 5 assets
- [ ] **Download buttons** appear at bottom

---

## 🔧 Troubleshooting

### Problem: Dashboard won't start

**Error**: `streamlit: command not found`

**Solution**:
```bash
pip install --upgrade streamlit
```

---

### Problem: Import errors

**Error**: `ModuleNotFoundError: No module named 'strategy_base'`

**Solution**:
```bash
# Ensure you're in the correct directory
cd "c:\Users\f650922\OneDrive - Fortescue Metals Group\Desktop\Ensemble Model"

# Then run
streamlit run app.py
```

---

### Problem: Data not loading

**Error**: "❌ File not found: NASDAQ.csv"

**Solution**:
```bash
# Generate sample data
python generate_sample_data.py

# Or use fallback (dashboard will auto-generate)
# Just click "Run Backtest" anyway
```

---

### Problem: Charts not rendering

**Error**: Blank space where charts should be

**Solution**:
```bash
# Check Plotly installation
pip install --upgrade plotly

# Clear browser cache
# Try different browser (Chrome recommended)
```

---

### Problem: Slow performance

**Symptoms**: Dashboard takes long to load/run

**Solutions**:
1. Reduce data size:
   ```python
   # Edit generate_sample_data.py
   generate_nasdaq_csv(
       num_tickers=10,  # Reduce from 20
       num_days=250     # Reduce from 500
   )
   ```

2. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```

3. Restart dashboard

---

## 📚 Next Steps

### After successful first run:

1. **Read the Guide**
   ```bash
   # Open in text editor or browser
   STREAMLIT_GUIDE.md
   ```

2. **Experiment with Strategies**
   - Try selecting only one strategy
   - Compare performance
   - Add "Random (Benchmark)" to see baseline

3. **Adjust Parameters**
   - Change Max Positions (3 vs 15)
   - Modify MA Lookback (20 vs 200)
   - Vary SMA Period

4. **Analyze Correlation**
   - Check heatmap colors
   - Aim for low correlation (< 0.3)
   - Blue = good diversification

5. **Export Results**
   - Download equity curve CSV
   - Open in Excel for analysis
   - Compare multiple runs

---

## 🎓 Learning Path

### Beginner (Week 1)
- [ ] Complete installation
- [ ] Run 3 backtests with default settings
- [ ] Understand performance metrics
- [ ] Read welcome screen guide

### Intermediate (Week 2)
- [ ] Try all strategy combinations
- [ ] Adjust 5 different parameters
- [ ] Compare correlation matrices
- [ ] Export and analyze in Excel

### Advanced (Week 3)
- [ ] Add custom strategy (see QUICK_REFERENCE.md)
- [ ] Optimize parameters systematically
- [ ] Use real market data (see STREAMLIT_GUIDE.md)
- [ ] Implement live trading (advanced)

---

## 📊 Quick Reference

### Dashboard Sections:
| Section | Purpose |
|---------|---------|
| Sidebar | Strategy selection & parameters |
| Performance Summary | Key metrics at a glance |
| Equity Curve | Portfolio value over time |
| Correlation Matrix | Strategy diversification |
| Top Holdings | Current portfolio composition |
| Export | Download results |

### Key Metrics:
| Metric | Good Value | Interpretation |
|--------|------------|----------------|
| Sharpe Ratio | > 1.5 | Risk-adjusted return |
| Max Drawdown | < -20% | Largest loss |
| Win Rate | > 50% | Trade profitability |
| Total Return | > 15% | Absolute performance |

### Strategy Types:
| Strategy | Philosophy | Best For |
|----------|------------|----------|
| Mean Reversion | Contrarian | Range-bound markets |
| Trend Following | Momentum | Trending markets |
| Random | Baseline | Benchmark comparison |

---

## ✅ Success Criteria

You're ready to move forward when you can:

- [ ] Launch dashboard without errors
- [ ] Run backtest with default settings
- [ ] See all charts render correctly
- [ ] Understand basic metrics (Sharpe, Drawdown)
- [ ] Change parameters and see impact
- [ ] Export results successfully

---

## 🆘 Need Help?

### Documentation Files:
1. `STREAMLIT_GUIDE.md` - Comprehensive usage guide
2. `DASHBOARD_SUMMARY.md` - Feature overview
3. `QUICK_REFERENCE.md` - Code customization
4. `README.md` - Architecture details

### Code Files:
1. `app.py` - Main dashboard (800 lines)
2. `strategy_base.py` - Strategy interface
3. `portfolio_manager.py` - Ensemble engine
4. `backtest_engine.py` - Simulation system

### In-Code Help:
- Hover over parameter labels for tooltips
- Check welcome screen for quick start
- Look for ℹ️ℹ️, ⚠️, ✅ symbols for guidance

---

## 🎯 Final Checklist

Before considering setup complete:

- [ ] Python 3.8+ installed
- [ ] All requirements installed (`pip list`)
- [ ] NASDAQ.csv generated and present
- [ ] Dashboard launches successfully
- [ ] First backtest runs without errors
- [ ] All charts render correctly
- [ ] Understand how to change parameters
- [ ] Know where to find documentation
- [ ] Can export results
- [ ] Ready to experiment!

---

**Congratulations! You're ready to use the Ensemble Trading Research Lab** 🎉

Start experimenting with different strategies and parameters to find optimal configurations!

---

**Need to reinstall?**
```bash
# Clean reinstall
pip uninstall pandas numpy matplotlib streamlit plotly -y
pip install -r requirements.txt

# Regenerate data
python generate_sample_data.py

# Launch
streamlit run app.py
```

**Questions or issues?**
Check the comprehensive guides in the documentation folder.

---

*Last Updated: December 16, 2025*
*Version: 1.0*
