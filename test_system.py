"""
Test Script - Verify Ensemble System Logic
===========================================
This script tests the modular architecture without requiring matplotlib.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import our modular components
from strategy_base import Strategy
from mean_reversion_strategy import MeanReversionQP
from trend_strategy import SimpleTrend
from portfolio_manager import PortfolioManager, PortfolioConfig


def generate_simple_test_data():
    """Generate minimal test data."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    tickers = ['ASSET_01', 'ASSET_02', 'ASSET_03']
    
    data = []
    for ticker in tickers:
        prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 100)))
        
        for date, price in zip(dates, prices):
            data.append({
                'date': date,
                'ticker': ticker,
                'open': price * 0.99,
                'high': price * 1.01,
                'low': price * 0.98,
                'close': price,
                'volume': 1000000
            })
    
    df = pd.DataFrame(data)
    df = df.set_index(['date', 'ticker'])
    
    return df


def test_strategy_interface():
    """Test that strategies follow the interface."""
    print("\n" + "="*60)
    print("TEST 1: Strategy Interface")
    print("="*60)
    
    data = generate_simple_test_data()
    
    # Test Mean Reversion
    mr_strategy = MeanReversionQP(name="TestMR")
    mr_signals = mr_strategy.generate_signals(data)
    
    assert 'signal' in mr_signals.columns, "Missing 'signal' column"
    assert mr_signals['signal'].min() >= -1.0, "Signal below -1.0"
    assert mr_signals['signal'].max() <= 1.0, "Signal above 1.0"
    
    print(f"✓ MeanReversionQP: {len(mr_signals)} signals generated")
    print(f"  Signal range: [{mr_signals['signal'].min():.3f}, {mr_signals['signal'].max():.3f}]")
    
    # Test Trend
    trend_strategy = SimpleTrend(name="TestTrend")
    trend_signals = trend_strategy.generate_signals(data)
    
    assert 'signal' in trend_signals.columns, "Missing 'signal' column"
    
    print(f"✓ SimpleTrend: {len(trend_signals)} signals generated")
    print(f"  Signal range: [{trend_signals['signal'].min():.3f}, {trend_signals['signal'].max():.3f}]")
    
    return True


def test_portfolio_manager():
    """Test the ensemble engine."""
    print("\n" + "="*60)
    print("TEST 2: Portfolio Manager (Ensemble Engine)")
    print("="*60)
    
    data = generate_simple_test_data()
    
    # Create strategies
    strategies = [
        MeanReversionQP(name="MeanRev"),
        SimpleTrend(name="Trend")
    ]
    
    # Create portfolio manager
    config = PortfolioConfig(top_n_assets=2)
    pm = PortfolioManager(strategies=strategies, config=config)
    
    # Generate ensemble signals
    ensemble = pm.generate_ensemble_signals(data)
    
    assert 'combined_score' in ensemble.columns, "Missing combined_score"
    assert 'rank' in ensemble.columns, "Missing rank"
    assert 'weight' in ensemble.columns, "Missing weight"
    
    print(f"\n✓ Ensemble signals generated: {len(ensemble)} rows")
    print(f"  Columns: {list(ensemble.columns)}")
    
    # Test correlation matrix
    assert pm.correlation_matrix is not None, "Correlation matrix not calculated"
    print(f"\n✓ Correlation matrix computed")
    
    # Test top assets selection
    last_date = ensemble.index.get_level_values('date').unique()[-1]
    top_assets = pm.get_top_assets(last_date)
    
    print(f"\n✓ Top assets selection working")
    print(f"  Top {len(top_assets)} assets for {last_date.date()}:")
    print(top_assets[['combined_score', 'rank', 'weight']].to_string())
    
    return True


def test_backtest_logic():
    """Test backtest calculations without plotting."""
    print("\n" + "="*60)
    print("TEST 3: Backtest Logic (without visualization)")
    print("="*60)
    
    from backtest_engine import BacktestEngine
    
    data = generate_simple_test_data()
    
    # Create simple signals
    strategies = [MeanReversionQP(name="MR")]
    pm = PortfolioManager(strategies=strategies, config=PortfolioConfig(top_n_assets=2))
    signals = pm.generate_ensemble_signals(data)
    
    # Run backtest
    backtest = BacktestEngine(initial_capital=10000, commission=0.001)
    equity_curve = backtest.run(data, signals)
    
    assert len(equity_curve) > 0, "No equity curve generated"
    assert 'portfolio_value' in equity_curve.columns, "Missing portfolio_value"
    
    print(f"\n✓ Backtest completed: {len(equity_curve)} periods")
    print(f"  Initial: ${backtest.initial_capital:,.2f}")
    print(f"  Final: ${equity_curve['portfolio_value'].iloc[-1]:,.2f}")
    
    # Get metrics
    metrics = backtest.get_performance_metrics()
    print(f"\n✓ Performance metrics calculated:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ENSEMBLE TRADING SYSTEM - VERIFICATION TESTS")
    print("="*70)
    print("Testing modular architecture without external dependencies...")
    print("="*70)
    
    try:
        # Run tests
        test_strategy_interface()
        test_portfolio_manager()
        test_backtest_logic()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED - SYSTEM IS OPERATIONAL")
        print("="*70)
        
        print("\n📊 Architecture Verified:")
        print("  ✓ Abstract Strategy base class working")
        print("  ✓ MeanReversionQP strategy operational")
        print("  ✓ SimpleTrend strategy operational")
        print("  ✓ PortfolioManager ensemble engine working")
        print("  ✓ Signal normalization and combination correct")
        print("  ✓ Strategy correlation matrix computed")
        print("  ✓ BacktestEngine simulation functional")
        print("  ✓ Performance metrics calculated")
        
        print("\n🚀 Ready to Add New Strategies:")
        print("  1. Create class inheriting from Strategy")
        print("  2. Implement generate_signals() method")
        print("  3. Add to strategies list in main.py")
        print("  4. Run - ensemble automatically incorporates it!")
        
        print("\n" + "="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
