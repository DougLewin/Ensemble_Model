"""
Portfolio Manager - The Ensemble Engine
=========================================
Combines multiple strategies using "Learning to Rank" philosophy.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from strategy_base import Strategy


@dataclass
class PortfolioConfig:
    """Configuration for Portfolio Manager."""
    top_n_assets: int = 5  # Select top N assets by combined score
    rebalance_frequency: str = 'daily'  # 'daily', 'weekly', 'monthly'
    equal_weight: bool = True  # Equal weight or proportional to signal strength
    long_only: bool = True  # Only long positions or allow shorts


class PortfolioManager:
    """
    Ensemble Engine: Combines multiple strategies and ranks assets.
    
    Philosophy: "Learning to Rank" - focus on relative comparison, not absolute values.
    """
    
    def __init__(self, 
                 strategies: List[Strategy],
                 config: Optional[PortfolioConfig] = None):
        """
        Initialize Portfolio Manager.
        
        Args:
            strategies: List of Strategy objects to combine
            config: Portfolio configuration parameters
        """
        self.strategies = strategies
        self.config = config or PortfolioConfig()
        self.strategy_signals = {}  # Store individual strategy signals
        self.combined_signals = None
        self.correlation_matrix = None
    
    def generate_ensemble_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate ensemble signals by combining all strategies.
        
        Args:
            data: Market data with MultiIndex (date, ticker)
        
        Returns:
            DataFrame with combined signals and rankings
        """
        print(f"\n{'='*60}")
        print(f"ENSEMBLE ENGINE: Combining {len(self.strategies)} Strategies")
        print(f"{'='*60}")
        
        all_signals = []
        
        # Step 1: Generate signals from each strategy
        for strategy in self.strategies:
            print(f"\n→ Running: {strategy}")
            signals = strategy.generate_signals(data)
            signals = signals.rename(columns={'signal': f'signal_{strategy.name}'})
            all_signals.append(signals[[f'signal_{strategy.name}']])
            self.strategy_signals[strategy.name] = signals
        
        # Step 2: Combine all signals into one DataFrame
        combined = pd.concat(all_signals, axis=1)
        
        # Step 3: Normalize signals (z-score normalization per strategy)
        for col in combined.columns:
            if col.startswith('signal_'):
                mean = combined[col].mean()
                std = combined[col].std()
                if std > 0:
                    combined[f'{col}_normalized'] = (combined[col] - mean) / std
                else:
                    combined[f'{col}_normalized'] = 0.0
        
        # Step 4: Sum normalized signals (equal weight)
        signal_cols = [col for col in combined.columns if col.endswith('_normalized')]
        combined['combined_score'] = combined[signal_cols].sum(axis=1)
        
        # Step 5: Rank assets by combined score (per date)
        combined['rank'] = combined.groupby(level='date')['combined_score'].rank(
            ascending=False, method='first'
        )
        
        # Step 6: Generate positions (top N assets)
        combined['position'] = 0.0
        combined.loc[combined['rank'] <= self.config.top_n_assets, 'position'] = 1.0
        
        # Equal weight allocation
        if self.config.equal_weight:
            combined['weight'] = combined['position'] / self.config.top_n_assets
        else:
            # Proportional to signal strength
            combined['weight'] = combined['combined_score'] / combined.groupby(level='date')['combined_score'].transform('sum')
            combined['weight'] = combined['weight'].fillna(0.0)
        
        self.combined_signals = combined
        
        # Step 7: Calculate strategy correlation matrix
        self._calculate_strategy_correlation()
        
        print(f"\n✓ Ensemble signals generated successfully")
        print(f"  Top {self.config.top_n_assets} assets selected per rebalance")
        
        return combined
    
    def _calculate_strategy_correlation(self):
        """Calculate correlation matrix between strategies."""
        signal_cols = [col for col in self.combined_signals.columns 
                      if col.startswith('signal_') and not col.endswith('_normalized')]
        
        if len(signal_cols) > 0:
            self.correlation_matrix = self.combined_signals[signal_cols].corr()
            
            print(f"\n{'─'*60}")
            print("STRATEGY CORRELATION MATRIX")
            print(f"{'─'*60}")
            print(self.correlation_matrix.round(3))
            print(f"{'─'*60}")
            print("💡 Insight: Low correlation = good diversification")
            print("   High correlation = strategies are redundant")
    
    def get_portfolio_weights(self, date: str) -> pd.Series:
        """
        Get portfolio weights for a specific date.
        
        Args:
            date: Date string or timestamp
        
        Returns:
            Series with ticker -> weight mapping
        """
        if self.combined_signals is None:
            raise ValueError("Must call generate_ensemble_signals first")
        
        try:
            weights = self.combined_signals.loc[date, 'weight']
            return weights[weights > 0]
        except KeyError:
            return pd.Series(dtype=float)
    
    def get_top_assets(self, date: str, top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Get top N assets for a specific date with their scores.
        
        Args:
            date: Date string or timestamp
            top_n: Number of top assets (default: from config)
        
        Returns:
            DataFrame with top assets and their metrics
        """
        if self.combined_signals is None:
            raise ValueError("Must call generate_ensemble_signals first")
        
        n = top_n or self.config.top_n_assets
        
        try:
            date_data = self.combined_signals.loc[date]
            top = date_data.nlargest(n, 'combined_score')
            return top[['combined_score', 'rank', 'weight']]
        except KeyError:
            return pd.DataFrame()
    
    def summary(self) -> Dict:
        """Get summary statistics of the ensemble."""
        if self.combined_signals is None:
            return {"error": "No signals generated yet"}
        
        summary = {
            "num_strategies": len(self.strategies),
            "strategy_names": [s.name for s in self.strategies],
            "avg_combined_score": self.combined_signals['combined_score'].mean(),
            "std_combined_score": self.combined_signals['combined_score'].std(),
            "assets_selected_per_period": self.config.top_n_assets,
            "correlation_matrix": self.correlation_matrix.to_dict() if self.correlation_matrix is not None else None
        }
        
        return summary
    
    def __repr__(self) -> str:
        return (f"PortfolioManager(strategies={len(self.strategies)}, "
                f"top_n={self.config.top_n_assets})")
