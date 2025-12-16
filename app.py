"""
Streamlit Trading Dashboard - Interactive Research Lab
=======================================================
Full-stack quantitative dashboard for ensemble trading strategies.

Author: Full-Stack Quantitative Developer
Date: December 16, 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our trading engine components
from strategy_base import Strategy
from mean_reversion_strategy import MeanReversionQP
from trend_strategy import SimpleTrend
from portfolio_manager import PortfolioManager, PortfolioConfig
from backtest_engine import BacktestEngine

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Ensemble Trading Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DATA LOADING (WITH CACHING)
# ============================================================

@st.cache_data
def load_nasdaq_data(filepath: str = "NASDAQ.csv") -> pd.DataFrame:
    """
    Load NASDAQ data with caching for performance.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with MultiIndex (date, ticker) and OHLCV columns
    """
    try:
        # Load CSV
        df = pd.read_csv(filepath)
        
        # Standardize column names (lowercase)
        df.columns = df.columns.str.lower()
        
        # Rename columns if needed
        column_mapping = {
            'date': 'date',
            'ticker': 'ticker',
            'symbol': 'ticker',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Set MultiIndex
        df = df.set_index(['date', 'ticker'])
        
        # Sort index
        df = df.sort_index()
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ File not found: {filepath}")
        st.info("📁 Please ensure NASDAQ.csv is in the current directory.")
        
        # Generate synthetic data as fallback
        st.warning("⚠️ Using synthetic data for demonstration...")
        return generate_fallback_data()
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return generate_fallback_data()


def generate_fallback_data() -> pd.DataFrame:
    """Generate synthetic data if NASDAQ.csv is not available."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', periods=500, freq='D')
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'WMT']
    
    data = []
    for ticker in tickers:
        drift = np.random.uniform(-0.0002, 0.0005)
        volatility = np.random.uniform(0.015, 0.03)
        
        returns = np.random.normal(drift, volatility, len(dates))
        initial_price = np.random.uniform(100, 300)
        prices = initial_price * np.exp(np.cumsum(returns))
        
        for date, price in zip(dates, prices):
            daily_vol = volatility * price
            data.append({
                'date': date,
                'ticker': ticker,
                'open': price + np.random.normal(0, daily_vol * 0.5),
                'high': price + abs(np.random.normal(0, daily_vol)),
                'low': price - abs(np.random.normal(0, daily_vol)),
                'close': price,
                'volume': int(np.random.uniform(1e6, 1e7))
            })
    
    df = pd.DataFrame(data)
    df = df.set_index(['date', 'ticker'])
    
    return df


# ============================================================
# HELPER CLASSES
# ============================================================

class RandomStrategy(Strategy):
    """
    Random Strategy (Benchmark/Placeholder).
    Generates random signals for comparison.
    """
    
    def __init__(self, name: str = "Random", seed: int = 42):
        super().__init__(name)
        self.seed = seed
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        np.random.seed(self.seed)
        df = data.copy()
        
        # Generate random signals
        df['signal'] = np.random.uniform(-1, 1, len(df))
        df['confidence'] = np.random.uniform(0.3, 0.7, len(df))
        
        return df[['signal', 'confidence']]
    
    def __repr__(self) -> str:
        return f"RandomStrategy(name='{self.name}')"


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("📊 Ensemble Trading Research Lab")
st.markdown("""
Interactive dashboard for testing and analyzing ensemble trading strategies.
Select strategies, configure parameters, and visualize performance in real-time.
""")

# ============================================================
# SIDEBAR - CONTROL PANEL
# ============================================================

st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("---")

# Load data
st.sidebar.subheader("📁 Data Source")
data_file = st.sidebar.text_input("CSV Filename", value="NASDAQ.csv")

with st.spinner("Loading market data..."):
    market_data = load_nasdaq_data(data_file)

if market_data is not None and len(market_data) > 0:
    # Display data info
    num_tickers = len(market_data.index.get_level_values('ticker').unique())
    date_range = market_data.index.get_level_values('date').unique()
    start_date = date_range.min()
    end_date = date_range.max()
    
    st.sidebar.success("✅ Data Loaded")
    st.sidebar.metric("Tickers", num_tickers)
    st.sidebar.metric("Date Range", f"{start_date.date()} to {end_date.date()}")
    st.sidebar.metric("Total Records", f"{len(market_data):,}")
