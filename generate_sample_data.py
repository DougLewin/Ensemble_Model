"""
Generate Sample NASDAQ.csv File
================================
Creates a synthetic NASDAQ dataset for testing the Streamlit dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_nasdaq_csv(
    filename: str = "NASDAQ.csv",
    num_tickers: int = 20,
    num_days: int = 500,
    seed: int = 42
):
    """
    Generate a synthetic NASDAQ dataset.
    
    Args:
        filename: Output CSV filename
        num_tickers: Number of stocks to simulate
        num_days: Number of trading days
        seed: Random seed for reproducibility
    """
    
    np.random.seed(seed)
    
    print(f"Generating {filename}...")
    print(f"  Tickers: {num_tickers}")
    print(f"  Days: {num_days}")
    
    # Real NASDAQ tickers for realism
    nasdaq_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
        'COST', 'ASML', 'PEP', 'NFLX', 'AMD', 'ADBE', 'CMCSA', 'INTC',
        'CSCO', 'QCOM', 'TXN', 'INTU', 'HON', 'AMAT', 'AMGN', 'SBUX'
    ]
    
    # Select tickers
    selected_tickers = nasdaq_tickers[:num_tickers]
    
    # Generate dates (business days)
    dates = pd.date_range(start='2022-01-01', periods=num_days, freq='B')
    
    data = []
    
    for ticker in selected_tickers:
        # Unique characteristics for each stock
        drift = np.random.uniform(-0.0003, 0.0008)  # Daily return
        volatility = np.random.uniform(0.015, 0.035)  # Daily volatility
        initial_price = np.random.uniform(50, 500)
        
        # Generate price series using Geometric Brownian Motion
        returns = np.random.normal(drift, volatility, num_days)
        
        # Add mean reversion
        ar_coefficient = np.random.uniform(0.2, 0.5)
        for i in range(1, len(returns)):
            returns[i] += -ar_coefficient * returns[i-1]
        
        # Convert to prices
        prices = initial_price * np.exp(np.cumsum(returns))
        
        # Generate OHLCV for each day
        for i, (date, close) in enumerate(zip(dates, prices)):
            daily_vol = volatility * close
            
            # Realistic OHLC generation
            open_price = close * np.random.uniform(0.99, 1.01)
            high_price = max(open_price, close) * np.random.uniform(1.0, 1.02)
            low_price = min(open_price, close) * np.random.uniform(0.98, 1.0)
            
            # Volume with realistic patterns (higher on volatile days)
            base_volume = np.random.uniform(5e6, 20e6)
            volume_multiplier = 1 + abs(returns[i]) * 50
            volume = int(base_volume * volume_multiplier)
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Ticker': ticker,
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close, 2),
                'Volume': volume
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    print(f"✅ Successfully generated {filename}")
    print(f"   Total rows: {len(df):,}")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   Tickers: {', '.join(selected_tickers[:5])}{'...' if len(selected_tickers) > 5 else ''}")
    print()
    print("You can now run the Streamlit dashboard:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    generate_nasdaq_csv(
        filename="NASDAQ.csv",
        num_tickers=20,
        num_days=500,
        seed=42
    )
