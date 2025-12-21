"""
Configuration File
==================
Centralized configuration for the Ensemble Trading System.
Modify these settings to customize behavior without changing code.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_config_value(key: str, default: str = None, streamlit_section: str = None) -> Optional[str]:
    """
    Get configuration value from Streamlit secrets or environment variables.
    Prioritizes Streamlit secrets when available (for cloud deployment).
    
    Args:
        key: Environment variable key
        default: Default value if not found
        streamlit_section: Section name in Streamlit secrets (e.g., 'aws', 'data')
    
    Returns:
        Configuration value or default
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if streamlit_section and key in st.secrets.get(streamlit_section, {}):
            return st.secrets[streamlit_section][key]
    except (ImportError, FileNotFoundError, KeyError):
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)


@dataclass
class AWSConfig:
    """AWS S3 configuration for data loading."""
    
    def __init__(self):
        """Initialize AWS config from Streamlit secrets or environment variables."""
        use_s3_str = get_config_value('USE_S3', 'true', 'data')
        self.use_s3 = use_s3_str.lower() in ('true', '1', 'yes')
        
        self.bucket_name = get_config_value('AWS_S3_BUCKET_NAME', 'my-nasdaq-data-bucket', 'aws')
        self.s3_key = get_config_value('AWS_S3_KEY', 'NASDAQ.csv', 'aws')
        self.aws_access_key_id = get_config_value('AWS_ACCESS_KEY_ID', None, 'aws')
        self.aws_secret_access_key = get_config_value('AWS_SECRET_ACCESS_KEY', None, 'aws')
        self.region_name = get_config_value('AWS_REGION', 'us-east-1', 'aws')
        self.use_cache = True  # Cache downloaded files locally
        self.local_fallback = get_config_value('LOCAL_FALLBACK', 'NASDAQ.csv', 'data')


@dataclass
class DataConfig:
    """Market data configuration."""
    num_tickers: int = 15
    num_days: int = 500
    random_seed: int = 42
    start_date: str = "2023-01-01"


@dataclass
class StrategyConfig:
    """Individual strategy parameters."""
    
    # Mean Reversion Strategy
    mean_reversion_enabled: bool = True
    mr_lookback_ma: int = 50
    mr_lookback_vol: int = 20
    mr_historical_vol_period: int = 100
    
    # Trend Following Strategy
    trend_enabled: bool = True
    trend_sma_period: int = 100
    
    # Momentum Strategy (optional)
    momentum_enabled: bool = False
    momentum_lookback: int = 20


@dataclass
class EnsembleConfig:
    """Portfolio manager configuration."""
    top_n_assets: int = 5
    rebalance_frequency: str = 'daily'  # 'daily', 'weekly', 'monthly'
    equal_weight: bool = True
    long_only: bool = True


@dataclass
class BacktestConfig:
    """Backtesting parameters."""
    initial_capital: float = 100000.0
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005   # 0.05%
    
    # Output settings
    save_results: bool = True
    results_filename: str = "ensemble_backtest_results.png"
    show_plots: bool = False


@dataclass
class SystemConfig:
    """Master configuration."""
    aws: AWSConfig = field(default_factory=AWSConfig)
    data: DataConfig = field(default_factory=DataConfig)
    strategies: StrategyConfig = field(default_factory=StrategyConfig)
    ensemble: EnsembleConfig = field(default_factory=EnsembleConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    
    # Reporting
    verbose: bool = True
    print_correlation: bool = True
    print_top_assets: bool = True


# ============================================================
# PRESET CONFIGURATIONS
# ============================================================

def get_conservative_config() -> SystemConfig:
    """Conservative portfolio: fewer assets, longer lookback."""
    config = SystemConfig()
    config.ensemble.top_n_assets = 3
    config.strategies.mr_lookback_ma = 100
    config.strategies.trend_sma_period = 200
    return config


def get_aggressive_config() -> SystemConfig:
    """Aggressive portfolio: more assets, shorter lookback."""
    config = SystemConfig()
    config.ensemble.top_n_assets = 10
    config.strategies.mr_lookback_ma = 20
    config.strategies.trend_sma_period = 50
    return config


def get_diversified_config() -> SystemConfig:
    """Diversified: Enable all strategies."""
    config = SystemConfig()
    config.strategies.mean_reversion_enabled = True
    config.strategies.trend_enabled = True
    config.strategies.momentum_enabled = True
    config.ensemble.top_n_assets = 7
    return config


def get_test_config() -> SystemConfig:
    """Quick test configuration: small dataset, fast execution."""
    config = SystemConfig()
    config.data.num_tickers = 5
    config.data.num_days = 100
    config.ensemble.top_n_assets = 3
    config.backtest.save_results = False
    return config


# ============================================================
# USAGE EXAMPLES
# ============================================================
"""
In main.py:

from config import SystemConfig, get_conservative_config

# Option 1: Default configuration
config = SystemConfig()

# Option 2: Preset configuration
config = get_conservative_config()

# Option 3: Custom configuration
config = SystemConfig()
config.ensemble.top_n_assets = 8
config.strategies.mr_lookback_ma = 60
config.backtest.initial_capital = 250000.0

# Then use throughout the system:
market_data = generate_mock_market_data(
    num_tickers=config.data.num_tickers,
    num_days=config.data.num_days,
    seed=config.data.random_seed
)

portfolio_manager = PortfolioManager(
    strategies=strategies,
    config=config.ensemble
)

backtest = BacktestEngine(
    initial_capital=config.backtest.initial_capital,
    commission=config.backtest.commission,
    slippage=config.backtest.slippage
)
"""

# Default export
DEFAULT_CONFIG = SystemConfig()
