import pandas as pd
import yfinance as yf
import json 
from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

def load_portfolio(file_path='portfolio.csv'): 
    try: 
        positions = trading_client.get_all_positions()
        data = []
        for p in positions:
            data.append({'tick': p.symbol, 'shares': float(p.qty)})
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[!] Could not fetch live portfolio. Falling back to CSV. Error: {e}")
        return pd.read_csv(file_path)

def load_target_alloc(file_path='target_allocation.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_stock_prices(tickers):
    prices = {}
    for tick in tickers:
        try: 
            stock = yf.Ticker(tick)
            prices[tick] = stock.info['regularMarketPrice']
        except Exception as e:
            print(f"Error fetching price for {tick}: {e}")
            prices[tick] = 0
    return prices

def calc_values(portfolio_df, prices):
    portfolio_df['price'] = portfolio_df['tick'].map(prices)
    portfolio_df['val'] = portfolio_df['shares'] * portfolio_df['price']
    return portfolio_df

def suggest_rebalance(portfolio_df, target_alloc): 
    total_val = portfolio['val'].sum()
    suggestions = []

    for _, row in portfolio_df.iterrows(): 
        tick =  row['tick']
        curr_pct = row['val'] / total_val
        target_pct = target_alloc.get(tick, 0)
        diff_pct = target_pct - curr_pct
        dollar_diff = diff_pct * total_val
        shares_diff = int(dollar_diff // row['price'])

        if shares_diff > 0: 
            suggestions.append(f"Buy {shares_diff} shares of {tick}")
        elif shares_diff < 0: 
            suggestions.append(f"Sell {-shares_diff} shares of {tick}")
        else: 
            suggestions.append(f"{tick} is already balanced.")
    
    return suggestions

if __name__ == "__main__":
    portfolio = load_portfolio()
    # print(portfolio.head())
    target_alloc = load_target_alloc()
    tickers = portfolio['tick'].tolist()

    prices = get_stock_prices(tickers)
    portfolio = calc_values(portfolio, prices)

    suggestions = suggest_rebalance(portfolio, target_alloc)
    print("\n--- Rebalancing Suggestions ---")
    for s in suggestions:
        print(s)

