"""
Streamlit Trading Dashboard - Multi-Page Navigation
====================================================
Interactive dashboard for ensemble trading strategies with organized navigation.

Author: Full-Stack Quantitative Developer  
Date: December 18, 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
import os
import glob
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Import our trading engine components
from strategy_base import Strategy
from mean_reversion_strategy import MeanReversionQP
from trend_strategy import SimpleTrend
from momentum_strategy import MomentumStrategy
from s3_data_loader import S3DataLoader
from config import AWSConfig

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
# SESSION STATE INITIALIZATION
# ============================================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

if 'current_model' not in st.session_state:
    st.session_state.current_model = None

if 'data_source' not in st.session_state:
    st.session_state.data_source = 'NASDAQ.csv'

if 'date_filter_enabled' not in st.session_state:
    st.session_state.date_filter_enabled = False

if 'ticker_filter' not in st.session_state:
    st.session_state.ticker_filter = None

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_available_csv_files():
    """Get list of CSV files in current directory."""
    csv_files = []
    # Match .csv files and files with .csv. pattern
    for pattern in ['*.csv', '*.csv.*']:
        csv_files.extend(glob.glob(pattern))
    # Remove duplicates and sort
    csv_files = sorted(list(set(csv_files)))
    return csv_files if csv_files else ['NASDAQ.csv']  # Default if none found

# ============================================================
# DATA LOADING (WITH CACHING)
# ============================================================

@st.cache_data
def load_nasdaq_data(
    filepath: str = "NASDAQ.csv",
    use_s3: bool = None,
    force_local: bool = False
) -> pd.DataFrame:
    """
    Load NASDAQ data with caching for performance.
    Supports both S3 and local file sources.
    
    Args:
        filepath: Path to the CSV file (used for local files or as S3 key)
        use_s3: Whether to use S3 (if None, uses config setting)
        force_local: Force loading from local file even if S3 is configured
        
    Returns:
        DataFrame with MultiIndex (date, ticker) and OHLCV columns
    """
    # Load AWS configuration
    aws_config = AWSConfig()
    
    # Determine data source
    should_use_s3 = not force_local and (use_s3 if use_s3 is not None else aws_config.use_s3)
    
    try:
        if should_use_s3:
            # Load from S3
            st.info(f"📡 Loading data from S3: {aws_config.bucket_name}/{aws_config.s3_key}")
            
            loader = S3DataLoader(
                bucket_name=aws_config.bucket_name,
                aws_access_key_id=aws_config.aws_access_key_id,
                aws_secret_access_key=aws_config.aws_secret_access_key,
                region_name=aws_config.region_name
            )
            
            df = loader.load_nasdaq_data(
                s3_key=aws_config.s3_key,
                use_cache=aws_config.use_cache
            )
            
            st.success(f"✅ Data loaded from S3: {len(df):,} rows")
            return df
            
        else:
            # Load from local file
            st.info(f"📁 Loading data from local file: {filepath}")
            
            # Load CSV
            df = pd.read_csv(filepath)
            
            # Standardize column names (lowercase)
            df.columns = df.columns.str.lower()
            
            # Rename columns to match expected format
            # Handle various column name formats: 'code', 'aokcode', etc.
            column_mapping = {
                'code': 'ticker',
                'aokcode': 'ticker',  # Handle 'aokCODE' after lowercase
                'ticker': 'ticker',
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Convert date to datetime (YYYY-MM-DD format)
            df['date'] = pd.to_datetime(df['date'])
            
            # Keep only required columns
            required_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
            df = df[required_cols]
            
            # Set MultiIndex
            df = df.set_index(['date', 'ticker'])
            
            # Sort index
            df = df.sort_index()
            
            st.success(f"✅ Data loaded from local file: {len(df):,} rows")
            return df
        
    except FileNotFoundError:
        st.error(f"❌ File not found: {filepath}")
        st.info(f"📁 Please ensure {filepath} is in the current directory.")
        return None
    
    except Exception as e:
        st.error(f"❌ Error loading data from S3: {str(e)}")
        st.info("💡 Check your AWS credentials in .env file")
        st.info("💡 Run test_s3_connection.py to debug S3 connection")
        return None

# ============================================================
# MODEL METADATA
# ============================================================

MODEL_INFO = {
    "Mean Reversion": {
        "class": MeanReversionQP,
        "short_desc": "Buys undervalued assets when price deviates below historical mean, assuming reversion to equilibrium.",
        "description": """
        **Mean Reversion (Quality-Price Indicator)**
        
        This strategy identifies undervalued assets by calculating a Quality-Price Indicator (QPI) 
        that measures how far current prices deviate from their historical average relative to volatility.
        
        **Core Logic:**
        - Calculates moving average and volatility over lookback periods
        - Computes QPI = (Price - MA) / Historical Volatility
        - Generates buy signals when QPI is low (price below mean)
        - Assumes prices will revert to the mean over time
        
        **Best Use Cases:**
        - Range-bound markets with clear support/resistance
        - Assets with stable fundamental values
        - Markets with cyclical behavior
        """,
        "assumptions": [
            "Asset prices oscillate around a stable mean",
            "Volatility is relatively constant over time",
            "No structural breaks or regime changes",
            "Sufficient liquidity for mean reversion to occur"
        ],
        "hyperparameters": {
            "lookback_ma": {
                "name": "MA Lookback Period",
                "description": "Number of periods to calculate moving average",
                "default": 50,
                "range": (20, 200),
                "impact": "Shorter = more responsive to price changes, Longer = smoother trend"
            },
            "lookback_vol": {
                "name": "Volatility Lookback Period",
                "description": "Number of periods to calculate volatility",
                "default": 20,
                "range": (10, 60),
                "impact": "Affects sensitivity to price deviations"
            },
            "historical_vol_period": {
                "name": "Historical Volatility Period",
                "description": "Extended period for calculating baseline volatility",
                "default": 100,
                "range": (50, 500),
                "impact": "Longer period = more stable volatility estimates"
            }
        }
    },
    
    "Trend Following": {
        "class": SimpleTrend,
        "short_desc": "Follows momentum by comparing price to moving average, buying when price is above trend.",
        "description": """
        **Simple Trend Following Strategy**
        
        This strategy captures momentum by identifying assets trading above their moving average,
        indicating an established uptrend.
        
        **Core Logic:**
        - Calculates Simple Moving Average (SMA) over specified period
        - Compares current price to SMA
        - Generates buy signals when price > SMA (uptrend)
        - Signal strength based on distance from SMA
        
        **Best Use Cases:**
        - Trending markets with clear directional moves
        - Breakout scenarios
        - Momentum-driven assets (tech stocks, growth sectors)
        """,
        "assumptions": [
            "Trends persist over time (momentum effect)",
            "Price above MA indicates continued upward movement",
            "Market exhibits trending behavior vs. mean reversion",
            "Transaction costs don't erode trend profits"
        ],
        "hyperparameters": {
            "sma_period": {
                "name": "SMA Period",
                "description": "Number of periods for moving average calculation",
                "default": 100,
                "range": (20, 200),
                "impact": "Shorter = captures short-term trends, Longer = focuses on major trends"
            }
        }
    },
    
    "Momentum": {
        "class": MomentumStrategy,
        "short_desc": "Ranks assets by recent price performance, buying strongest performers expecting continuation.",
        "description": """
        **Momentum Strategy (Rate of Change)**
        
        This strategy selects assets with the strongest recent price performance,
        based on the principle that past winners tend to continue winning.
        
        **Core Logic:**
        - Calculates rate of change over lookback period
        - Ranks assets by momentum score
        - Generates signals favoring top performers
        - Continuous rebalancing to maintain momentum exposure
        
        **Best Use Cases:**
        - Bull markets with clear sector leaders
        - Growth-oriented portfolios
        - High-volatility environments with persistent trends
        """,
        "assumptions": [
            "Past performance predicts future performance (short-term)",
            "Winner momentum persists for the holding period",
            "Market rewards risk-taking in uptrends",
            "Sufficient liquidity to enter/exit positions"
        ],
        "hyperparameters": {
            "lookback_period": {
                "name": "Momentum Lookback Period",
                "description": "Number of periods to calculate momentum",
                "default": 20,
                "range": (5, 60),
                "impact": "Shorter = more reactive to recent changes, Longer = more stable signals"
            }
        }
    }
}

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("📊 Navigation")

# Data Source Selector
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Data Source")

available_csv_files = get_available_csv_files()
current_source = st.session_state.data_source

# Ensure current source is in the list
if current_source not in available_csv_files:
    available_csv_files.append(current_source)
    available_csv_files = sorted(available_csv_files)

selected_csv = st.sidebar.selectbox(
    "Select CSV file:",
    options=available_csv_files,
    index=available_csv_files.index(current_source) if current_source in available_csv_files else 0,
    help="Choose the data file to use for analysis",
    key="csv_selector"
)

# Update session state if changed
if selected_csv != st.session_state.data_source:
    st.session_state.data_source = selected_csv
    # Clear cache to reload data
    load_nasdaq_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# Main navigation
page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "💾 Data", "🧠 Models", "🚀 Run Simulation", "📊 Data Explorer"],
    key="main_nav"
)

# Update session state
if page == "🏠 Home":
    st.session_state.current_page = "Home"
elif page == "💾 Data":
    st.session_state.current_page = "Data"
elif page == "🧠 Models":
    st.session_state.current_page = "Models"
elif page == "🚀 Run Simulation":
    st.session_state.current_page = "Run Simulation"
elif page == "📊 Data Explorer":
    st.session_state.current_page = "Data Explorer"

# Sub-navigation for Models page
if st.session_state.current_page == "Models":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Select Model:")
    
    for model_name in MODEL_INFO.keys():
        if st.sidebar.button(f"📈 {model_name}", key=f"nav_{model_name}"):
            st.session_state.current_model = model_name

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ by Quantitative Research Team")

# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.current_page == "Home":
    # HOME PAGE
    st.title("📊 Ensemble Trading Research Lab")
    st.markdown("""
    Welcome to the Ensemble Trading Research Lab - an interactive platform for testing
    and analyzing quantitative trading strategies.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 Models")
        st.markdown("""
        Explore our suite of trading strategies:
        - **Mean Reversion**: Capitalizes on price oscillations
        - **Trend Following**: Rides momentum waves
        - **Momentum**: Selects top performers
        
        Each model includes detailed documentation, assumptions, and tunable hyperparameters.
        """)
        
    with col2:
        st.subheader("🚀 Run Simulation")
        st.markdown("""
        Test your ensemble strategies:
        - Select multiple models to combine
        - Configure hyperparameters
        - Set portfolio constraints
        - Analyze performance metrics
        - Export results for further analysis
        """)
    
    st.markdown("---")
    
    st.subheader("📈 Quick Stats")
    st.info(f"📁 **Active Data Source:** `{st.session_state.data_source}`")
    
    with st.spinner("Loading data statistics..."):
        market_data = load_nasdaq_data(st.session_state.data_source)
        
        if market_data is not None:
            num_tickers = len(market_data.index.get_level_values('ticker').unique())
            date_range = market_data.index.get_level_values('date').unique()
            start_date = date_range.min()
            end_date = date_range.max()
            
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("Total Records", f"{len(market_data):,}")
            with col_b:
                st.metric("Unique Tickers", num_tickers)
            with col_c:
                st.metric("Start Date", str(start_date.date()))
            with col_d:
                st.metric("End Date", str(end_date.date()))

