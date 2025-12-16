"""
Mean Reversion Strategy (Murphy's Law Principle)
=================================================
"Buy when things look bad" - Target assets with low Quality-Price-Indicator
"""

import pandas as pd
import numpy as np
from strategy_base import Strategy


class MeanReversionQP(Strategy):
    """
    Mean Reversion Strategy based on Quality-Price Indicator (QPI).
    
    Core Logic:
    - QPI = (Price / Moving Average) * (Volatility / Historical Volatility)
    - Low QPI = Asset is "cheap" and "stable" -> BUY signal
    - High QPI = Asset is "expensive" and "volatile" -> SELL signal
    
    Signal Strength: Inverse normalized QPI scaled to [-1, 1]
    """
    
    def __init__(self, 
                 name: str = "MeanReversionQP",
                 lookback_ma: int = 50,
                 lookback_vol: int = 20,
                 historical_vol_period: int = 252):
        """
        Initialize Mean Reversion Strategy.
        
        Args:
            name: Strategy identifier
            lookback_ma: Moving average period for price normalization
            lookback_vol: Recent volatility calculation period
            historical_vol_period: Historical volatility baseline
        """
        super().__init__(name)
        self.lookback_ma = lookback_ma
        self.lookback_vol = lookback_vol
        self.historical_vol_period = historical_vol_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate mean reversion signals based on QPI.
        
        Returns:
            DataFrame with 'signal' column: +1.0 (strong buy) to -1.0 (strong sell)
        """
        df = data.copy()
        
        # Calculate Moving Average
        df['ma'] = df.groupby(level='ticker')['close'].transform(
            lambda x: x.rolling(self.lookback_ma, min_periods=1).mean()
        )
        
        # Calculate Recent Volatility (standard deviation of returns)
        df['returns'] = df.groupby(level='ticker')['close'].pct_change()
        df['recent_vol'] = df.groupby(level='ticker')['returns'].transform(
            lambda x: x.rolling(self.lookback_vol, min_periods=1).std()
        )
        
        # Calculate Historical Volatility (long-term baseline)
        df['historical_vol'] = df.groupby(level='ticker')['returns'].transform(
            lambda x: x.rolling(self.historical_vol_period, min_periods=self.lookback_vol).mean()
        )
        
        # Quality-Price Indicator (QPI)
        df['price_ratio'] = df['close'] / df['ma']
        df['vol_ratio'] = df['recent_vol'] / (df['historical_vol'] + 1e-8)  # Avoid division by zero
        df['qpi'] = df['price_ratio'] * df['vol_ratio']
        
        # Generate signals: Inverse of QPI (low QPI = strong buy)
        # Normalize QPI to [-1, 1] using percentile ranks within each date
        df['qpi_rank'] = df.groupby(level='date')['qpi'].rank(pct=True)
        
        # Invert and scale: low QPI (rank close to 0) -> signal close to +1
        df['signal'] = 1.0 - 2.0 * df['qpi_rank']  # Maps [0, 1] to [1, -1]
        
        # Handle NaN values
        df['signal'] = df['signal'].fillna(0.0)
        
        # Confidence: inverse of volatility ratio (stable = high confidence)
        df['confidence'] = 1.0 / (1.0 + df['vol_ratio'])
        df['confidence'] = df['confidence'].fillna(0.5)
        
        return df[['signal', 'confidence']]
    
    def __repr__(self) -> str:
        return (f"MeanReversionQP(name='{self.name}', "
                f"MA={self.lookback_ma}, Vol={self.lookback_vol})")
