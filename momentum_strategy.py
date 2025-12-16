"""
Example: Adding a Third Strategy (Strategy C)
==============================================
Demonstrates how easy it is to extend the ensemble system.

This is a Momentum Strategy that you can plug directly into the ensemble.
"""

import pandas as pd
import numpy as np
from strategy_base import Strategy


class MomentumStrategy(Strategy):
    """
    Simple Momentum Strategy.
    
    Core Logic:
    - Calculate return over lookback period
    - Positive momentum = BUY signal
    - Negative momentum = SELL signal
    
    Signal Strength: Normalized momentum returns
    """
    
    def __init__(self, 
                 name: str = "Momentum",
                 lookback: int = 20):
        """
        Initialize Momentum Strategy.
        
        Args:
            name: Strategy identifier
            lookback: Lookback period for momentum calculation
        """
        super().__init__(name)
        self.lookback = lookback
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate momentum signals.
        
        Returns:
            DataFrame with 'signal' column: +1.0 (strong momentum) to -1.0 (weak momentum)
        """
        df = data.copy()
        
        # Calculate momentum (return over lookback period)
        df['momentum'] = df.groupby(level='ticker')['close'].pct_change(self.lookback)
        
        # Normalize using tanh (maps to [-1, 1])
        df['signal'] = np.tanh(df['momentum'] * 10)  # 10 is sensitivity factor
        
        # Handle NaN values
        df['signal'] = df['signal'].fillna(0.0)
        
        # Confidence: based on absolute momentum (strong moves = high confidence)
        df['confidence'] = np.abs(df['momentum']).clip(0, 0.5) / 0.5
        df['confidence'] = df['confidence'].fillna(0.5)
        
        return df[['signal', 'confidence']]
    
    def __repr__(self) -> str:
        return f"MomentumStrategy(name='{self.name}', lookback={self.lookback})"


# ============================================================
# HOW TO USE THIS STRATEGY
# ============================================================
"""
In main.py, simply:

1. Import it:
   from momentum_strategy import MomentumStrategy

2. Initialize it:
   momentum = MomentumStrategy(name="Momentum", lookback=20)

3. Add to the strategies list:
   portfolio_manager = PortfolioManager(
       strategies=[mean_reversion, trend_following, momentum],  # <-- Add here!
       config=config
   )

That's it! The ensemble automatically:
- Generates momentum signals
- Normalizes them
- Combines with other strategies
- Updates correlation matrix
- Includes in portfolio selection

The power of modular architecture!
"""
