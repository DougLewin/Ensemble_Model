"""
Simple Trend Following Strategy
=================================
Classic momentum: "Buy the winners, sell the losers"
"""

import pandas as pd
import numpy as np
from strategy_base import Strategy


class SimpleTrend(Strategy):
    """
    Simple Trend Following Strategy using Moving Average crossover.
    
    Core Logic:
    - Signal = +1.0 if Price > Long-term SMA (bullish trend)
    - Signal = -1.0 if Price < Long-term SMA (bearish trend)
    - Signal strength modulated by distance from SMA
    """
    
    def __init__(self, 
                 name: str = "SimpleTrend",
                 sma_period: int = 200):
        """
        Initialize Simple Trend Strategy.
        
        Args:
            name: Strategy identifier
            sma_period: Period for the Simple Moving Average
        """
        super().__init__(name)
        self.sma_period = sma_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trend-following signals.
        
        Returns:
            DataFrame with 'signal' column: +1.0 (strong uptrend) to -1.0 (strong downtrend)
        """
        df = data.copy()
        
        # Calculate SMA
        df['sma'] = df.groupby(level='ticker')['close'].transform(
            lambda x: x.rolling(self.sma_period, min_periods=1).mean()
        )
        
        # Price distance from SMA (percentage)
        df['distance_pct'] = (df['close'] - df['sma']) / df['sma']
        
        # Generate signals: positive distance = bullish, negative = bearish
        # Clip to [-1, 1] range and apply tanh for smooth scaling
        df['signal'] = np.tanh(df['distance_pct'] * 5)  # 5 is sensitivity factor
        
        # Handle NaN values
        df['signal'] = df['signal'].fillna(0.0)
        
        # Confidence: based on how far we are from SMA (larger distance = higher confidence)
        df['confidence'] = np.abs(df['distance_pct']).clip(0, 0.2) / 0.2  # Normalize to [0, 1]
        df['confidence'] = df['confidence'].fillna(0.5)
        
        return df[['signal', 'confidence']]
    
    def __repr__(self) -> str:
        return f"SimpleTrend(name='{self.name}', SMA={self.sma_period})"
