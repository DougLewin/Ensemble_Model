"""
Architecture Visualization
===========================
Visual representation of the Ensemble Trading System architecture.
"""

ARCHITECTURE = """
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENSEMBLE TRADING SYSTEM                              │
│                    ═══════════════════════════                          │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  Market Data │
                              │   (OHLCV)    │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │  Strategy A  │  │  Strategy B  │  │  Strategy C  │
          │──────────────│  │──────────────│  │──────────────│
          │ Mean         │  │ Trend        │  │ Momentum     │
          │ Reversion    │  │ Following    │  │ (Extensible) │
          └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                 │                 │                  │
                 │  signal: [-1,1] │  signal: [-1,1]  │  signal: [-1,1]
                 │  confidence     │  confidence      │  confidence
                 │                 │                  │
                 └─────────────────┼──────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   PORTFOLIO MANAGER          │
                    │   ═══════════════            │
                    │   (Ensemble Engine)          │
                    │                              │
                    │  1. Normalize signals        │
                    │  2. Combine (sum)            │
                    │  3. Rank assets              │
                    │  4. Select top N             │
                    │  5. Calculate weights        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
                    ▼                              ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Correlation      │          │ Portfolio        │
          │ Matrix           │          │ Weights          │
          │                  │          │                  │
          │ Shows strategy   │          │ Top N assets     │
          │ diversification  │          │ with allocation  │
          └──────────────────┘          └────────┬─────────┘
                                                  │
                                                  ▼
                                   ┌──────────────────────────┐
                                   │   BACKTEST ENGINE        │
                                   │   ═══════════════        │
                                   │                          │
                                   │  • Event-driven sim      │
                                   │  • Commission/slippage   │
                                   │  • Position tracking     │
                                   │  • Performance metrics   │
                                   └──────────┬───────────────┘
                                              │
                            ┌─────────────────┼─────────────────┐
                            │                 │                 │
                            ▼                 ▼                 ▼
                  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                  │ Equity Curve │  │ Sharpe Ratio │  │ Drawdown     │
                  │ Visualization│  │ & Returns    │  │ Analysis     │
                  └──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  KEY PRINCIPLES                                                         │
│  ══════════════                                                         │
│                                                                         │
│  1. THE BITTER LESSON (Rich Sutton)                                    │
│     • Keep components simple                                           │
│     • Let the system scale with data                                   │
│     • Avoid hand-crafted complexity                                    │
│                                                                         │
│  2. LEARNING TO RANK                                                   │
│     • Focus on relative comparison                                     │
│     • Rank assets against each other                                   │
│     • Top-N selection more robust than absolute prediction             │
│                                                                         │
│  3. MODULARITY                                                         │
│     • Abstract Strategy interface                                      │
│     • Easy to add new strategies (just inherit & implement)            │
│     • Ensemble automatically incorporates new components               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""

COMPONENT_DETAILS = """
┌─────────────────────────────────────────────────────────────────────────┐
│  COMPONENT BREAKDOWN                                                    │
└─────────────────────────────────────────────────────────────────────────┘

1. STRATEGY BASE CLASS (strategy_base.py)
   ─────────────────────────────────────
   • Abstract class enforcing standard interface
   • Required method: generate_signals(data) -> DataFrame
   • Output: signal [-1, 1], confidence [0, 1]

2. STRATEGY IMPLEMENTATIONS
   ──────────────────────────
   
   A. MeanReversionQP (mean_reversion_strategy.py)
      • Logic: Buy when QPI (Quality-Price-Indicator) is low
      • QPI = (Price/MA) * (RecentVol/HistoricalVol)
      • Signal: Inverse normalized QPI
   
   B. SimpleTrend (trend_strategy.py)
      • Logic: Buy when Price > SMA
      • Signal: Distance from SMA (tanh scaled)
   
   C. MomentumStrategy (momentum_strategy.py)
      • Logic: Buy assets with positive momentum
      • Signal: Normalized return over lookback period

3. PORTFOLIO MANAGER (portfolio_manager.py)
   ──────────────────────────────────────
   • Combines multiple strategies
   • Z-score normalization per strategy
   • Sum normalized signals → Combined Score
   • Rank assets by Combined Score
   • Select top N assets
   • Calculate strategy correlation matrix

4. BACKTEST ENGINE (backtest_engine.py)
   ─────────────────────────────────────
   • Event-driven simulation (day-by-day)
   • Rebalancing logic
   • Transaction costs (commission + slippage)
   • Position tracking
   • Performance metrics:
     - Total Return
     - Sharpe Ratio
     - Maximum Drawdown
     - Win Rate
     - Annualized Return/Volatility

5. MAIN EXECUTION (main.py)
   ─────────────────────────
   • Orchestrates the entire pipeline
   • Generate/load market data
   • Initialize strategies
   • Create ensemble
   • Run backtest
   • Generate reports & visualizations
"""

HOW_TO_EXTEND = """
┌─────────────────────────────────────────────────────────────────────────┐
│  HOW TO ADD A NEW STRATEGY                                              │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: Create Your Strategy Class
───────────────────────────────────

from strategy_base import Strategy
import pandas as pd
import numpy as np

class YourStrategy(Strategy):
    def __init__(self, name="YourStrategy", param1=10):
        super().__init__(name)
        self.param1 = param1
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Your logic here
        df['signal'] = ...  # Calculate signal [-1, 1]
        df['confidence'] = ...  # Calculate confidence [0, 1]
        
        return df[['signal', 'confidence']]


STEP 2: Add to main.py
──────────────────────

from your_strategy import YourStrategy

# In main():
your_strategy = YourStrategy(name="Custom", param1=20)

portfolio_manager = PortfolioManager(
    strategies=[mean_reversion, trend_following, your_strategy],
    config=config
)


STEP 3: Run!
────────────

python main.py

The ensemble automatically:
✓ Generates your signals
✓ Normalizes them
✓ Combines with others
✓ Updates correlation matrix
✓ Includes in portfolio selection

That's the power of modular design! 🚀
"""


def print_architecture():
    """Print the architecture diagram."""
    print(ARCHITECTURE)
    print("\n")
    print(COMPONENT_DETAILS)
    print("\n")
    print(HOW_TO_EXTEND)


if __name__ == "__main__":
    print_architecture()
