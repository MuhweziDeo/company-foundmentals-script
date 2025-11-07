"""
Display functions for stock analysis output
"""

from datetime import datetime
from .constants import Colors, FRED_API_KEY
from .formatters import (
    format_number,
    format_percentage,
    format_percentage_colored,
    format_ratio,
    format_price
)
from .calculators import (
    calculate_rsi,
    get_rsi_signal,
    get_earnings_trend,
    get_analyst_ratings,
    analyze_price_action_trend,
    identify_swing_points,
    generate_trading_recommendation
)
from .data_fetcher import get_macro_data

def display_analyst_ratings(data):
    """Display analyst ratings and price targets"""
    info = data['info']
    recommendations = data.get('recommendations')
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}6. ANALYST RATINGS & PRICE TARGETS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    analyst_data = get_analyst_ratings(info, recommendations, current_price)
    
    # Average Price Target
    if analyst_data['average_target']:
        avg_target = analyst_data['average_target']
        print(f"\n{Colors.BOLD}Average Price Target:{Colors.END} {Colors.YELLOW}{format_price(avg_target)}{Colors.END}")
        
        # Upside/Downside
        if 'upside_downside' in analyst_data:
            ud = analyst_data['upside_downside']
            ud_color = Colors.GREEN if ud > 0 else Colors.RED if ud < 0 else Colors.YELLOW
            direction = "↑ Upside" if ud > 0 else "↓ Downside" if ud < 0 else "→ Neutral"
            print(f"{Colors.BOLD}Price Target vs Current:{Colors.END} {ud_color}{direction} ({ud:+.2f}%){Colors.END}")
        
        # High and Low targets
        if analyst_data['high_target']:
            print(f"{Colors.BOLD}High Target:{Colors.END} {Colors.GREEN}{format_price(analyst_data['high_target'])}{Colors.END}")
        if analyst_data['low_target']:
            print(f"{Colors.BOLD}Low Target:{Colors.END} {Colors.RED}{format_price(analyst_data['low_target'])}{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}Average Price Target:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Recommendation Summary
    if analyst_data['recommendation']:
        rec = analyst_data['recommendation']
        # Recommendation values: 1=Strong Buy, 2=Buy, 3=Hold, 4=Underperform, 5=Sell
        if isinstance(rec, (int, float)):
            rec_labels = {1: "Strong Buy", 2: "Buy", 3: "Hold", 4: "Underperform", 5: "Sell"}
            rec_label = rec_labels.get(int(rec), f"{rec:.1f}")
            rec_color = Colors.GREEN if rec <= 2 else Colors.YELLOW if rec <= 3 else Colors.RED
            print(f"{Colors.BOLD}Average Recommendation:{Colors.END} {rec_color}{rec_label}{Colors.END}")
        else:
            print(f"{Colors.BOLD}Average Recommendation:{Colors.END} {Colors.YELLOW}{rec}{Colors.END}")
    
    # Recommendation Breakdown
    if analyst_data['recommendation_breakdown']:
        breakdown = analyst_data['recommendation_breakdown']
        print(f"\n{Colors.BOLD}Recommendation Breakdown:{Colors.END}")
        for rec_type, count in breakdown.items():
            if count and count > 0:
                rec_color = Colors.GREEN if 'buy' in rec_type.lower() else Colors.RED if 'sell' in rec_type.lower() else Colors.YELLOW
                print(f"  {rec_color}{rec_type}: {int(count)}{Colors.END}")
    
    # List Recent Analysts
    if analyst_data['analysts']:
        print(f"\n{Colors.BOLD}Recent Analyst Recommendations:{Colors.END}")
        print(f"{Colors.WHITE}{'Firm':<30} {'Rating':<20} {'Date'}{Colors.END}")
        print(f"{Colors.WHITE}{'-' * 80}{Colors.END}")
        
        # Show last 10 analysts
        for analyst in analyst_data['analysts'][:10]:
            firm = analyst['firm'][:28] if len(analyst['firm']) > 28 else analyst['firm']
            rating = analyst['rating']
            date = analyst['date'][:10] if len(analyst['date']) > 10 else analyst['date']
            
            # Color code rating
            rating_lower = str(rating).lower()
            rating_color = Colors.GREEN if 'buy' in rating_lower or 'strong' in rating_lower else Colors.RED if 'sell' in rating_lower else Colors.YELLOW
            
            print(f"{Colors.WHITE}{firm:<30}{Colors.END} {rating_color}{rating:<20}{Colors.END} {Colors.WHITE}{date}{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}Recent Analyst Recommendations:{Colors.END} {Colors.WHITE}N/A (data unavailable){Colors.END}")


def display_earnings_trend(data):
    """Display earnings trend over time"""
    financials = data.get('financials')
    quarterly_financials = data.get('quarterly_financials')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}5. EARNINGS TREND{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    earnings_trend = get_earnings_trend(financials, quarterly_financials)
    
    if not earnings_trend:
        print(f"{Colors.WHITE}Earnings trend data not available{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Period{' ' * 20}Earnings{' ' * 15}Change{Colors.END}")
    print(f"{Colors.WHITE}{'-' * 80}{Colors.END}")
    
    for i, period in enumerate(earnings_trend):
        date_str = period['date']
        earnings = period['earnings']
        period_type = period['period']
        
        # Calculate change from previous period
        change_str = ""
        change_color = Colors.WHITE
        if i < len(earnings_trend) - 1:
            prev_earnings = earnings_trend[i + 1]['earnings']
            if prev_earnings != 0:
                change = ((earnings - prev_earnings) / abs(prev_earnings)) * 100
                change_color = Colors.GREEN if change >= 0 else Colors.RED
                sign = "+" if change >= 0 else ""
                change_str = f"{sign}{change:.2f}%"
            else:
                change_str = "N/A"
        
        earnings_color = Colors.GREEN if earnings >= 0 else Colors.RED
        earnings_formatted = format_number(earnings)
        
        # Format date nicely
        date_display = date_str[:10] if len(date_str) > 10 else date_str
        
        print(f"{Colors.WHITE}{date_display} ({period_type}){' ' * (20 - len(date_display) - len(period_type) - 2)}{earnings_color}{earnings_formatted}{' ' * (25 - len(earnings_formatted))}{change_color}{change_str}{Colors.END}")
    
    # Calculate overall trend
    if len(earnings_trend) >= 2:
        first_earnings = earnings_trend[-1]['earnings']
        latest_earnings = earnings_trend[0]['earnings']
        
        if first_earnings != 0:
            overall_change = ((latest_earnings - first_earnings) / abs(first_earnings)) * 100
            trend_color = Colors.GREEN if overall_change >= 0 else Colors.RED
            trend_direction = "↑ Increasing" if overall_change > 0 else "↓ Decreasing" if overall_change < 0 else "→ Stable"
            
            print(f"\n{Colors.BOLD}Overall Trend:{Colors.END} {trend_color}{trend_direction} ({overall_change:+.2f}%){Colors.END}")


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


def display_macro_sector_data(data):
    """Display macroeconomic and sector data"""
    info = data['info']
    
    # Fetch macro data from FRED API (only if API key is available)
    macro_data = {}
    if FRED_API_KEY:
        print(f"{Colors.YELLOW}Fetching macroeconomic data from FRED API...{Colors.END}")
        macro_data = get_macro_data()
    else:
        print(f"{Colors.YELLOW}Note: FRED API key not set. Macroeconomic data will not be fetched.{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}4. MACROECONOMIC AND SECTOR METRICS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Interest rates from FRED
    if 'interest_rate' in macro_data:
        ir_data = macro_data['interest_rate']
        print(f"{Colors.BOLD}Interest Rate ({ir_data['label']}):{Colors.END} {Colors.YELLOW}{ir_data['value']:.2f}%{Colors.END} (as of {ir_data['date']})")
    else:
        print(f"{Colors.BOLD}Interest Rate:{Colors.END} {Colors.WHITE}N/A (data unavailable){Colors.END}")
    
    # Inflation from FRED
    if 'inflation' in macro_data:
        inf_data = macro_data['inflation']
        inflation_color = Colors.RED if inf_data['value'] > 3 else Colors.GREEN if inf_data['value'] < 2 else Colors.YELLOW
        print(f"{Colors.BOLD}Inflation ({inf_data['label']}):{Colors.END} {inflation_color}{inf_data['value']:.2f}%{Colors.END} (as of {inf_data['date']})")
    else:
        print(f"{Colors.BOLD}Inflation:{Colors.END} {Colors.WHITE}N/A (data unavailable){Colors.END}")
    
    # Unemployment Rate
    if 'unemployment' in macro_data:
        unemp_data = macro_data['unemployment']
        print(f"{Colors.BOLD}Unemployment Rate:{Colors.END} {Colors.YELLOW}{unemp_data['value']:.2f}%{Colors.END} (as of {unemp_data['date']})")
    else:
        print(f"{Colors.BOLD}Unemployment Rate:{Colors.END} {Colors.WHITE}N/A (data unavailable){Colors.END}")
    
    # GDP
    if 'gdp' in macro_data:
        gdp_data = macro_data['gdp']
        print(f"{Colors.BOLD}Real GDP:{Colors.END} {Colors.GREEN}${gdp_data['value']:.2f}B{Colors.END} (as of {gdp_data['date']})")
    
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
    
    # Store macro data for export
    data['macro_data'] = macro_data


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


def display_price_data(data):
    """Display current price, all-time high/low, and YTD performance"""
    info = data['info']
    history = data['history']
    next_earnings_date = data.get('next_earnings_date')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}0. PRICE INFORMATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Current price
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    print(f"{Colors.BOLD}Current Price:{Colors.END} {Colors.YELLOW}{format_price(current_price)}{Colors.END}")
    
    # Calculate and display RSI
    rsi = None
    if not history.empty:
        try:
            # Get recent price data (last 30 days for RSI calculation)
            recent_prices = history['Close'].tail(30)
            if len(recent_prices) >= 15:  # Need at least 15 days for 14-period RSI
                rsi = calculate_rsi(recent_prices, period=14)
        except Exception:
            pass
    
    if rsi is not None:
        signal, signal_color = get_rsi_signal(rsi)
        rsi_color = Colors.RED if rsi >= 70 else Colors.GREEN if rsi <= 30 else Colors.YELLOW
        print(f"{Colors.BOLD}RSI (14-day):{Colors.END} {rsi_color}{format_ratio(rsi)}{Colors.END} {signal_color}({signal}){Colors.END}")
    else:
        print(f"{Colors.BOLD}RSI (14-day):{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Next earnings date
    if next_earnings_date:
        try:
            # Format the date
            if hasattr(next_earnings_date, 'strftime'):
                earnings_date_str = next_earnings_date.strftime('%Y-%m-%d')
            elif isinstance(next_earnings_date, (list, tuple)) and len(next_earnings_date) > 0:
                earnings_date_str = str(next_earnings_date[0])
            else:
                earnings_date_str = str(next_earnings_date)
            
            # Calculate days until earnings
            try:
                if hasattr(next_earnings_date, 'strftime'):
                    earnings_date = next_earnings_date
                else:
                    from datetime import datetime as dt
                    earnings_date = dt.strptime(earnings_date_str, '%Y-%m-%d')
                
                days_until = (earnings_date.date() - datetime.now().date()).days if hasattr(earnings_date, 'date') else None
                days_str = f" ({days_until} days)" if days_until is not None and days_until >= 0 else ""
            except:
                days_str = ""
            
            print(f"{Colors.BOLD}Next Earnings Date:{Colors.END} {Colors.CYAN}{earnings_date_str}{days_str}{Colors.END}")
        except Exception:
            print(f"{Colors.BOLD}Next Earnings Date:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    else:
        print(f"{Colors.BOLD}Next Earnings Date:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
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


def display_price_action_trend(data):
    """Display price action trend analysis and swing structures on 1-day timeframe"""
    history = data.get('history')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}7. PRICE ACTION TREND & SWING STRUCTURES (1D Timeframe){Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    if history is None or history.empty:
        print(f"{Colors.WHITE}Price action data not available{Colors.END}")
        return
    
    # Analyze price action trend
    trend_data = analyze_price_action_trend(history)
    
    # Display trend
    trend = trend_data['trend']
    trend_strength = trend_data['trend_strength']
    description = trend_data['description']
    
    # Color code the trend
    if trend == 'UPTREND':
        trend_color = Colors.GREEN
        trend_symbol = "↑"
    elif trend == 'DOWNTREND':
        trend_color = Colors.RED
        trend_symbol = "↓"
    elif trend == 'SIDEWAYS':
        trend_color = Colors.YELLOW
        trend_symbol = "→"
    else:
        trend_color = Colors.WHITE
        trend_symbol = "?"
    
    print(f"\n{Colors.BOLD}Price Action Trend:{Colors.END} {trend_color}{trend_symbol} {trend}{Colors.END}")
    if trend_strength is not None:
        print(f"{Colors.BOLD}Trend Strength:{Colors.END} {trend_color}{trend_strength:.1%}{Colors.END}")
    print(f"{Colors.BOLD}Analysis:{Colors.END} {Colors.WHITE}{description}{Colors.END}")
    
    # Display swing structures
    swing_highs = trend_data['swing_highs']
    swing_lows = trend_data['swing_lows']
    
    # Display current swing high and low prices prominently
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}Current Swing Points:{Colors.END}")
    
    if swing_highs and len(swing_highs) > 0:
        current_swing_high = swing_highs[0]
        current_high_price = format_price(current_swing_high['price'])
        current_high_date = current_swing_high['date'][:10] if len(current_swing_high['date']) > 10 else current_swing_high['date']
        print(f"{Colors.BOLD}Current Swing High:{Colors.END} {Colors.GREEN}{current_high_price}{Colors.END} {Colors.WHITE}(on {current_high_date}){Colors.END}")
    else:
        print(f"{Colors.BOLD}Current Swing High:{Colors.END} {Colors.WHITE}N/A (insufficient data){Colors.END}")
    
    if swing_lows and len(swing_lows) > 0:
        current_swing_low = swing_lows[0]
        current_low_price = format_price(current_swing_low['price'])
        current_low_date = current_swing_low['date'][:10] if len(current_swing_low['date']) > 10 else current_swing_low['date']
        print(f"{Colors.BOLD}Current Swing Low:{Colors.END} {Colors.RED}{current_low_price}{Colors.END} {Colors.WHITE}(on {current_low_date}){Colors.END}")
    else:
        print(f"{Colors.BOLD}Current Swing Low:{Colors.END} {Colors.WHITE}N/A (insufficient data){Colors.END}")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Swing Structures (1-Day Timeframe):{Colors.END}")
    
    # Display swing highs
    if swing_highs:
        print(f"\n{Colors.BOLD}Recent Swing Highs:{Colors.END}")
        print(f"{Colors.WHITE}{'Date':<15} {'Price':<15} {'Status'}{Colors.END}")
        print(f"{Colors.WHITE}{'-' * 50}{Colors.END}")
        
        for i, swing in enumerate(swing_highs[:5]):  # Show last 5
            date_str = swing['date'][:10] if len(swing['date']) > 10 else swing['date']
            price = format_price(swing['price'])
            
            # Compare with previous swing high to show if higher/lower
            status = ""
            if i < len(swing_highs) - 1:
                prev_price = swing_highs[i + 1]['price']
                if swing['price'] > prev_price:
                    status = f"{Colors.GREEN}↑ Higher{Colors.END}"
                elif swing['price'] < prev_price:
                    status = f"{Colors.RED}↓ Lower{Colors.END}"
                else:
                    status = f"{Colors.YELLOW}→ Equal{Colors.END}"
            else:
                status = f"{Colors.WHITE}N/A{Colors.END}"
            
            print(f"{Colors.WHITE}{date_str:<15}{Colors.END} {Colors.GREEN}{price:<15}{Colors.END} {status}")
    else:
        print(f"\n{Colors.BOLD}Recent Swing Highs:{Colors.END} {Colors.WHITE}N/A (insufficient data){Colors.END}")
    
    # Display swing lows
    if swing_lows:
        print(f"\n{Colors.BOLD}Recent Swing Lows:{Colors.END}")
        print(f"{Colors.WHITE}{'Date':<15} {'Price':<15} {'Status'}{Colors.END}")
        print(f"{Colors.WHITE}{'-' * 50}{Colors.END}")
        
        for i, swing in enumerate(swing_lows[:5]):  # Show last 5
            date_str = swing['date'][:10] if len(swing['date']) > 10 else swing['date']
            price = format_price(swing['price'])
            
            # Compare with previous swing low to show if higher/lower
            status = ""
            if i < len(swing_lows) - 1:
                prev_price = swing_lows[i + 1]['price']
                if swing['price'] > prev_price:
                    status = f"{Colors.GREEN}↑ Higher{Colors.END}"
                elif swing['price'] < prev_price:
                    status = f"{Colors.RED}↓ Lower{Colors.END}"
                else:
                    status = f"{Colors.YELLOW}→ Equal{Colors.END}"
            else:
                status = f"{Colors.WHITE}N/A{Colors.END}"
            
            print(f"{Colors.WHITE}{date_str:<15}{Colors.END} {Colors.RED}{price:<15}{Colors.END} {status}")
    else:
        print(f"\n{Colors.BOLD}Recent Swing Lows:{Colors.END} {Colors.WHITE}N/A (insufficient data){Colors.END}")
    
    # Summary of swing structure pattern
    if swing_highs and swing_lows and len(swing_highs) >= 2 and len(swing_lows) >= 2:
        print(f"\n{Colors.BOLD}Swing Structure Pattern:{Colors.END}")
        
        # Check if we have higher highs
        has_higher_highs = len(swing_highs) >= 2 and swing_highs[0]['price'] > swing_highs[1]['price']
        has_lower_highs = len(swing_highs) >= 2 and swing_highs[0]['price'] < swing_highs[1]['price']
        has_higher_lows = len(swing_lows) >= 2 and swing_lows[0]['price'] > swing_lows[1]['price']
        has_lower_lows = len(swing_lows) >= 2 and swing_lows[0]['price'] < swing_lows[1]['price']
        
        if has_higher_highs and has_higher_lows:
            print(f"  {Colors.GREEN}✓ Higher Highs and Higher Lows (Classic Uptrend){Colors.END}")
        elif has_lower_highs and has_lower_lows:
            print(f"  {Colors.RED}✓ Lower Highs and Lower Lows (Classic Downtrend){Colors.END}")
        elif has_higher_highs and has_lower_lows:
            print(f"  {Colors.YELLOW}⚠ Higher Highs but Lower Lows (Potential Reversal){Colors.END}")
        elif has_lower_highs and has_higher_lows:
            print(f"  {Colors.YELLOW}⚠ Lower Highs but Higher Lows (Potential Reversal){Colors.END}")
        else:
            print(f"  {Colors.WHITE}→ Mixed pattern (Consolidation){Colors.END}")


def display_trading_recommendation(data):
    """Display comprehensive buy/sell/hold recommendation based on multiple indicators"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}8. TRADING RECOMMENDATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    # Generate recommendation
    rec_data = generate_trading_recommendation(data)
    
    recommendation = rec_data['recommendation']
    recommendation_color = rec_data['recommendation_color']
    recommendation_symbol = rec_data['recommendation_symbol']
    total_score = rec_data['total_score']
    scores = rec_data['scores']
    reasons = rec_data['reasons']
    summary_reason = rec_data['summary_reason']
    
    # Display the main recommendation prominently
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}RECOMMENDATION: {recommendation_color}{recommendation_symbol} {recommendation}{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}")
    
    # Display summary reason
    print(f"\n{Colors.BOLD}Summary:{Colors.END} {Colors.WHITE}{summary_reason}{Colors.END}")
    
    # Display score breakdown
    print(f"\n{Colors.BOLD}Indicator Scores:{Colors.END}")
    print(f"{Colors.WHITE}{'-' * 50}{Colors.END}")
    
    # Price Action Score
    pa_score = scores['price_action']
    pa_color = Colors.GREEN if pa_score > 0 else Colors.RED if pa_score < 0 else Colors.YELLOW
    pa_sign = "+" if pa_score > 0 else ""
    print(f"{Colors.BOLD}Price Action Trend:{Colors.END} {pa_color}{pa_sign}{pa_score:+d}{Colors.END}")
    
    # Analyst Rating Score
    ar_score = scores['analyst_rating']
    ar_color = Colors.GREEN if ar_score > 0 else Colors.RED if ar_score < 0 else Colors.YELLOW
    ar_sign = "+" if ar_score > 0 else ""
    print(f"{Colors.BOLD}Analyst Ratings:{Colors.END} {ar_color}{ar_sign}{ar_score:+d}{Colors.END}")
    
    # RSI Score
    rsi_score = scores['rsi']
    rsi_color = Colors.GREEN if rsi_score > 0 else Colors.RED if rsi_score < 0 else Colors.YELLOW
    rsi_sign = "+" if rsi_score > 0 else ""
    print(f"{Colors.BOLD}RSI Indicator:{Colors.END} {rsi_color}{rsi_sign}{rsi_score:+d}{Colors.END}")
    
    # Zacks Recommendation Score
    zacks_score = scores.get('zacks', 0)
    zacks_color = Colors.GREEN if zacks_score > 0 else Colors.RED if zacks_score < 0 else Colors.YELLOW
    zacks_sign = "+" if zacks_score > 0 else ""
    print(f"{Colors.BOLD}Zacks Recommendation:{Colors.END} {zacks_color}{zacks_sign}{zacks_score:+d}{Colors.END}")
    
    print(f"{Colors.WHITE}{'-' * 50}{Colors.END}")
    
    # Calculate maximum possible score (all indicators at maximum bullish)
    # Price Action: +2, Analyst: +2, RSI: +2, Zacks: +2 = 8 max
    # Minimum possible score (all indicators at maximum bearish)
    # Price Action: -2, Analyst: -2, RSI: -2, Zacks: -2 = -8 min
    max_possible_score = 8  # All indicators bullish
    min_possible_score = -8  # All indicators bearish
    
    total_color = Colors.GREEN if total_score > 0 else Colors.RED if total_score < 0 else Colors.YELLOW
    total_sign = "+" if total_score > 0 else ""
    print(f"{Colors.BOLD}Total Score / Overall Score:{Colors.END} {total_color}{total_sign}{total_score:+d}{Colors.END} / {Colors.WHITE}{max_possible_score:+d}{Colors.END} (Range: {min_possible_score:+d} to {max_possible_score:+d})")
    
    # Display detailed reasons
    if reasons:
        print(f"\n{Colors.BOLD}Detailed Analysis:{Colors.END}")
        for i, reason in enumerate(reasons, 1):
            print(f"  {Colors.WHITE}{i}. {reason}{Colors.END}")
    
    # Display individual indicator values for reference
    print(f"\n{Colors.BOLD}Indicator Values:{Colors.END}")
    
    # RSI Value
    rsi_value = rec_data.get('rsi_value')
    if rsi_value is not None:
        rsi_signal, rsi_signal_color = get_rsi_signal(rsi_value)
        rsi_display_color = Colors.RED if rsi_value >= 70 else Colors.GREEN if rsi_value <= 30 else Colors.YELLOW
        print(f"  {Colors.BOLD}RSI:{Colors.END} {rsi_display_color}{rsi_value:.1f}{Colors.END} {rsi_signal_color}({rsi_signal}){Colors.END}")
    else:
        print(f"  {Colors.BOLD}RSI:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Price Action Trend
    price_action_trend = rec_data.get('price_action_trend', 'UNKNOWN')
    if price_action_trend != 'UNKNOWN':
        trend_color = Colors.GREEN if price_action_trend == 'UPTREND' else Colors.RED if price_action_trend == 'DOWNTREND' else Colors.YELLOW
        print(f"  {Colors.BOLD}Price Action Trend:{Colors.END} {trend_color}{price_action_trend}{Colors.END}")
    else:
        print(f"  {Colors.BOLD}Price Action Trend:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Analyst Recommendation
    analyst_rec = rec_data.get('analyst_recommendation')
    if analyst_rec:
        if isinstance(analyst_rec, (int, float)):
            rec_labels = {1: "Strong Buy", 2: "Buy", 3: "Hold", 4: "Underperform", 5: "Sell"}
            rec_label = rec_labels.get(int(analyst_rec), f"{analyst_rec:.1f}")
            rec_color = Colors.GREEN if analyst_rec <= 2 else Colors.YELLOW if analyst_rec <= 3 else Colors.RED
            print(f"  {Colors.BOLD}Analyst Consensus:{Colors.END} {rec_color}{rec_label}{Colors.END}")
        else:
            print(f"  {Colors.BOLD}Analyst Consensus:{Colors.END} {Colors.YELLOW}{analyst_rec}{Colors.END}")
    else:
        print(f"  {Colors.BOLD}Analyst Consensus:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Zacks Recommendation
    zacks_rec = rec_data.get('zacks_recommendation')
    zacks_rank = rec_data.get('zacks_rank')
    if zacks_rec:
        rec_lower = str(zacks_rec).lower()
        if 'strong buy' in rec_lower or rec_lower == 'buy':
            zacks_color = Colors.GREEN
        elif 'strong sell' in rec_lower or rec_lower == 'sell':
            zacks_color = Colors.RED
        else:
            zacks_color = Colors.YELLOW
        rank_text = f" (Rank {zacks_rank})" if zacks_rank else ""
        print(f"  {Colors.BOLD}Zacks Recommendation:{Colors.END} {zacks_color}{zacks_rec}{rank_text}{Colors.END}")
    elif zacks_rank:
        rank_labels = {1: "Strong Buy", 2: "Buy", 3: "Hold", 4: "Sell", 5: "Strong Sell"}
        rank_label = rank_labels.get(zacks_rank, f"Rank {zacks_rank}")
        zacks_color = Colors.GREEN if zacks_rank <= 2 else Colors.YELLOW if zacks_rank == 3 else Colors.RED
        print(f"  {Colors.BOLD}Zacks Recommendation:{Colors.END} {zacks_color}{rank_label} (Rank {zacks_rank}){Colors.END}")
    else:
        print(f"  {Colors.BOLD}Zacks Recommendation:{Colors.END} {Colors.WHITE}N/A{Colors.END}")
    
    # Risk Disclaimer
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Disclaimer:{Colors.END} This recommendation is based on technical analysis and should not be the sole basis for investment decisions. Always conduct your own research and consider your risk tolerance.{Colors.END}")


def display_zacks_recommendation(data):
    """Display Zacks.com recommendation summary"""
    zacks_data = data.get('zacks_data')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}9. ZACKS.COM RECOMMENDATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    
    if not zacks_data:
        print(f"\n{Colors.WHITE}Zacks.com recommendation data not available.{Colors.END}")
        print(f"{Colors.WHITE}This may be due to:{Colors.END}")
        print(f"{Colors.WHITE}  - Stock not found on Zacks.com{Colors.END}")
        print(f"{Colors.WHITE}  - Website structure changes{Colors.END}")
        print(f"{Colors.WHITE}  - Network connectivity issues{Colors.END}")
        return
    
    recommendation = zacks_data.get('recommendation')
    rank = zacks_data.get('rank')
    style_scores = zacks_data.get('style_scores', {})
    url = zacks_data.get('url', '')
    
    # Display recommendation
    if recommendation:
        # Color code the recommendation
        rec_lower = recommendation.lower()
        if 'strong buy' in rec_lower or rec_lower == 'buy':
            rec_color = Colors.GREEN
            rec_symbol = "↑"
        elif 'strong sell' in rec_lower or rec_lower == 'sell':
            rec_color = Colors.RED
            rec_symbol = "↓"
        else:
            rec_color = Colors.YELLOW
            rec_symbol = "→"
        
        print(f"\n{Colors.BOLD}Zacks Recommendation:{Colors.END} {rec_color}{rec_symbol} {recommendation}{Colors.END}")
        
        # Display rank if available
        if rank:
            rank_labels = {1: 'Strong Buy', 2: 'Buy', 3: 'Hold', 4: 'Sell', 5: 'Strong Sell'}
            rank_label = rank_labels.get(rank, f'Rank {rank}')
            rank_color = Colors.GREEN if rank <= 2 else Colors.RED if rank >= 4 else Colors.YELLOW
            print(f"{Colors.BOLD}Zacks Rank:{Colors.END} {rank_color}{rank} ({rank_label}){Colors.END}")
            print(f"{Colors.WHITE}Note: Zacks Rank 1 = Strong Buy, 2 = Buy, 3 = Hold, 4 = Sell, 5 = Strong Sell{Colors.END}")
        
        # Display style scores if available
        if style_scores:
            print(f"\n{Colors.BOLD}Style Scores:{Colors.END}")
            
            # Helper function to get color for grade
            def get_grade_color(grade):
                if isinstance(grade, str):
                    grade_upper = grade.upper()
                    if grade_upper == 'A':
                        return Colors.GREEN
                    elif grade_upper == 'B':
                        return Colors.GREEN
                    elif grade_upper == 'C':
                        return Colors.YELLOW
                    elif grade_upper == 'D':
                        return Colors.YELLOW
                    else:  # F
                        return Colors.RED
                else:  # numeric score
                    return Colors.GREEN if grade >= 4 else Colors.YELLOW if grade >= 2 else Colors.RED
            
            if 'value' in style_scores or 'value_grade' in style_scores:
                value_grade = style_scores.get('value_grade') or (style_scores.get('value') and ['F', 'D', 'C', 'B', 'A'][style_scores['value'] - 1] if style_scores.get('value') else None)
                value_score = style_scores.get('value', 0)
                if value_grade:
                    value_color = get_grade_color(value_grade)
                    print(f"  {Colors.BOLD}Value:{Colors.END} {value_color}{value_grade}{Colors.END}")
                elif value_score:
                    value_color = get_grade_color(value_score)
                    print(f"  {Colors.BOLD}Value:{Colors.END} {value_color}{value_score}/5{Colors.END}")
            
            if 'growth' in style_scores or 'growth_grade' in style_scores:
                growth_grade = style_scores.get('growth_grade') or (style_scores.get('growth') and ['F', 'D', 'C', 'B', 'A'][style_scores['growth'] - 1] if style_scores.get('growth') else None)
                growth_score = style_scores.get('growth', 0)
                if growth_grade:
                    growth_color = get_grade_color(growth_grade)
                    print(f"  {Colors.BOLD}Growth:{Colors.END} {growth_color}{growth_grade}{Colors.END}")
                elif growth_score:
                    growth_color = get_grade_color(growth_score)
                    print(f"  {Colors.BOLD}Growth:{Colors.END} {growth_color}{growth_score}/5{Colors.END}")
            
            if 'momentum' in style_scores or 'momentum_grade' in style_scores:
                momentum_grade = style_scores.get('momentum_grade') or (style_scores.get('momentum') and ['F', 'D', 'C', 'B', 'A'][style_scores['momentum'] - 1] if style_scores.get('momentum') else None)
                momentum_score = style_scores.get('momentum', 0)
                if momentum_grade:
                    momentum_color = get_grade_color(momentum_grade)
                    print(f"  {Colors.BOLD}Momentum:{Colors.END} {momentum_color}{momentum_grade}{Colors.END}")
                elif momentum_score:
                    momentum_color = get_grade_color(momentum_score)
                    print(f"  {Colors.BOLD}Momentum:{Colors.END} {momentum_color}{momentum_score}/5{Colors.END}")
            
            if 'vgm' in style_scores or 'vgm_grade' in style_scores:
                vgm_grade = style_scores.get('vgm_grade') or (style_scores.get('vgm') and ['F', 'D', 'C', 'B', 'A'][style_scores['vgm'] - 1] if style_scores.get('vgm') else None)
                vgm_score = style_scores.get('vgm', 0)
                if vgm_grade:
                    vgm_color = get_grade_color(vgm_grade)
                    print(f"  {Colors.BOLD}VGM Score:{Colors.END} {vgm_color}{vgm_grade}{Colors.END}")
                elif vgm_score:
                    vgm_color = get_grade_color(vgm_score)
                    print(f"  {Colors.BOLD}VGM Score:{Colors.END} {vgm_color}{vgm_score}/5{Colors.END}")
            
            print(f"{Colors.WHITE}Note: Style Scores use letter grades (A=Best, F=Worst){Colors.END}")
        
        # Display source URL
        if url:
            print(f"\n{Colors.BOLD}Source:{Colors.END} {Colors.WHITE}{url}{Colors.END}")
    else:
        print(f"\n{Colors.WHITE}Recommendation data could not be extracted from Zacks.com{Colors.END}")
        if url:
            print(f"{Colors.WHITE}You can check manually at: {url}{Colors.END}")
    
    # Disclaimer
    print(f"\n{Colors.YELLOW}{Colors.BOLD}Note:{Colors.END} Zacks.com data is scraped from their website and may not always be available or accurate. Always verify information from official sources.{Colors.END}")


