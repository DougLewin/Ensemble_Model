"""
Backtesting Engine & Performance Reporting
===========================================
Event-driven backtest with standard performance metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional
from datetime import datetime


class BacktestEngine:
    """
    Event-driven backtesting engine.
    
    Simulates portfolio rebalancing and tracks performance metrics.
    """
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 commission: float = 0.001,  # 0.1% per trade
                 slippage: float = 0.0005):  # 0.05% slippage
        """
        Initialize Backtest Engine.
        
        Args:
            initial_capital: Starting portfolio value
            commission: Trading commission (as decimal)
            slippage: Price slippage (as decimal)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Performance tracking
        self.equity_curve = []
        self.daily_returns = []
        self.positions_history = []
        self.trades = []
    
    def run(self, 
            data: pd.DataFrame, 
            signals: pd.DataFrame) -> pd.DataFrame:
        """
        Run backtest simulation.
        
        Args:
            data: Market data with MultiIndex (date, ticker)
            signals: Signal DataFrame with 'weight' column
        
        Returns:
            DataFrame with equity curve and metrics
        """
        print(f"\n{'='*60}")
        print("BACKTEST ENGINE: Running Simulation")
        print(f"{'='*60}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Commission: {self.commission*100:.2f}%")
        print(f"Slippage: {self.slippage*100:.3f}%")
        
        # Get unique dates
        dates = data.index.get_level_values('date').unique().sort_values()
        
        # Initialize portfolio
        cash = self.initial_capital
        positions = {}  # ticker -> (shares, entry_price)
        portfolio_value = self.initial_capital
        
        for i, date in enumerate(dates):
            # Get today's prices and weights
            try:
                today_data = data.loc[date]
                today_signals = signals.loc[date]
            except KeyError:
                continue
            
            # Combine data and signals
            if isinstance(today_data, pd.Series):
                today_data = today_data.to_frame().T
            if isinstance(today_signals, pd.Series):
                today_signals = today_signals.to_frame().T
            
            combined = today_data.join(today_signals[['weight']], how='left')
            combined['weight'] = combined['weight'].fillna(0.0)
            
            # Calculate current portfolio value
            positions_value = 0.0
            for ticker, (shares, _) in positions.items():
                if ticker in combined.index:
                    current_price = combined.loc[ticker, 'close']
                    positions_value += shares * current_price
            
            portfolio_value = cash + positions_value
            
            # Rebalance portfolio
            target_positions = {}
            for ticker in combined.index:
                weight = combined.loc[ticker, 'weight']
                if weight > 0:
                    target_value = portfolio_value * weight
                    price = combined.loc[ticker, 'close']
                    target_shares = target_value / (price * (1 + self.slippage))
                    target_positions[ticker] = (target_shares, price)
            
            # Close positions not in target
            for ticker in list(positions.keys()):
                if ticker not in target_positions:
                    shares, entry_price = positions[ticker]
                    if ticker in combined.index:
                        exit_price = combined.loc[ticker, 'close'] * (1 - self.slippage)
                        cash += shares * exit_price * (1 - self.commission)
                        
                        # Record trade
                        pnl = shares * (exit_price - entry_price)
                        self.trades.append({
                            'date': date,
                            'ticker': ticker,
                            'action': 'SELL',
                            'shares': shares,
                            'price': exit_price,
                            'pnl': pnl
                        })
                    del positions[ticker]
            
            # Open/adjust positions in target
            for ticker, (target_shares, entry_price) in target_positions.items():
                current_shares = positions.get(ticker, (0, 0))[0]
                shares_diff = target_shares - current_shares
                
                if abs(shares_diff) > 0.01:  # Minimum trade threshold
                    trade_value = shares_diff * entry_price * (1 + self.slippage)
                    commission_cost = abs(trade_value) * self.commission
                    cash -= (trade_value + commission_cost)
                    positions[ticker] = (target_shares, entry_price)
                    
                    # Record trade
                    self.trades.append({
                        'date': date,
                        'ticker': ticker,
                        'action': 'BUY' if shares_diff > 0 else 'SELL',
                        'shares': abs(shares_diff),
                        'price': entry_price,
                        'pnl': 0.0
                    })
            
            # Record daily equity
            self.equity_curve.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'positions_value': positions_value,
                'num_positions': len(positions)
            })
            
            # Calculate daily return
            if i > 0:
                prev_value = self.equity_curve[i-1]['portfolio_value']
                daily_return = (portfolio_value - prev_value) / prev_value
                self.daily_returns.append(daily_return)
            
            # Store positions snapshot
            self.positions_history.append({
                'date': date,
                'positions': positions.copy()
            })
        
        # Convert to DataFrame
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df = equity_df.set_index('date')
        
        print(f"\n✓ Backtest completed: {len(dates)} trading days")
        print(f"  Final Portfolio Value: ${portfolio_value:,.2f}")
        print(f"  Total Return: {(portfolio_value/self.initial_capital - 1)*100:.2f}%")
        print(f"  Number of Trades: {len(self.trades)}")
        
        return equity_df
    
    def get_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics."""
        if len(self.daily_returns) == 0:
            return {"error": "No backtest results available"}
        
        returns = pd.Series(self.daily_returns)
        equity = pd.DataFrame(self.equity_curve)
        
        # Basic metrics
        total_return = (equity['portfolio_value'].iloc[-1] / self.initial_capital) - 1
        
        # Annualized metrics (assuming 252 trading days)
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        annualized_vol = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(self.trades) if len(self.trades) > 0 else 0
        
        metrics = {
            'Total Return': f"{total_return*100:.2f}%",
            'Annualized Return': f"{annualized_return*100:.2f}%",
            'Annualized Volatility': f"{annualized_vol*100:.2f}%",
            'Sharpe Ratio': f"{sharpe_ratio:.3f}",
            'Maximum Drawdown': f"{max_drawdown*100:.2f}%",
            'Win Rate': f"{win_rate*100:.2f}%",
            'Total Trades': len(self.trades),
            'Avg Positions': equity['num_positions'].mean(),
            'Final Value': f"${equity['portfolio_value'].iloc[-1]:,.2f}"
        }
        
        return metrics
    
    def plot_results(self, save_path: Optional[str] = None):
        """
        Plot backtest results with equity curve and drawdown.
        
        Args:
            save_path: Optional path to save the figure
        """
        if len(self.equity_curve) == 0:
            print("No results to plot")
            return
        
        equity_df = pd.DataFrame(self.equity_curve).set_index('date')
        returns = pd.Series(self.daily_returns)
        
        # Calculate drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        # Create figure
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle('Ensemble Strategy Backtest Results', fontsize=16, fontweight='bold')
        
        # Plot 1: Equity Curve
        ax1 = axes[0]
        ax1.plot(equity_df.index, equity_df['portfolio_value'], linewidth=2, color='#2E86AB')
        ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5)
        ax1.set_title('Portfolio Value Over Time', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.legend(['Portfolio Value', 'Initial Capital'], loc='upper left')
        
        # Plot 2: Drawdown
        ax2 = axes[1]
        ax2.fill_between(range(len(drawdown)), drawdown * 100, 0, 
                         color='#A23B72', alpha=0.6)
        ax2.set_title('Drawdown Analysis', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Number of Positions
        ax3 = axes[2]
        ax3.plot(equity_df.index, equity_df['num_positions'], 
                linewidth=1.5, color='#F18F01', marker='o', markersize=3)
        ax3.set_title('Portfolio Composition', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Number of Positions', fontsize=10)
        ax3.set_xlabel('Date', fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Results saved to: {save_path}")
        else:
            plt.show()
    
    def print_performance_report(self):
        """Print formatted performance report."""
        metrics = self.get_performance_metrics()
        
        print(f"\n{'='*60}")
        print("PERFORMANCE REPORT")
        print(f"{'='*60}")
        
        for key, value in metrics.items():
            print(f"{key:.<30} {value}")
        
        print(f"{'='*60}")
