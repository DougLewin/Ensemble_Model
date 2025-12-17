"""
Main Execution Script - Ensemble Trading System
================================================
Demo: Combining Mean Reversion + Trend Following strategies

Author: Lead Quantitative Software Architect
Date: December 16, 2025
"""

import pandas as pd
import numpy as np
import warnings
import os
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Import our modular components
from strategy_base import Strategy
from mean_reversion_strategy import MeanReversionQP
from trend_strategy import SimpleTrend
from portfolio_manager import PortfolioManager, PortfolioConfig
from backtest_engine import BacktestEngine
from s3_data_loader import S3DataLoader
from config import AWSConfig


def load_live_market_data(
    filepath: str = "NASDAQ_HISTORY_2.csv",
    use_s3: bool = None
) -> pd.DataFrame:
    """
    Load live market data from S3 or local CSV file.
    
    Args:
        filepath: Path to the CSV file (used for local files or as fallback)
        use_s3: Whether to use S3 (if None, uses config setting)
    
    Returns:
        DataFrame with MultiIndex (date, ticker) and OHLCV columns
    """
    print(f"\n{'='*60}")
    print("DATA LOADING: Reading Live Market Data")
    print(f"{'='*60}")
    
    # Load AWS configuration
    aws_config = AWSConfig()
    
    # Determine data source
    should_use_s3 = use_s3 if use_s3 is not None else aws_config.use_s3
    
    try:
        if should_use_s3:
            # Load from S3
            print(f"📡 Loading from S3: {aws_config.bucket_name}/{aws_config.s3_key}")
            
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
            
            return df
            
        else:
            # Load from local file
            print(f"📁 Loading from local file: {filepath}")
            
            # Load CSV
            df = pd.read_csv(filepath)
            
            # Standardize column names (lowercase)
            df.columns = df.columns.str.lower()
            
            # Rename columns to match expected format
            column_mapping = {
                'code': 'ticker',
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
            df = df.set_index(['date', 'ticker']).sort_index()
            
            # Remove any duplicates
            df = df[~df.index.duplicated(keep='first')]
            
            print(f"\n📊 Data Summary:")
            print(f"   Date Range: {df.index.get_level_values('date').min()} to {df.index.get_level_values('date').max()}")
            print(f"   Unique Tickers: {df.index.get_level_values('ticker').nunique()}")
            print(f"   Total Records: {len(df):,}")
            
            return df
    
    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        
        # Try fallback if S3 failed
        if should_use_s3 and aws_config.local_fallback:
            print(f"\n⚠️ S3 load failed. Attempting local fallback: {aws_config.local_fallback}")
            try:
                return load_live_market_data(aws_config.local_fallback, use_s3=False)
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {str(fallback_error)}")
                raise
        else:
            raise
        required_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
        df = df[required_cols]
        
        # Set MultiIndex
        df = df.set_index(['date', 'ticker'])
        
        # Sort index
        df = df.sort_index()
        
        print(f"✓ Loaded {len(df)} data points")
        print(f"  Date Range: {df.index.get_level_values('date').min().date()} to {df.index.get_level_values('date').max().date()}")
        print(f"  Tickers: {', '.join(df.index.get_level_values('ticker').unique())}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        raise


def main():
    """Main execution function."""
    
    print("\n" + "="*60)
    print("ENSEMBLE TRADING SYSTEM - MODULAR ARCHITECTURE")
    print("="*60)
    print("Philosophy: The Bitter Lesson + Learning to Rank")
    print("="*60)
    
    # ============================================================
    # 1. Load Live Market Data
    # ============================================================
    market_data = load_live_market_data(filepath="NASDAQ_HISTORY_2.csv")
    
    # ============================================================
    # STEP 2: Initialize Strategies
    # ============================================================
    print(f"\n{'='*60}")
    print("STRATEGY INITIALIZATION")
    print(f"{'='*60}")
    
    # Strategy A: Mean Reversion (Murphy's Law)
    mean_reversion = MeanReversionQP(
        name="MeanReversion",
        lookback_ma=50,
        lookback_vol=20,
        historical_vol_period=100
    )
    print(f"✓ Initialized: {mean_reversion}")
    
    # Strategy B: Simple Trend Following
    trend_following = SimpleTrend(
        name="TrendFollowing",
        sma_period=100
    )
    print(f"✓ Initialized: {trend_following}")
    
    # NOTE: To add Strategy C, simply create it here and add to the list!
    # Example:
    # momentum = MomentumStrategy(name="Momentum", lookback=20)
    
    # ============================================================
    # STEP 3: Create Ensemble (Portfolio Manager)
    # ============================================================
    print(f"\n{'='*60}")
    print("PORTFOLIO MANAGER SETUP")
    print(f"{'='*60}")
    
    config = PortfolioConfig(
        top_n_assets=5,
        rebalance_frequency='daily',
        equal_weight=True,
        long_only=True
    )
    
    portfolio_manager = PortfolioManager(
        strategies=[mean_reversion, trend_following],
        config=config
    )
    print(f"✓ Created: {portfolio_manager}")
    print(f"  Configuration: Top {config.top_n_assets} assets, Equal weight")
    
    # ============================================================
    # STEP 4: Generate Ensemble Signals
    # ============================================================
    ensemble_signals = portfolio_manager.generate_ensemble_signals(market_data)
    
    # ============================================================
    # STEP 5: Run Backtest
    # ============================================================
    backtest = BacktestEngine(
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.0005
    )
    
    equity_curve = backtest.run(market_data, ensemble_signals)
    
    # ============================================================
    # STEP 6: Performance Reporting
    # ============================================================
    backtest.print_performance_report()
    
    # ============================================================
    # STEP 7: Visualizations
    # ============================================================
    print(f"\n{'='*60}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*60}")
    
    backtest.plot_results(save_path='ensemble_backtest_results.png')
    
    # ============================================================
    # STEP 8: Strategy Insights
    # ============================================================
    print(f"\n{'='*60}")
    print("ENSEMBLE INSIGHTS")
    print(f"{'='*60}")
    
    summary = portfolio_manager.summary()
    print(f"\nNumber of Strategies: {summary['num_strategies']}")
    print(f"Strategy Names: {', '.join(summary['strategy_names'])}")
    print(f"Avg Combined Score: {summary['avg_combined_score']:.4f}")
    print(f"Std Combined Score: {summary['std_combined_score']:.4f}")
    
    # Show example of top assets for last date
    last_date = ensemble_signals.index.get_level_values('date').unique()[-1]
    print(f"\n{'─'*60}")
    print(f"TOP ASSETS ON LAST DAY ({last_date.date()})")
    print(f"{'─'*60}")
    top_assets = portfolio_manager.get_top_assets(last_date)
    print(top_assets)
    
    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print(f"\n{'='*60}")
    print("✓ ENSEMBLE SYSTEM EXECUTION COMPLETE")
    print(f"{'='*60}")
    print("\n📊 Key Takeaways:")
    print("  1. Modular design allows easy addition of new strategies")
    print("  2. Strategy correlation matrix shows diversification")
    print("  3. Combined signals leverage complementary insights")
    print("  4. Performance metrics validate ensemble approach")
    print("\n🚀 Next Steps:")
    print("  - Add Strategy C by creating a new class")
    print("  - Experiment with different combination methods")
    print("  - Optimize top_n_assets and rebalancing frequency")
    print("  - Test on real market data")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