elif st.session_state.current_page == "Data":
    # DATA CONFIGURATION PAGE
    st.title("💾 Data Configuration")
    st.markdown("Configure your data source and filtering options for simulations.")
    st.info(f"📁 **Current Data Source:** `{st.session_state.data_source}`")
    
    st.markdown("---")
    
    # Data Source Selection
    st.subheader("📁 Data Source")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        data_file = st.text_input(
            "CSV Filename",
            value=st.session_state.data_source,
            help="Enter the filename of your CSV data file",
            key="data_file_input"
        )
    
    with col2:
        if st.button("📥 Load Data", type="primary", use_container_width=True):
            st.session_state.data_source = data_file
            # Clear cache to reload data
            load_nasdaq_data.clear()
            st.success(f"✅ Data source updated to: {data_file}")
            st.rerun()
    
    st.markdown("---")
    
    # Data Preview
    st.subheader("📊 Current Data Source")
    
    with st.spinner("Loading data preview..."):
        market_data = load_nasdaq_data(st.session_state.data_source)
    
    if market_data is not None:
        st.success(f"✅ Successfully loaded: {st.session_state.data_source}")
        
        # Display metrics
        num_tickers = len(market_data.index.get_level_values('ticker').unique())
        date_range = market_data.index.get_level_values('date').unique()
        start_date = date_range.min()
        end_date = date_range.max()
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.metric("Total Records", f"{len(market_data):,}")
        with col_b:
            st.metric("Unique Tickers", num_tickers)
        with col_c:
            st.metric("Start Date", str(start_date.date()))
        with col_d:
            st.metric("End Date", str(end_date.date()))
        
        st.markdown("---")
        
        # Date Range Filtering
        st.subheader("📅 Date Range Filter")
        
        enable_filter = st.checkbox(
            "Enable date range filtering for simulations",
            value=st.session_state.date_filter_enabled,
            help="When enabled, only data within the selected range will be used"
        )
        
        if enable_filter:
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                filter_start = st.date_input(
                    "Start Date",
                    value=start_date,
                    min_value=start_date,
                    max_value=end_date
                )
            
            with col_date2:
                filter_end = st.date_input(
                    "End Date",
                    value=end_date,
                    min_value=start_date,
                    max_value=end_date
                )
            
            st.session_state.date_filter_enabled = True
            st.session_state.date_filter_start = pd.Timestamp(filter_start)
            st.session_state.date_filter_end = pd.Timestamp(filter_end)
            
            filtered_data = market_data.loc[
                (market_data.index.get_level_values('date') >= pd.Timestamp(filter_start)) &
                (market_data.index.get_level_values('date') <= pd.Timestamp(filter_end))
            ]
            
            st.info(f"📊 Filtered: {len(filtered_data):,} records ({len(filtered_data) / len(market_data) * 100:.1f}% of total)")
        else:
            st.session_state.date_filter_enabled = False
        
        st.markdown("---")
        
        # Ticker Selection
        st.subheader("🎯 Ticker Filter")
        
        all_tickers = sorted(market_data.index.get_level_values('ticker').unique())
        
        filter_type = st.radio(
            "Filter type:",
            ["Use All Tickers", "Select Specific Tickers", "Exclude Tickers"],
            horizontal=True
        )
        
        if filter_type == "Select Specific Tickers":
            selected_tickers = st.multiselect(
                "Select tickers to include:",
                options=all_tickers,
                default=all_tickers[:10] if len(all_tickers) > 10 else all_tickers,
                help="Only selected tickers will be used"
            )
            st.session_state.ticker_filter = selected_tickers
            st.session_state.ticker_filter_type = "include"
            st.info(f"📊 Selected {len(selected_tickers)} tickers")
        
        elif filter_type == "Exclude Tickers":
            excluded_tickers = st.multiselect(
                "Select tickers to exclude:",
                options=all_tickers,
                help="These tickers will be excluded"
            )
            st.session_state.ticker_filter = excluded_tickers
            st.session_state.ticker_filter_type = "exclude"
            if excluded_tickers:
                st.info(f"📊 Excluding {len(excluded_tickers)} tickers ({len(all_tickers) - len(excluded_tickers)} remaining)")
        else:
            st.session_state.ticker_filter = None
            st.session_state.ticker_filter_type = None
        
        st.markdown("---")
        
        # Sample Data Preview
        st.subheader("👀 Data Sample")
        preview_rows = st.slider("Number of rows to preview", 5, 100, 20)
        st.dataframe(market_data.head(preview_rows), use_container_width=True)
    
    else:
        st.error(f"❌ Failed to load data from: {st.session_state.data_source}")
        st.info("💡 Please check that the file exists and is in the correct format.")

