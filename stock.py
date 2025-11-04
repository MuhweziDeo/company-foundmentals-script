#!/usr/bin/env python3
"""
Stock Fundamentals Analyzer
Collects company fundamental data using free APIs and displays it in the console.
Usage: python stock.py <TICKER>
"""

import sys
import argparse
from datetime import datetime
import yfinance as yf
import requests

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'


def get_financial_data(ticker):
    """Fetch financial data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get financial statements
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        # Get historical data for price metrics
        hist = stock.history(period="max")  # Get all available historical data
        
        return {
            'info': info,
            'financials': financials,
            'balance_sheet': balance_sheet,
            'cashflow': cashflow,
            'stock': stock,
            'history': hist
        }
    except Exception as e:
        print(f"{Colors.RED}Error fetching data: {e}{Colors.END}")
        return None


def get_macro_data():
    """Fetch macroeconomic data"""
    try:
        # Using free API for interest rates (FRED API is free but requires registration)
        # For demo purposes, we'll use a simple approach
        # Note: In production, you'd want to use FRED API or similar
        return {}
    except Exception as e:
        return {}


def format_number(value):
    """Format large numbers in readable format"""
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except:
        return str(value)


def format_percentage(value):
    """Format percentage values"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except:
        return str(value)


def format_percentage_colored(value):
    """Format percentage values with color (green for positive, red for negative)"""
    if value is None:
        return f"{Colors.WHITE}N/A{Colors.END}"
    try:
        val = float(value)
        color = Colors.GREEN if val >= 0 else Colors.RED
        sign = "+" if val >= 0 else ""
        return f"{color}{sign}{val:.2f}%{Colors.END}"
    except:
        return f"{Colors.WHITE}{str(value)}{Colors.END}"