else:
    st.sidebar.error("❌ No data available")
    st.stop()

st.sidebar.markdown("---")

# ============================================================
# STRATEGY SELECTION
# ============================================================

st.sidebar.subheader("🎯 Ensemble Composition")

available_strategies = {
    "Mean Reversion (QP)": "mean_reversion",
    "Trend Following": "trend",
    "Random (Benchmark)": "random"
}

selected_strategies = st.sidebar.multiselect(
    "Select Strategies",
    options=list(available_strategies.keys()),
    default=["Mean Reversion (QP)", "Trend Following"],
    help="Choose which strategies to include in the ensemble"
)

if len(selected_strategies) == 0:
    st.warning("⚠️ Please select at least one strategy from the sidebar.")
    st.stop()

st.sidebar.markdown("---")

# ============================================================
# PARAMETERS
# ============================================================

st.sidebar.subheader("📐 Parameters")

# Portfolio parameters
top_n_assets = st.sidebar.slider(
    "Max Positions",
    min_value=3,
    max_value=min(20, num_tickers),
    value=5,
    help="Maximum number of assets to hold simultaneously"
)

# Strategy-specific parameters
with st.sidebar.expander("Mean Reversion Settings", expanded=False):
    mr_lookback_ma = st.slider("MA Lookback", 20, 200, 50)
    mr_lookback_vol = st.slider("Volatility Lookback", 10, 60, 20)
    mr_hist_vol = st.slider("Historical Vol Period", 50, 500, 100)

with st.sidebar.expander("Trend Following Settings", expanded=False):
    trend_sma_period = st.slider("SMA Period", 20, 200, 100)

# Backtest parameters
with st.sidebar.expander("Backtest Settings", expanded=False):
    initial_capital = st.number_input("Initial Capital ($)", value=100000, step=10000)
    commission = st.number_input("Commission (%)", value=0.1, step=0.05) / 100
    slippage = st.number_input("Slippage (%)", value=0.05, step=0.01) / 100

st.sidebar.markdown("---")

# ============================================================
# RUN BUTTON
# ============================================================