elif st.session_state.current_page == "Models":
    # MODELS PAGE
    
    if st.session_state.current_model is None:
        # Models Overview
        st.title("🧠 Trading Models")
        st.markdown("Select a model from the sidebar to view detailed information.")
        
        st.markdown("---")
        
        for model_name, info in MODEL_INFO.items():
            with st.expander(f"📈 **{model_name}**", expanded=False):
                st.markdown(f"**Description:** {info['short_desc']}")
                st.markdown(f"**Best For:** {info['description'].split('**Best Use Cases:**')[1].split('**')[0].strip()}")
                
                if st.button(f"View Details →", key=f"details_{model_name}"):
                    st.session_state.current_model = model_name
                    st.rerun()
    
    else:
        # Specific Model Details
        model_name = st.session_state.current_model
        model_info = MODEL_INFO[model_name]
        
        if st.button("← Back to Models Overview"):
            st.session_state.current_model = None
            st.rerun()
        
        st.title(f"📈 {model_name}")
        
        st.markdown("---")
        
        # Description
        st.subheader("📝 Description")
        st.markdown(model_info['description'])
        
        st.markdown("---")
        
        # Assumptions
        st.subheader("⚠️ Key Assumptions")
        for assumption in model_info['assumptions']:
            st.markdown(f"- {assumption}")
        
        st.markdown("---")
        
        # Hyperparameters
        st.subheader("⚙️ Hyperparameters")
        
        for param_key, param_info in model_info['hyperparameters'].items():
            with st.expander(f"**{param_info['name']}**", expanded=False):
                st.markdown(f"**Description:** {param_info['description']}")
                st.markdown(f"**Default Value:** {param_info['default']}")
                st.markdown(f"**Typical Range:** {param_info['range'][0]} - {param_info['range'][1]}")
                st.markdown(f"**Impact:** {param_info['impact']}")

