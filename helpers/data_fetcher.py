"""
Data fetching functions for stock and macroeconomic data
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from .constants import Colors, FRED_API_KEY, FRED_API_BASE_URL


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
        
        # Get earnings calendar for next earnings date
        next_earnings_date = None
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                # Try to get next earnings date from calendar
                if 'Earnings Date' in calendar.index:
                    earnings_dates = calendar.loc['Earnings Date']
                    if len(earnings_dates) > 0:
                        # Get the first (most recent) earnings date
                        next_earnings_date = earnings_dates.iloc[0] if hasattr(earnings_dates, 'iloc') else earnings_dates[0]
                # Try alternative column names
                elif 'Earnings' in calendar.index:
                    earnings_dates = calendar.loc['Earnings']
                    if len(earnings_dates) > 0:
                        next_earnings_date = earnings_dates.iloc[0] if hasattr(earnings_dates, 'iloc') else earnings_dates[0]
        except Exception:
            pass
        
        # Fallback to info fields
        if not next_earnings_date:
            # Try various date fields that might contain earnings info
            for field in ['earningsDate', 'nextFiscalYearEnd', 'exDividendDate', 'mostRecentQuarter']:
                date_value = info.get(field)
                if date_value:
                    try:
                        # Try to parse if it's a timestamp
                        if isinstance(date_value, (int, float)):
                            next_earnings_date = datetime.fromtimestamp(date_value)
                        else:
                            next_earnings_date = date_value
                        break
                    except:
                        continue
        
        return {
            'info': info,
            'financials': financials,
            'quarterly_financials': quarterly_financials,
            'balance_sheet': balance_sheet,
            'cashflow': cashflow,
            'stock': stock,
            'history': hist,
            'next_earnings_date': next_earnings_date,
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"{Colors.RED}Error fetching data: {e}{Colors.END}")
        return None


def get_fred_data(series_id, api_key=None):
    """Fetch data from FRED API for a given series ID"""
    if not api_key:
        api_key = FRED_API_KEY
    
    if not api_key:
        return None, None
    
    try:
        url = f"{FRED_API_BASE_URL}"
        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'limit': 1,
            'sort_order': 'desc'
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'observations' in data and len(data['observations']) > 0:
                latest = data['observations'][0]
                value = latest.get('value')
                if value and value != '.':
                    try:
                        return float(value), latest.get('date')
                    except (ValueError, TypeError):
                        return None, None
        return None, None
    except Exception as e:
        return None, None


def get_macro_data():
    """Fetch macroeconomic data from FRED API"""
    macro_data = {}
    
    # Check if API key is available
    if not FRED_API_KEY:
        return macro_data
    
    try:
        # Federal Funds Rate (Interest Rates)
        fed_rate, fed_date = get_fred_data('FEDFUNDS')
        if fed_rate is not None:
            macro_data['interest_rate'] = {
                'value': fed_rate,
                'date': fed_date,
                'label': 'Federal Funds Rate'
            }
        
        # Consumer Price Index (Inflation - YoY)
        # Get current and year-ago CPI
        cpi_current, cpi_date = get_fred_data('CPIAUCSL')
        if cpi_current is not None and cpi_date:
            try:
                # Try to get year-ago data
                year_ago_date = (datetime.strptime(cpi_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
                url = f"{FRED_API_BASE_URL}"
                params = {
                    'series_id': 'CPIAUCSL',
                    'api_key': FRED_API_KEY,
                    'file_type': 'json',
                    'observation_start': year_ago_date,
                    'limit': 1,
                    'sort_order': 'desc'
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) > 0:
                        cpi_year_ago = float(data['observations'][0].get('value', 0))
                        if cpi_year_ago > 0:
                            inflation_rate = ((cpi_current - cpi_year_ago) / cpi_year_ago) * 100
                            macro_data['inflation'] = {
                                'value': inflation_rate,
                                'date': cpi_date,
                                'label': 'CPI Inflation (YoY)'
                            }
            except Exception:
                pass
        
        # Unemployment Rate
        unemployment, unemp_date = get_fred_data('UNRATE')
        if unemployment is not None:
            macro_data['unemployment'] = {
                'value': unemployment,
                'date': unemp_date,
                'label': 'Unemployment Rate'
            }
        
        # GDP Growth Rate (Quarterly)
        gdp, gdp_date = get_fred_data('GDPC1')  # Real GDP
        if gdp is not None:
            macro_data['gdp'] = {
                'value': gdp,
                'date': gdp_date,
                'label': 'Real GDP'
            }
        
    except Exception as e:
        pass
    
    return macro_data


