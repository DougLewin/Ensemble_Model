"""
Abstract Base Class for Trading Strategies
===========================================
Following "The Bitter Lesson": Keep components simple and standardized.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Philosophy: Every strategy must produce standardized signals 
    that can be compared and combined.
    """
    
    def __init__(self, name: str):
        """
        Initialize the strategy with a name.
        
        Args:
            name: Unique identifier for this strategy
        """
        self.name = name
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals for all assets.
        
        Args:
            data: DataFrame with MultiIndex (date, ticker) or single ticker
                  Must contain: 'open', 'high', 'low', 'close', 'volume'
        
        Returns:
            DataFrame with columns:
                - 'signal': Float between -1.0 (strong sell) and +1.0 (strong buy)
                - 'confidence': Optional, float between 0.0 and 1.0
            Index: Same as input (date, ticker) or (date,)
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