elif st.session_state.current_page == "Run Simulation":
    # Import simulation page components
    from run_simulation_page import render_simulation_page
    render_simulation_page(MODEL_INFO, load_nasdaq_data)

elif st.session_state.current_page == "Data Explorer":
    # DATA EXPLORER PAGE
    st.title("📊 Data Explorer")
    st.info(f"📁 **Active Data Source:** `{st.session_state.data_source}`")
    
    with st.spinner("Loading market data..."):
        market_data = load_nasdaq_data(st.session_state.data_source)
    
    if market_data is not None:
        st.success("✅ Data loaded successfully")
        
        # Data info
        num_tickers = len(market_data.index.get_level_values('ticker').unique())
        date_range = market_data.index.get_level_values('date').unique()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", f"{len(market_data):,}")
        with col2:
            st.metric("Unique Tickers", num_tickers)
        with col3:
            st.metric("Date Range", f"{str(date_range.min().date())} to {str(date_range.max().date())}")
        
        st.markdown("---")
        
        # Data preview
        st.subheader("📋 Data Preview")
        sample_size = st.slider("Number of rows to display", 10, 1000, 100)
        st.dataframe(market_data.head(sample_size), width='stretch', height=400)
        
        # Export
        st.markdown("---")
        st.subheader("💾 Export Data")
        csv = market_data.head(10000).to_csv()
        st.download_button(
            label="📥 Download Sample (10,000 rows)",
            data=csv,
            file_name="market_data_sample.csv",
            mime="text/csv"
        )
