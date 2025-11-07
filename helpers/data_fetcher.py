"""
Data fetching functions for stock and macroeconomic data
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from .constants import Colors, FRED_API_KEY, FRED_API_BASE_URL
from .zacks_scrapper import get_zacks_recommendation_for_ticker


def get_financial_data(ticker):
    """Fetch financial data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get financial statements
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        quarterly_financials = stock.quarterly_financials
        
        # Get historical data for price metrics
        hist = stock.history(period="max")  # Get all available historical data
        
        # Get analyst recommendations
        recommendations = None
        try:
            recommendations = stock.recommendations
        except Exception:
            pass
        
        # Get Zacks recommendation
        zacks_data = None
        try:
            print(f"{Colors.YELLOW}Fetching Zacks.com recommendation for {ticker}...{Colors.END}")
            zacks_data = get_zacks_recommendation(ticker)
        except Exception as e:
            # Silently fail - Zacks data is optional
            pass
        
        # Get earnings calendar for next earnings date
        next_earnings_date = None
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                # Try to get next earnings date from calendar
                if 'Earnings Date' in calendar.index:
                    earnings_dates = calendar.loc['Earnings Date']
                    if len(earnings_dates) > 0:
                        next_earnings_date = earnings_dates.iloc[0]
        except Exception:
            pass
        
        return {
            'ticker': ticker,
            'info': info,
            'financials': financials,
            'balance_sheet': balance_sheet,
            'cashflow': cashflow,
            'quarterly_financials': quarterly_financials,
            'history': hist,
            'recommendations': recommendations,
            'zacks_data': zacks_data,
            'next_earnings_date': next_earnings_date
        }
    except Exception as e:
        print(f"{Colors.RED}Error fetching data: {e}{Colors.END}")
        return None


def get_macro_data():
    """Fetch macroeconomic data from FRED API"""
    macro_data = {}
    
    if not FRED_API_KEY:
        return macro_data
    
    try:
        # Get 10-Year Treasury Rate
        try:
            url = f"{FRED_API_BASE_URL}/series/observations"
            params = {
                'series_id': 'DGS10',
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    macro_data['treasury_10y'] = float(data['observations'][0]['value'])
        except Exception:
            pass
        
        # Get Federal Funds Rate
        try:
            params['series_id'] = 'FEDFUNDS'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    macro_data['fed_funds_rate'] = float(data['observations'][0]['value'])
        except Exception:
            pass
        
        # Get GDP Growth Rate
        try:
            params['series_id'] = 'A191RL1Q225SBEA'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    macro_data['gdp_growth'] = float(data['observations'][0]['value'])
        except Exception:
            pass
        
        # Get Unemployment Rate
        try:
            params['series_id'] = 'UNRATE'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    macro_data['unemployment_rate'] = float(data['observations'][0]['value'])
        except Exception:
            pass
        
        # Get Inflation Rate (CPI)
        try:
            params['series_id'] = 'CPIAUCSL'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 1:
                    current = float(data['observations'][0]['value'])
                    previous = float(data['observations'][1]['value'])
                    macro_data['inflation_rate'] = ((current - previous) / previous) * 100
        except Exception:
            pass
    except Exception:
        pass
    
    return macro_data


def get_zacks_recommendation(ticker):
    """
    Scrape Zacks.com to get stock recommendation (Buy, Hold, Sell)
    Uses the zacks_scrapper.py module for all Zacks data extraction.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dictionary with recommendation data or None if unavailable
    """
    try:
        # Use the zacks_scrapper module to get all Zacks data
        zacks_data = get_zacks_recommendation_for_ticker(ticker)
        
        # Return None if no recommendation was found
        if not zacks_data.get('recommendation'):
            return None
        
        return zacks_data
        
    except Exception as e:
        # Silently fail - Zacks data is optional
        return None
