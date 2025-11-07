"""
Calculation functions for technical indicators and data analysis
"""

import pandas as pd
from .constants import Colors


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index (RSI)"""
    if prices is None or len(prices) < period + 1:
        return None
    
    try:
        # Convert to pandas Series if not already
        if not isinstance(prices, pd.Series):
            prices = pd.Series(prices)
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses using exponential moving average
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # Return the most recent RSI value
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
    except Exception as e:
        return None


def get_rsi_signal(rsi):
    """Get RSI signal (oversold/overbought/neutral)"""
    if rsi is None:
        return None, "N/A"
    
    if rsi >= 70:
        return "OVERBOUGHT", Colors.RED
    elif rsi <= 30:
        return "OVERSOLD", Colors.GREEN
    else:
        return "NEUTRAL", Colors.YELLOW


def get_earnings_trend(financials, quarterly_financials):
    """Extract earnings trend from financial statements"""
    earnings_trend = []
    
    # Try to get quarterly earnings first (more recent data)
    if quarterly_financials is not None and not quarterly_financials.empty:
        try:
            # Get Net Income from quarterly data
            if 'Net Income' in quarterly_financials.index:
                quarterly_data = quarterly_financials.loc['Net Income']
                for date, value in quarterly_data.items():
                    # Check for NaN (value != value checks for NaN)
                    if value is not None and not (isinstance(value, float) and value != value):
                        try:
                            earnings_trend.append({
                                'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                                'earnings': float(value),
                                'period': 'Quarterly'
                            })
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass
    
    # Fallback to annual financials if quarterly not available
    if not earnings_trend and financials is not None and not financials.empty:
        try:
            if 'Net Income' in financials.index:
                annual_data = financials.loc['Net Income']
                for date, value in annual_data.items():
                    # Check for NaN (value != value checks for NaN)
                    if value is not None and not (isinstance(value, float) and value != value):
                        try:
                            earnings_trend.append({
                                'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                                'earnings': float(value),
                                'period': 'Annual'
                            })
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass
    
    # Sort by date (most recent first)
    earnings_trend.sort(key=lambda x: x['date'], reverse=True)
    
    # Limit to last 8 periods for readability
    return earnings_trend[:8]


def get_analyst_ratings(info, recommendations, current_price):
    """Extract analyst ratings and price targets"""
    analyst_data = {
        'average_target': None,
        'high_target': None,
        'low_target': None,
        'recommendation': None,
        'recommendation_breakdown': {},
        'analysts': []
    }
    
    # Get price targets from info
    target_mean = info.get('targetMeanPrice')
    target_high = info.get('targetHighPrice')
    target_low = info.get('targetLowPrice')
    
    if target_mean:
        analyst_data['average_target'] = float(target_mean)
    if target_high:
        analyst_data['high_target'] = float(target_high)
    if target_low:
        analyst_data['low_target'] = float(target_low)
    
    # Get recommendation summary
    recommendation_mean = info.get('recommendationMean')
    recommendation_key = info.get('recommendationKey')
    
    if recommendation_mean:
        analyst_data['recommendation'] = recommendation_mean
    
    # Get recommendation breakdown
    # Try multiple possible fields for recommendation breakdown
    breakdown_fields = ['recommendationKey', 'recommendationBreakdown', 'numberOfAnalystOpinions']
    
    for field in breakdown_fields:
        breakdown_value = info.get(field)
        if breakdown_value:
            if isinstance(breakdown_value, dict):
                analyst_data['recommendation_breakdown'] = breakdown_value
                break
            elif isinstance(breakdown_value, (list, tuple)):
                # Sometimes it's a list
                if len(breakdown_value) > 0:
                    analyst_data['recommendation_breakdown'] = breakdown_value
                    break
    
    # Also try to get individual recommendation counts
    for key in ['strongBuy', 'buy', 'hold', 'underperform', 'sell']:
        count = info.get(key)
        if count is not None and count > 0:
            if 'recommendation_breakdown' not in analyst_data or not analyst_data['recommendation_breakdown']:
                analyst_data['recommendation_breakdown'] = {}
            analyst_data['recommendation_breakdown'][key] = count
    
    # Get recent analyst recommendations
    if recommendations is not None and not recommendations.empty:
        try:
            # Get the most recent recommendations
            recent_recs = recommendations.tail(20)  # Get last 20 recommendations
            
            # Try different column name variations
            firm_col = None
            rating_col = None
            
            for col in recent_recs.columns:
                col_lower = col.lower()
                if 'firm' in col_lower or 'analyst' in col_lower or 'company' in col_lower:
                    firm_col = col
                if 'grade' in col_lower or 'rating' in col_lower or 'recommendation' in col_lower or 'to' in col_lower:
                    rating_col = col
            
            # Group by firm/analyst if possible
            if firm_col and rating_col:
                for idx, row in recent_recs.iterrows():
                    firm = str(row.get(firm_col, 'Unknown')) if firm_col else 'Unknown'
                    rating = str(row.get(rating_col, 'N/A')) if rating_col else 'N/A'
                    date = idx if hasattr(idx, 'strftime') else str(idx)
                    analyst_data['analysts'].append({
                        'firm': firm,
                        'rating': rating,
                        'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10]
                    })
            elif rating_col:
                # If we only have rating column
                for idx, row in recent_recs.iterrows():
                    rating = str(row.get(rating_col, 'N/A'))
                    date = idx if hasattr(idx, 'strftime') else str(idx)
                    analyst_data['analysts'].append({
                        'firm': 'Analyst',
                        'rating': rating,
                        'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10]
                    })
            else:
                # If it's a Series with index as dates, try to extract from the value
                if len(recent_recs.columns) == 0 or (len(recent_recs.columns) == 1 and recent_recs.columns[0] == 0):
                    for idx in recent_recs.index:
                        date = idx if hasattr(idx, 'strftime') else str(idx)
                        analyst_data['analysts'].append({
                            'firm': 'Analyst',
                            'rating': 'Available',
                            'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10]
                        })
        except Exception as e:
            # Silently fail if recommendations parsing fails
            pass
    
    # Calculate upside/downside if we have average target and current price
    if analyst_data['average_target'] and current_price:
        try:
            current_price_val = float(current_price)
            target_val = analyst_data['average_target']
            upside_downside = ((target_val - current_price_val) / current_price_val) * 100
            analyst_data['upside_downside'] = upside_downside
        except (ValueError, TypeError):
            pass
    
    return analyst_data