def format_ratio(value):
    """Format ratio values"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except:
        return str(value)


def format_price(value):
    """Format price values"""
    if value is None:
        return "N/A"
    try:
        return f"${float(value):.2f}"
    except:
        return str(value)


def display_price_data(data):
    """Display current price, all-time high/low, and YTD performance"""
    info = data['info']
    history = data['history']
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}0. PRICE INFORMATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Current price
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    print(f"{Colors.BOLD}Current Price:{Colors.END} {Colors.YELLOW}{format_price(current_price)}{Colors.END}")
    
    # Get YTD data
    current_year = datetime.now().year
    ytd_start = f"{current_year}-01-01"
    
    ytd_percent_change = None
    ytd_high = None
    ytd_low = None
    ytd_high_date = None
    ytd_low_date = None
    
    if not history.empty:
        try:
            # Get price at start of year
            ytd_prices = history[history.index >= ytd_start]
            if not ytd_prices.empty:
                year_start_price = ytd_prices['Close'].iloc[0]
                current_price_val = float(current_price) if current_price else None
                if current_price_val and year_start_price:
                    ytd_percent_change = ((current_price_val - year_start_price) / year_start_price) * 100
                
                # Get YTD high and low
                ytd_high = ytd_prices['High'].max()
                ytd_low = ytd_prices['Low'].min()
                
                # Get dates for YTD high and low
                ytd_high_date = ytd_prices[ytd_prices['High'] == ytd_high].index[0]
                ytd_low_date = ytd_prices[ytd_prices['Low'] == ytd_low].index[0]
        except Exception as e:
            pass
    
    # Alternative: try to get from info
    if ytd_percent_change is None:
        # Try to get from ytdReturn if available
        ytd_return = info.get('ytdReturn')
        if ytd_return:
            ytd_percent_change = ytd_return * 100
    
    print(f"{Colors.BOLD}YTD % Change:{Colors.END} {format_percentage_colored(ytd_percent_change)}")
    
    # YTD High and Low
    print(f"{Colors.BOLD}YTD High ({current_year}):{Colors.END} {Colors.GREEN}{format_price(ytd_high)}{Colors.END}", end="")
    if ytd_high_date is not None:
        print(f" {Colors.WHITE}(on {ytd_high_date.strftime('%Y-%m-%d')}){Colors.END}")
    else:
        print()
    
    print(f"{Colors.BOLD}YTD Low ({current_year}):{Colors.END} {Colors.RED}{format_price(ytd_low)}{Colors.END}", end="")
    if ytd_low_date is not None:
        print(f" {Colors.WHITE}(on {ytd_low_date.strftime('%Y-%m-%d')}){Colors.END}")
    else:
        print()
    
    # All-time high and low
    all_time_high = None
    all_time_low = None
    all_time_high_date = None
    all_time_low_date = None
    
    if not history.empty:
        try:
            # Get all-time high and low from historical data
            all_time_high = history['High'].max()
            all_time_low = history['Low'].min()
            
            # Get dates for all-time high and low
            all_time_high_date = history[history['High'] == all_time_high].index[0]
            all_time_low_date = history[history['Low'] == all_time_low].index[0]
        except Exception as e:
            pass
    
    # Fallback to 52-week high/low if available
    if all_time_high is None:
        all_time_high = info.get('fiftyTwoWeekHigh')
    if all_time_low is None:
        all_time_low = info.get('fiftyTwoWeekLow')
    
    print(f"{Colors.BOLD}All-Time High:{Colors.END} {Colors.GREEN}{format_price(all_time_high)}{Colors.END}", end="")
    if all_time_high_date is not None:
        print(f" {Colors.WHITE}(on {all_time_high_date.strftime('%Y-%m-%d')}){Colors.END}")
    else:
        print()
    
    print(f"{Colors.BOLD}All-Time Low:{Colors.END} {Colors.RED}{format_price(all_time_low)}{Colors.END}", end="")
    if all_time_low_date is not None:
        print(f" {Colors.WHITE}(on {all_time_low_date.strftime('%Y-%m-%d')}){Colors.END}")
    else:
        print()
    
    # Calculate distance from all-time high/low
    if current_price and all_time_high:
        try:
            current_price_val = float(current_price)
            ath_val = float(all_time_high)
            distance_from_ath = ((current_price_val - ath_val) / ath_val) * 100
            print(f"{Colors.BOLD}Distance from All-Time High:{Colors.END} {format_percentage_colored(distance_from_ath)}")
        except:
            pass
    
    if current_price and all_time_low:
        try:
            current_price_val = float(current_price)
            atl_val = float(all_time_low)
            distance_from_atl = ((current_price_val - atl_val) / atl_val) * 100
            print(f"{Colors.BOLD}Distance from All-Time Low:{Colors.END} {format_percentage_colored(distance_from_atl)}")
        except:
            pass


def display_financial_data(data):
    """Display financial metrics"""
    info = data['info']
    financials = data['financials']
    balance_sheet = data['balance_sheet']
    cashflow = data['cashflow']
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}1. FINANCIAL METRICS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Revenue
    revenue = info.get('totalRevenue') or info.get('revenue')
    if revenue is None and not financials.empty:
        try:
            revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
        except:
            pass
    print(f"{Colors.BOLD}Revenue (Sales):{Colors.END} {Colors.GREEN}{format_number(revenue)}{Colors.END}")
    
    # Earnings / Net Income
    net_income = info.get('netIncomeToCommon') or info.get('netIncome')
    if net_income is None and not financials.empty:
        try:
            net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else None
        except:
            pass
    income_color = Colors.GREEN if (net_income and float(net_income) >= 0) else Colors.RED
    print(f"{Colors.BOLD}Earnings / Net Income:{Colors.END} {income_color}{format_number(net_income)}{Colors.END}")
    
    # Earnings Per Share (EPS)
    eps = info.get('trailingEps') or info.get('forwardEps')
    eps_color = Colors.GREEN if (eps and float(eps) >= 0) else Colors.RED
    print(f"{Colors.BOLD}Earnings Per Share (EPS):{Colors.END} {eps_color}{format_ratio(eps)}{Colors.END}")
    
    # Cash Flow
    operating_cashflow = info.get('operatingCashflow')
    if operating_cashflow is None and not cashflow.empty:
        try:
            operating_cashflow = cashflow.loc['Total Cash From Operating Activities'].iloc[0] if 'Total Cash From Operating Activities' in cashflow.index else None
        except:
            pass
    cashflow_color = Colors.GREEN if (operating_cashflow and float(operating_cashflow) >= 0) else Colors.RED
    print(f"{Colors.BOLD}Cash Flow (Operating):{Colors.END} {cashflow_color}{format_number(operating_cashflow)}{Colors.END}")
    
    # Debt-to-Equity Ratio
    debt_to_equity = info.get('debtToEquity')
    print(f"{Colors.BOLD}Debt-to-Equity Ratio:{Colors.END} {Colors.YELLOW}{format_ratio(debt_to_equity)}{Colors.END}")
    
    # Return on Equity (ROE)
    roe = info.get('returnOnEquity')
    if roe:
        roe = roe * 100
    roe_color = Colors.GREEN if (roe and float(roe) >= 0) else Colors.RED
    print(f"{Colors.BOLD}Return on Equity (ROE):{Colors.END} {roe_color}{format_percentage(roe)}{Colors.END}")
    
    # Gross Margin
    gross_margin = info.get('grossMargins')
    if gross_margin:
        gross_margin = gross_margin * 100
    print(f"{Colors.BOLD}Gross Margin:{Colors.END} {Colors.GREEN}{format_percentage(gross_margin)}{Colors.END}")
    
    # Net Margin
    net_margin = info.get('profitMargins')
    if net_margin:
        net_margin = net_margin * 100
    margin_color = Colors.GREEN if (net_margin and float(net_margin) >= 0) else Colors.RED
    print(f"{Colors.BOLD}Net Margin:{Colors.END} {margin_color}{format_percentage(net_margin)}{Colors.END}")


def display_valuation_data(data):
    """Display valuation metrics"""
    info = data['info']
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}2. VALUATION METRICS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # P/E Ratio
    pe_ratio = info.get('trailingPE') or info.get('forwardPE')
    print(f"{Colors.BOLD}P/E (Price-to-Earnings):{Colors.END} {Colors.YELLOW}{format_ratio(pe_ratio)}{Colors.END}")
    
    # P/B Ratio
    pb_ratio = info.get('priceToBook')
    print(f"{Colors.BOLD}P/B (Price-to-Book):{Colors.END} {Colors.YELLOW}{format_ratio(pb_ratio)}{Colors.END}")
    
    # P/S Ratio
    ps_ratio = info.get('priceToSalesTrailing12Months')
    print(f"{Colors.BOLD}P/S (Price-to-Sales):{Colors.END} {Colors.YELLOW}{format_ratio(ps_ratio)}{Colors.END}")
    
    # EV/EBITDA
    ev_ebitda = info.get('enterpriseToEbitda')
    print(f"{Colors.BOLD}EV/EBITDA:{Colors.END} {Colors.YELLOW}{format_ratio(ev_ebitda)}{Colors.END}")


def display_operation_data(data):
    """Display operational metrics"""
    info = data['info']
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}3. OPERATIONAL METRICS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Market share - not directly available, show market cap as proxy
    market_cap = info.get('marketCap')
    print(f"{Colors.BOLD}Market Capitalization:{Colors.END} {Colors.GREEN}{format_number(market_cap)}{Colors.END}")
    print(f"{Colors.BOLD}Market Share:{Colors.END} {Colors.WHITE}N/A (requires industry-specific data){Colors.END}")
    
    # Business model - description
    business_summary = info.get('longBusinessSummary') or info.get('businessSummary')
    if business_summary:
        print(f"\n{Colors.BOLD}Business Model / Summary:{Colors.END}")
        # Truncate if too long
        summary = business_summary[:500] + "..." if len(business_summary) > 500 else business_summary
        print(f"  {Colors.WHITE}{summary}{Colors.END}")
    else:
        print(f"{Colors.BOLD}Business Model:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Competitive advantage - not directly available
    print(f"{Colors.BOLD}Competitive Advantage (Moat):{Colors.END} {Colors.WHITE}N/A (qualitative analysis required){Colors.END}")
    
    # Management quality - not directly available
    print(f"{Colors.BOLD}Management Quality:{Colors.END} {Colors.WHITE}N/A (qualitative analysis required){Colors.END}")
    
    # Product diversification - sector and industry
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    print(f"{Colors.BOLD}Sector:{Colors.END} {Colors.CYAN}{sector}{Colors.END}")
    print(f"{Colors.BOLD}Industry:{Colors.END} {Colors.CYAN}{industry}{Colors.END}")
    
    # Number of employees as proxy for diversification
    employees = info.get('fullTimeEmployees')
    if employees:
        print(f"{Colors.BOLD}Full-Time Employees:{Colors.END} {Colors.YELLOW}{employees:,}{Colors.END}")


def display_macro_sector_data(data):
    """Display macroeconomic and sector data"""
    info = data['info']
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}4. MACROECONOMIC AND SECTOR METRICS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Interest rates - not directly available from stock data
    print(f"{Colors.BOLD}Interest Rates:{Colors.END} {Colors.WHITE}N/A (requires external macro data API){Colors.END}")
    
    # Inflation - not directly available
    print(f"{Colors.BOLD}Inflation:{Colors.END} {Colors.WHITE}N/A (requires external macro data API){Colors.END}")
    
    # Consumer demand - use revenue growth as proxy
    revenue_growth = info.get('revenueGrowth')
    if revenue_growth:
        revenue_growth = revenue_growth * 100
    print(f"{Colors.BOLD}Revenue Growth (Demand Proxy):{Colors.END} {format_percentage_colored(revenue_growth)}")
    
    # Commodity prices - not directly available
    print(f"{Colors.BOLD}Commodity Prices:{Colors.END} {Colors.WHITE}N/A (requires commodity-specific data){Colors.END}")
    
    # Regulations / taxes - not directly available
    print(f"{Colors.BOLD}Regulations / Taxes:{Colors.END} {Colors.WHITE}N/A (requires regulatory research){Colors.END}")
    
    # Industry growth trends - use earnings growth as proxy
    earnings_growth = info.get('earningsGrowth')
    if earnings_growth:
        earnings_growth = earnings_growth * 100
    print(f"{Colors.BOLD}Earnings Growth (Industry Trend Proxy):{Colors.END} {format_percentage_colored(earnings_growth)}")
    
    # Additional sector info
    beta = info.get('beta')
    print(f"{Colors.BOLD}Beta (Market Correlation):{Colors.END} {Colors.YELLOW}{format_ratio(beta)}{Colors.END}")


def main():
    parser = argparse.ArgumentParser(
        description='Stock Fundamentals Analyzer - Collects company fundamental data'
    )
    parser.add_argument('ticker', type=str.upper, help='Stock ticker symbol (e.g., AAPL, MSFT)')
    
    args = parser.parse_args()
    ticker = args.ticker
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}STOCK FUNDAMENTALS ANALYSIS FOR: {Colors.YELLOW}{ticker}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.WHITE}Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Fetch data
    print(f"\n{Colors.YELLOW}Fetching data for {ticker}...{Colors.END}")
    data = get_financial_data(ticker)
    
    if data is None:
        print(f"\n{Colors.RED}{Colors.BOLD}Error: Could not fetch data for ticker {ticker}{Colors.END}")
        print(f"{Colors.RED}Please verify the ticker symbol is correct.{Colors.END}")
        sys.exit(1)
    
    # Display all sections
    display_price_data(data)
    display_financial_data(data)
    display_valuation_data(data)
    display_operation_data(data)
    display_macro_sector_data(data)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}Analysis Complete{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}\n")
    
    # Note about data availability
    print(f"{Colors.YELLOW}Note: Some metrics (marked as N/A) require:{Colors.END}")
    print(f"{Colors.WHITE}  - Qualitative analysis (business model, competitive advantage, management){Colors.END}")
    print(f"{Colors.WHITE}  - External macroeconomic data APIs (interest rates, inflation){Colors.END}")
    print(f"{Colors.WHITE}  - Industry-specific research (market share, regulations){Colors.END}")
    print()


if __name__ == "__main__":
    main()