run_backtest = st.sidebar.button("🚀 Run Backtest", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ by Quantitative Research Team")

# ============================================================
# MAIN PAGE - RESULTS
# ============================================================

if run_backtest:
    
    with st.spinner("Running ensemble backtest..."):
        
        # --------------------------------------------------------
        # Step 1: Initialize selected strategies
        # --------------------------------------------------------
        
        strategy_objects = []
        
        for strategy_name in selected_strategies:
            strategy_type = available_strategies[strategy_name]
            
            if strategy_type == "mean_reversion":
                strategy_objects.append(MeanReversionQP(
                    name="MeanReversion",
                    lookback_ma=mr_lookback_ma,
                    lookback_vol=mr_lookback_vol,
                    historical_vol_period=mr_hist_vol
                ))
            
            elif strategy_type == "trend":
                strategy_objects.append(SimpleTrend(
                    name="TrendFollowing",
                    sma_period=trend_sma_period
                ))
            
            elif strategy_type == "random":
                strategy_objects.append(RandomStrategy(
                    name="Random"
                ))
        
        # --------------------------------------------------------
        # Step 2: Create Portfolio Manager
        # --------------------------------------------------------
        
        config = PortfolioConfig(
            top_n_assets=top_n_assets,
            rebalance_frequency='daily',
            equal_weight=True,
            long_only=True
        )
        
        portfolio_manager = PortfolioManager(
            strategies=strategy_objects,
            config=config
        )
        
        # --------------------------------------------------------
        # Step 3: Generate Ensemble Signals
        # --------------------------------------------------------
        
        ensemble_signals = portfolio_manager.generate_ensemble_signals(market_data)
        
        # --------------------------------------------------------
        # Step 4: Run Backtest
        # --------------------------------------------------------
        
        backtest_engine = BacktestEngine(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        
        equity_curve = backtest_engine.run(market_data, ensemble_signals)
        metrics = backtest_engine.get_performance_metrics()
        
    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------
    
    st.success("✅ Backtest completed successfully!")
    
    # --------------------------------------------------------
    # Section 1: Performance Summary
    # --------------------------------------------------------
    
    st.header("📈 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Return",
            metrics['Total Return'],
            help="Cumulative return over the entire period"
        )
    
    with col2:
        st.metric(
            "Sharpe Ratio",
            metrics['Sharpe Ratio'],
            help="Risk-adjusted return (>1.0 is good, >2.0 is excellent)"
        )
    
    with col3:
        st.metric(
            "Max Drawdown",
            metrics['Maximum Drawdown'],
            delta=None,
            delta_color="inverse",
            help="Largest peak-to-trough decline"
        )
    
    with col4:
        st.metric(
            "Win Rate",
            metrics['Win Rate'],
            help="Percentage of profitable trades"
        )
    
    # Additional metrics in expandable section
    with st.expander("📊 Detailed Metrics", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Annualized Return", metrics['Annualized Return'])
            st.metric("Annualized Volatility", metrics['Annualized Volatility'])
        
        with col_b:
            st.metric("Total Trades", metrics['Total Trades'])
            st.metric("Avg Positions", f"{metrics['Avg Positions']:.1f}")
        
        with col_c:
            st.metric("Final Value", metrics['Final Value'])
            st.metric("Initial Capital", f"${initial_capital:,.2f}")
    
    st.markdown("---")
    
    # --------------------------------------------------------
    # Section 2: Equity Curve
    # --------------------------------------------------------
    
    st.header("💰 Equity Curve")
    
    # Create interactive Plotly chart
    fig_equity = go.Figure()
    
    fig_equity.add_trace(go.Scatter(
        x=equity_curve.index,
        y=equity_curve['portfolio_value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#2E86AB', width=2),
        fill='tonexty',
        fillcolor='rgba(46, 134, 171, 0.1)'
    ))
    
    # Add initial capital line
    fig_equity.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        annotation_text="Initial Capital",
        annotation_position="right"
    )
    
    fig_equity.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_equity, use_container_width=True)
    
    # --------------------------------------------------------
    # Section 3: Drawdown Chart
    # --------------------------------------------------------
    
    with st.expander("📉 Drawdown Analysis", expanded=False):
        
        # Calculate drawdown
        returns = equity_curve['portfolio_value'].pct_change()
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        fig_dd = go.Figure()
        
        fig_dd.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown * 100,
            mode='lines',
            name='Drawdown',
            line=dict(color='#A23B72', width=2),
            fill='tozeroy',
            fillcolor='rgba(162, 59, 114, 0.3)'
        ))
        
        fig_dd.update_layout(
            title="Portfolio Drawdown",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_dd, use_container_width=True)
    
    st.markdown("---")
    
    # --------------------------------------------------------
    # Section 4: Strategy Correlation Heatmap
    # --------------------------------------------------------
    
    st.header("🔗 Strategy Correlation Matrix")
    
    st.markdown("""
    **Interpretation:**
    - **Low correlation (near 0)**: Strategies are independent → Good diversification
    - **High positive (near +1)**: Strategies are redundant → Consider removing one
    - **High negative (near -1)**: Strategies hedge each other
    """)
    
    if portfolio_manager.correlation_matrix is not None:
        
        # Clean up column names for display
        corr_matrix = portfolio_manager.correlation_matrix.copy()
        corr_matrix.columns = [col.replace('signal_', '') for col in corr_matrix.columns]
        corr_matrix.index = [idx.replace('signal_', '') for idx in corr_matrix.index]
        
        # Create heatmap
        fig_corr = px.imshow(
            corr_matrix,
            text_auto='.3f',
            color_continuous_scale='RdBu_r',
            color_continuous_midpoint=0,
            aspect='auto',
            labels=dict(color="Correlation")
        )
        
        fig_corr.update_layout(
            title="Strategy Signal Correlation",
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Correlation insights
        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
        
        if avg_corr < 0.3:
            st.success(f"✅ Excellent diversification! Average correlation: {avg_corr:.3f}")
        elif avg_corr < 0.6:
            st.info(f"ℹ️ Moderate diversification. Average correlation: {avg_corr:.3f}")
        else:
            st.warning(f"⚠️ High correlation detected. Average: {avg_corr:.3f}. Consider more diverse strategies.")
    
    else:
        st.warning("⚠️ Correlation matrix not available. Need at least 2 strategies.")
    
    st.markdown("---")
    
    # --------------------------------------------------------
    # Section 5: Top Holdings
    # --------------------------------------------------------
    
    st.header("🏆 Top Holdings (Last Rebalance)")
    
    last_date = ensemble_signals.index.get_level_values('date').unique()[-1]
    top_assets = portfolio_manager.get_top_assets(last_date, top_n=top_n_assets)
    
    if len(top_assets) > 0:
        
        # Format for display
        display_df = top_assets.copy()
        display_df['combined_score'] = display_df['combined_score'].round(3)
        display_df['weight'] = (display_df['weight'] * 100).round(2).astype(str) + '%'
        display_df['rank'] = display_df['rank'].astype(int)
        
        display_df = display_df.rename(columns={
            'combined_score': 'Combined Score',
            'rank': 'Rank',
            'weight': 'Weight'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=300
        )
    
    else:
        st.warning("⚠️ No holdings data available.")
    
    st.markdown("---")
    
    # --------------------------------------------------------
    # Section 6: Download Results
    # --------------------------------------------------------
    
    st.header("💾 Export Results")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # Export equity curve
        equity_csv = equity_curve.to_csv()
        st.download_button(
            label="📥 Download Equity Curve",
            data=equity_csv,
            file_name=f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_dl2:
        # Export signals
        signals_csv = ensemble_signals.to_csv()
        st.download_button(
            label="📥 Download Signals",
            data=signals_csv,
            file_name=f"ensemble_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    # --------------------------------------------------------
    # WELCOME SCREEN (Before running backtest)
    # --------------------------------------------------------
    
    st.info("👈 Configure your ensemble in the sidebar and click **'Run Backtest'** to begin!")
    
    st.markdown("---")
    
    st.subheader("📚 Quick Start Guide")
    
    col_guide1, col_guide2 = st.columns(2)
    
    with col_guide1:
        st.markdown("""
        **1. Select Strategies**
        - Choose 1 or more strategies from the sidebar
        - Each strategy provides unique signals
        - More diverse strategies = better ensemble
        
        **2. Configure Parameters**
        - Adjust max positions (portfolio concentration)
        - Fine-tune strategy-specific settings
        - Set realistic transaction costs
        """)
    
    with col_guide2:
        st.markdown("""
        **3. Run & Analyze**
        - Click "Run Backtest" to execute
        - Review performance metrics
        - Check strategy correlation for diversification
        - Export results for further analysis
        
        **4. Iterate & Optimize**
        - Try different strategy combinations
        - Adjust parameters to improve performance
        - Compare results across multiple runs
        """)
    
    st.markdown("---")
    
    st.subheader("📊 Available Strategies")
    
    strategy_info = {
        "Mean Reversion (QP)": {
            "Description": "Buys undervalued assets with low Quality-Price Indicator",
            "Best For": "Range-bound markets, contrarian opportunities",
            "Key Parameter": "MA Lookback (controls mean reversion speed)"
        },
        "Trend Following": {
            "Description": "Follows momentum by comparing price to moving average",
            "Best For": "Trending markets, momentum capture",
            "Key Parameter": "SMA Period (defines trend timeframe)"
        },
        "Random (Benchmark)": {
            "Description": "Generates random signals for performance baseline",
            "Best For": "Benchmarking strategy effectiveness",
            "Key Parameter": "None (random seed for reproducibility)"
        }
    }
    
    for strat_name, info in strategy_info.items():
        with st.expander(f"🔹 {strat_name}", expanded=False):
            st.markdown(f"**Description:** {info['Description']}")
            st.markdown(f"**Best For:** {info['Best For']}")
            st.markdown(f"**Key Parameter:** {info['Key Parameter']}")
    
    st.markdown("---")
    
    # Data preview
    st.subheader("👀 Data Preview")
    
    if market_data is not None and len(market_data) > 0:
        
        # Show sample data
        sample_size = min(100, len(market_data))
        st.dataframe(
            market_data.head(sample_size),
            use_container_width=True,
            height=300
        )
        
        # Basic statistics
        st.caption(f"Showing first {sample_size} rows of {len(market_data):,} total records")
