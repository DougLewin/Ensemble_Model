"""
Run Simulation Page - Ensemble Trading Dashboard
=================================================
Page for configuring and running ensemble backtests.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from portfolio_manager import PortfolioManager, PortfolioConfig
from backtest_engine import BacktestEngine


class RandomStrategy:
    """Random strategy for benchmarking."""
    
    def __init__(self, name: str = "Random", seed: int = 42):
        self.name = name
        self.seed = seed
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        np.random.seed(self.seed)
        df = data.copy()
        df['signal'] = np.random.uniform(-1, 1, len(df))
        df['confidence'] = np.random.uniform(0.3, 0.7, len(df))
        return df[['signal', 'confidence']]
    
    def __repr__(self) -> str:
        return f"RandomStrategy(name='{self.name}')"


def render_simulation_page(MODEL_INFO, load_nasdaq_data):
    """Render the simulation configuration and execution page."""
    
    st.title("🚀 Run Simulation")
    st.markdown("Configure your ensemble and run a backtest on historical data.")
    st.info(f"📁 **Active Data Source:** `{st.session_state.data_source}`")
    
    st.markdown("---")
    
    # ============================================================
    # SIDEBAR - CONTROL PANEL
    # ============================================================
    
    st.sidebar.markdown("## ⚙️ Simulation Config")
    st.sidebar.markdown("---")
    
    # Load data using configured source from session state
    data_source = st.session_state.get('data_source', 'NASDAQ_HISTORY_2.csv')
    
    with st.spinner("Loading market data..."):
        market_data = load_nasdaq_data(data_source)
    
    if market_data is None or len(market_data) == 0:
        st.error("❌ Unable to load market data. Please configure data source in the Data tab.")
        st.stop()
    
    # Apply date filter if enabled
    if st.session_state.get('date_filter_enabled', False):
        filter_start = st.session_state.get('date_filter_start')
        filter_end = st.session_state.get('date_filter_end')
        market_data = market_data.loc[
            (market_data.index.get_level_values('date') >= filter_start) &
            (market_data.index.get_level_values('date') <= filter_end)
        ]
        st.sidebar.info(f"📅 Date filter active: {filter_start.date()} to {filter_end.date()}")
    
    # Apply ticker filter if enabled
    if st.session_state.get('ticker_filter') is not None:
        filter_type = st.session_state.get('ticker_filter_type')
        ticker_list = st.session_state.get('ticker_filter')
        
        if filter_type == "include":
            market_data = market_data.loc[
                market_data.index.get_level_values('ticker').isin(ticker_list)
            ]
            st.sidebar.info(f"🎯 Using {len(ticker_list)} selected tickers")
        elif filter_type == "exclude":
            market_data = market_data.loc[
                ~market_data.index.get_level_values('ticker').isin(ticker_list)
            ]
            st.sidebar.info(f"🎯 Excluding {len(ticker_list)} tickers")
    
    # Display data info
    num_tickers = len(market_data.index.get_level_values('ticker').unique())
    date_range = market_data.index.get_level_values('date').unique()
    start_date = date_range.min()
    end_date = date_range.max()
    
    st.sidebar.success("✅ Data Loaded")
    st.sidebar.metric("Tickers", num_tickers)
    st.sidebar.metric("Records", f"{len(market_data):,}")
    
    st.sidebar.markdown("---")
    
    # ============================================================
    # STRATEGY SELECTION
    # ============================================================
    
    st.sidebar.subheader("🎯 Select Models")
    
    available_strategies = {
        "Mean Reversion": "mean_reversion",
        "Trend Following": "trend",
        "Momentum": "momentum",
        "Random (Benchmark)": "random"
    }
    
    selected_strategies = st.sidebar.multiselect(
        "Choose Strategies",
        options=list(available_strategies.keys()),
        default=["Mean Reversion", "Trend Following"],
        help="Select 1 or more strategies to combine in the ensemble"
    )
    
    if len(selected_strategies) == 0:
        st.warning("⚠️ Please select at least one strategy from the sidebar.")
        st.stop()
    
    st.sidebar.markdown("---")
    
    # ============================================================
    # PARAMETERS
    # ============================================================
    
    st.sidebar.subheader("📐 Portfolio Settings")
    
    top_n_assets = st.sidebar.slider(
        "Max Positions",
        min_value=3,
        max_value=min(20, num_tickers),
        value=5,
        help="Maximum number of assets to hold simultaneously"
    )
    
    st.sidebar.markdown("---")
    
    # Strategy-specific parameters
    st.sidebar.subheader("🔧 Model Parameters")
    
    # Mean Reversion
    if "Mean Reversion" in selected_strategies:
        with st.sidebar.expander("Mean Reversion", expanded=False):
            mr_lookback_ma = st.slider("MA Lookback", 20, 200, 50, key="mr_ma")
            mr_lookback_vol = st.slider("Volatility Lookback", 10, 60, 20, key="mr_vol")
            mr_hist_vol = st.slider("Historical Vol Period", 50, 500, 100, key="mr_hist")
    
    # Trend Following
    if "Trend Following" in selected_strategies:
        with st.sidebar.expander("Trend Following", expanded=False):
            trend_sma_period = st.slider("SMA Period", 20, 200, 100, key="trend_sma")
    
    # Momentum
    if "Momentum" in selected_strategies:
        with st.sidebar.expander("Momentum", expanded=False):
            momentum_lookback = st.slider("Lookback Period", 5, 60, 20, key="mom_lookback")
    
    st.sidebar.markdown("---")
    
    # Backtest parameters
    st.sidebar.subheader("💰 Backtest Settings")
    
    initial_capital = st.sidebar.number_input(
        "Initial Capital ($)",
        value=100000,
        step=10000,
        key="initial_cap"
    )
    
    commission = st.sidebar.number_input(
        "Commission (%)",
        value=0.1,
        step=0.05,
        key="commission"
    ) / 100
    
    slippage = st.sidebar.number_input(
        "Slippage (%)",
        value=0.05,
        step=0.01,
        key="slippage"
    ) / 100
    
    st.sidebar.markdown("---")
    
    # ============================================================
    # RUN BUTTON
    # ============================================================
    
    run_backtest = st.sidebar.button(
        "🚀 Run Backtest",
        type="primary",
        use_container_width=True,
        key="run_btn"
    )
    
    # ============================================================
    # MAIN CONTENT
    # ============================================================
    
    if run_backtest:
        
        with st.spinner("Running ensemble backtest..."):
            
            # Initialize strategies
            strategy_objects = []
            
            for strategy_name in selected_strategies:
                strategy_type = available_strategies[strategy_name]
                
                if strategy_type == "mean_reversion":
                    strategy_class = MODEL_INFO["Mean Reversion"]["class"]
                    strategy_objects.append(strategy_class(
                        name="MeanReversion",
                        lookback_ma=mr_lookback_ma,
                        lookback_vol=mr_lookback_vol,
                        historical_vol_period=mr_hist_vol
                    ))
                
                elif strategy_type == "trend":
                    strategy_class = MODEL_INFO["Trend Following"]["class"]
                    strategy_objects.append(strategy_class(
                        name="TrendFollowing",
                        sma_period=trend_sma_period
                    ))
                
                elif strategy_type == "momentum":
                    strategy_class = MODEL_INFO["Momentum"]["class"]
                    strategy_objects.append(strategy_class(
                        name="Momentum",
                        lookback_period=momentum_lookback
                    ))
                
                elif strategy_type == "random":
                    strategy_objects.append(RandomStrategy(name="Random"))
            
            # Create Portfolio Manager
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
            
            # Generate ensemble signals
            ensemble_signals = portfolio_manager.generate_ensemble_signals(market_data)
            
            # Run backtest
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
        
        # Performance Summary
        st.header("📈 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", metrics['Total Return'])
        with col2:
            st.metric("Sharpe Ratio", metrics['Sharpe Ratio'])
        with col3:
            st.metric("Max Drawdown", metrics['Maximum Drawdown'])
        with col4:
            st.metric("Win Rate", metrics['Win Rate'])
        
        # Detailed metrics
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
        
        # Equity Curve
        st.header("💰 Equity Curve")
        
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
        
        fig_equity.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital"
        )
        
        fig_equity.update_layout(
            title="Portfolio Value Over Time",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_equity, use_container_width=True)
        
        # Drawdown
        with st.expander("📉 Drawdown Analysis", expanded=False):
            returns = equity_curve['portfolio_value'].pct_change()
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown * 100,
                mode='lines',
                fill='tozeroy',
                line=dict(color='#A23B72', width=2)
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
        
        # Strategy Correlation
        st.header("🔗 Strategy Correlation Matrix")
        
        if portfolio_manager.correlation_matrix is not None:
            corr_matrix = portfolio_manager.correlation_matrix.copy()
            corr_matrix.columns = [col.replace('signal_', '') for col in corr_matrix.columns]
            corr_matrix.index = [idx.replace('signal_', '') for idx in corr_matrix.index]
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto='.3f',
                color_continuous_scale='RdBu_r',
                color_continuous_midpoint=0,
                aspect='auto'
            )
            
            fig_corr.update_layout(
                title="Strategy Signal Correlation",
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("---")
        
        # Top Holdings
        st.header("🏆 Top Holdings (Last Rebalance)")
        
        last_date = ensemble_signals.index.get_level_values('date').unique()[-1]
        top_assets = portfolio_manager.get_top_assets(last_date, top_n=top_n_assets)
        
        if len(top_assets) > 0:
            display_df = top_assets.copy()
            display_df['combined_score'] = display_df['combined_score'].round(3)
            display_df['weight'] = (display_df['weight'] * 100).round(2).astype(str) + '%'
            display_df['rank'] = display_df['rank'].astype(int)
            
            st.dataframe(display_df, use_container_width=True, height=300)
        
        st.markdown("---")
        
        # Export
        st.header("💾 Export Results")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            equity_csv = equity_curve.to_csv()
            st.download_button(
                label="📥 Download Equity Curve",
                data=equity_csv,
                file_name=f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_dl2:
            signals_csv = ensemble_signals.to_csv()
            st.download_button(
                label="📥 Download Signals",
                data=signals_csv,
                file_name=f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        # Welcome screen
        st.info("👈 Configure your ensemble in the sidebar and click **'Run Backtest'** to begin!")
        
        st.markdown("---")
        
        st.subheader("🎯 Selected Strategies")
        
        for strategy_name in selected_strategies:
            with st.expander(f"📈 {strategy_name}", expanded=False):
                if strategy_name in MODEL_INFO:
                    st.markdown(MODEL_INFO[strategy_name]['short_desc'])
                elif strategy_name == "Random (Benchmark)":
                    st.markdown("Generates random signals for performance baseline comparison.")
