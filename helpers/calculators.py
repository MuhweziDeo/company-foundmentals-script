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


def identify_swing_points(history, lookback=5):
    """
    Identify swing highs and swing lows on daily timeframe.
    A swing high is a high that is higher than N candles on both sides.
    A swing low is a low that is lower than N candles on both sides.
    
    Args:
        history: DataFrame with OHLC data
        lookback: Number of candles to look back/forward (default 5)
    
    Returns:
        Dictionary with swing_highs and swing_lows lists
    """
    if history is None or history.empty or len(history) < lookback * 2 + 1:
        return {'swing_highs': [], 'swing_lows': []}
    
    try:
        swing_highs = []
        swing_lows = []
        
        # Get High and Low columns
        highs = history['High']
        lows = history['Low']
        
        # Iterate through the data, skipping the first and last N candles
        for i in range(lookback, len(history) - lookback):
            current_high = highs.iloc[i]
            current_low = lows.iloc[i]
            current_date = history.index[i]
            
            # Check if current high is a swing high
            is_swing_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and highs.iloc[j] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append({
                    'date': current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date)[:10],
                    'price': float(current_high),
                    'index': i
                })
            
            # Check if current low is a swing low
            is_swing_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and lows.iloc[j] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append({
                    'date': current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date)[:10],
                    'price': float(current_low),
                    'index': i
                })
        
        # Sort by date (most recent first)
        swing_highs.sort(key=lambda x: x['index'], reverse=True)
        swing_lows.sort(key=lambda x: x['index'], reverse=True)
        
        return {
            'swing_highs': swing_highs,
            'swing_lows': swing_lows
        }
    except Exception as e:
        return {'swing_highs': [], 'swing_lows': []}


def analyze_price_action_trend(history, swing_points=None):
    """
    Analyze price action to determine if it's an uptrend or downtrend.
    Uses swing structure analysis:
    - Uptrend: Higher highs and higher lows
    - Downtrend: Lower highs and lower lows
    
    Args:
        history: DataFrame with OHLC data
        swing_points: Optional pre-calculated swing points
    
    Returns:
        Dictionary with trend information
    """
    if history is None or history.empty:
        return {
            'trend': 'UNKNOWN',
            'trend_strength': None,
            'description': 'Insufficient data',
            'swing_highs': [],
            'swing_lows': []
        }
    
    try:
        # Get swing points if not provided
        if swing_points is None:
            swing_points = identify_swing_points(history, lookback=5)
        
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Need at least 2 swing highs and 2 swing lows to determine trend
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            # Fallback: Use simple moving average comparison
            closes = history['Close']
            if len(closes) >= 50:
                sma_20 = closes.tail(20).mean()
                sma_50 = closes.tail(50).mean()
                
                if sma_20 > sma_50:
                    trend = 'UPTREND'
                    description = 'Price above short-term average (bullish momentum)'
                elif sma_20 < sma_50:
                    trend = 'DOWNTREND'
                    description = 'Price below short-term average (bearish momentum)'
                else:
                    trend = 'SIDEWAYS'
                    description = 'Price consolidating (neutral)'
                
                return {
                    'trend': trend,
                    'trend_strength': None,
                    'description': description,
                    'swing_highs': swing_highs[:5],  # Last 5
                    'swing_lows': swing_lows[:5]  # Last 5
                }
            else:
                return {
                    'trend': 'UNKNOWN',
                    'trend_strength': None,
                    'description': 'Insufficient data for trend analysis',
                    'swing_highs': swing_highs[:5],
                    'swing_lows': swing_lows[:5]
                }
        
        # Analyze recent swing structure (last 3-4 swings)
        recent_highs = swing_highs[:4]  # Most recent 4 swing highs
        recent_lows = swing_lows[:4]    # Most recent 4 swing lows
        
        # Check for higher highs (uptrend) or lower highs (downtrend)
        higher_highs = 0
        lower_highs = 0
        higher_lows = 0
        lower_lows = 0
        
        # Compare consecutive swing highs
        for i in range(len(recent_highs) - 1):
            if recent_highs[i]['price'] > recent_highs[i + 1]['price']:
                higher_highs += 1
            elif recent_highs[i]['price'] < recent_highs[i + 1]['price']:
                lower_highs += 1
        
        # Compare consecutive swing lows
        for i in range(len(recent_lows) - 1):
            if recent_lows[i]['price'] > recent_lows[i + 1]['price']:
                higher_lows += 1
            elif recent_lows[i]['price'] < recent_lows[i + 1]['price']:
                lower_lows += 1
        
        # Determine trend based on swing structure
        uptrend_score = higher_highs + higher_lows
        downtrend_score = lower_highs + lower_lows
        
        if uptrend_score > downtrend_score and higher_highs > 0:
            trend = 'UPTREND'
            trend_strength = min(uptrend_score / 4.0, 1.0)  # Normalize to 0-1
            description = f'Higher highs and higher lows pattern (strength: {trend_strength:.1%})'
        elif downtrend_score > uptrend_score and lower_highs > 0:
            trend = 'DOWNTREND'
            trend_strength = min(downtrend_score / 4.0, 1.0)
            description = f'Lower highs and lower lows pattern (strength: {trend_strength:.1%})'
        else:
            trend = 'SIDEWAYS'
            trend_strength = None
            description = 'Mixed swing structure (consolidation/range-bound)'
        
        return {
            'trend': trend,
            'trend_strength': trend_strength,
            'description': description,
            'swing_highs': recent_highs[:5],  # Last 5 for display
            'swing_lows': recent_lows[:5]     # Last 5 for display
        }
    except Exception as e:
        return {
            'trend': 'UNKNOWN',
            'trend_strength': None,
            'description': f'Error analyzing trend: {str(e)}',
            'swing_highs': [],
            'swing_lows': []
        }


def generate_trading_recommendation(data):
    """
    Generate a comprehensive buy/sell/hold recommendation based on:
    - Price action trend
    - Analyst ratings
    - RSI indicator
    
    Returns a dictionary with recommendation, score, and detailed reasons
    """
    info = data.get('info', {})
    history = data.get('history')
    recommendations = data.get('recommendations')
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    
    # Initialize scores (positive = bullish, negative = bearish)
    scores = {
        'price_action': 0,
        'analyst_rating': 0,
        'rsi': 0
    }
    
    reasons = []
    
    # 1. Analyze Price Action Trend
    price_action_score = 0
    price_action_reason = ""
    trend_data = None
    if history is not None and not history.empty:
        trend_data = analyze_price_action_trend(history)
        trend = trend_data.get('trend', 'UNKNOWN')
        trend_strength = trend_data.get('trend_strength')
        
        if trend == 'UPTREND':
            # Strong uptrend gets +2, moderate gets +1
            price_action_score = 2 if (trend_strength and trend_strength > 0.6) else 1
            price_action_reason = f"Price action shows {trend.lower()} pattern"
            if trend_strength:
                price_action_reason += f" (strength: {trend_strength:.1%})"
        elif trend == 'DOWNTREND':
            # Strong downtrend gets -2, moderate gets -1
            price_action_score = -2 if (trend_strength and trend_strength > 0.6) else -1
            price_action_reason = f"Price action shows {trend.lower()} pattern"
            if trend_strength:
                price_action_reason += f" (strength: {trend_strength:.1%})"
        else:
            price_action_score = 0
            price_action_reason = "Price action shows sideways/consolidation pattern"
    else:
        price_action_reason = "Price action data unavailable"
    
    scores['price_action'] = price_action_score
    if price_action_reason:
        reasons.append(f"Price Action: {price_action_reason}")
    
    # 2. Analyze Analyst Ratings
    analyst_score = 0
    analyst_reason = ""
    analyst_data = get_analyst_ratings(info, recommendations, current_price)
    
    recommendation_mean = analyst_data.get('recommendation')
    recommendation_breakdown = analyst_data.get('recommendation_breakdown', {})
    
    if recommendation_mean:
        # Recommendation values: 1=Strong Buy, 2=Buy, 3=Hold, 4=Underperform, 5=Sell
        if isinstance(recommendation_mean, (int, float)):
            if recommendation_mean <= 1.5:
                analyst_score = 2
                analyst_reason = "Strong Buy consensus"
            elif recommendation_mean <= 2.5:
                analyst_score = 1
                analyst_reason = "Buy consensus"
            elif recommendation_mean <= 3.5:
                analyst_score = 0
                analyst_reason = "Hold consensus"
            elif recommendation_mean <= 4.5:
                analyst_score = -1
                analyst_reason = "Underperform consensus"
            else:
                analyst_score = -2
                analyst_reason = "Sell consensus"
        else:
            rec_str = str(recommendation_mean).lower()
            if 'strong buy' in rec_str or 'buy' in rec_str:
                analyst_score = 1
                analyst_reason = f"Analyst recommendation: {recommendation_mean}"
            elif 'sell' in rec_str or 'underperform' in rec_str:
                analyst_score = -1
                analyst_reason = f"Analyst recommendation: {recommendation_mean}"
            else:
                analyst_score = 0
                analyst_reason = f"Analyst recommendation: {recommendation_mean}"
    
    # Also consider price target
    if analyst_data.get('average_target') and current_price:
        try:
            target = float(analyst_data['average_target'])
            price_val = float(current_price)
            upside = ((target - price_val) / price_val) * 100
            
            if upside > 20:
                analyst_score += 1
                analyst_reason += f" (Target: +{upside:.1f}% upside)"
            elif upside < -20:
                analyst_score -= 1
                analyst_reason += f" (Target: {upside:.1f}% downside)"
        except (ValueError, TypeError):
            pass
    
    scores['analyst_rating'] = analyst_score
    if analyst_reason:
        reasons.append(f"Analyst Ratings: {analyst_reason}")
    
    # 3. Analyze RSI
    rsi_score = 0
    rsi_reason = ""
    rsi_value = None
    
    if history is not None and not history.empty:
        try:
            recent_prices = history['Close'].tail(30)
            if len(recent_prices) >= 15:
                rsi_value = calculate_rsi(recent_prices, period=14)
                
                if rsi_value is not None:
                    if rsi_value <= 30:
                        # Oversold - bullish signal
                        rsi_score = 2
                        rsi_reason = f"RSI is oversold ({rsi_value:.1f}) - potential buying opportunity"
                    elif rsi_value <= 40:
                        # Approaching oversold - slightly bullish
                        rsi_score = 1
                        rsi_reason = f"RSI is low ({rsi_value:.1f}) - may indicate oversold condition"
                    elif rsi_value >= 70:
                        # Overbought - bearish signal
                        rsi_score = -2
                        rsi_reason = f"RSI is overbought ({rsi_value:.1f}) - potential selling pressure"
                    elif rsi_value >= 60:
                        # Approaching overbought - slightly bearish
                        rsi_score = -1
                        rsi_reason = f"RSI is elevated ({rsi_value:.1f}) - approaching overbought territory"
                    else:
                        # Neutral range (40-60)
                        rsi_score = 0
                        rsi_reason = f"RSI is neutral ({rsi_value:.1f})"
        except Exception:
            pass
    
    scores['rsi'] = rsi_score
    if rsi_reason:
        reasons.append(f"RSI: {rsi_reason}")
    
    # Calculate total score
    total_score = scores['price_action'] + scores['analyst_rating'] + scores['rsi']
    
    # Determine recommendation based on total score
    if total_score >= 3:
        recommendation = "STRONG BUY"
        recommendation_color = Colors.GREEN
        recommendation_symbol = "↑↑"
    elif total_score >= 1:
        recommendation = "BUY"
        recommendation_color = Colors.GREEN
        recommendation_symbol = "↑"
    elif total_score <= -3:
        recommendation = "STRONG SELL"
        recommendation_color = Colors.RED
        recommendation_symbol = "↓↓"
    elif total_score <= -1:
        recommendation = "SELL"
        recommendation_color = Colors.RED
        recommendation_symbol = "↓"
    else:
        recommendation = "HOLD"
        recommendation_color = Colors.YELLOW
        recommendation_symbol = "→"
    
    # Generate summary reason
    summary_reason = ""
    if total_score >= 3:
        summary_reason = "Multiple bullish indicators align - strong buying opportunity"
    elif total_score >= 1:
        summary_reason = "Bullish indicators outweigh bearish signals"
    elif total_score <= -3:
        summary_reason = "Multiple bearish indicators align - strong selling signal"
    elif total_score <= -1:
        summary_reason = "Bearish indicators outweigh bullish signals"
    else:
        summary_reason = "Mixed signals - maintain current position or wait for clearer direction"
    
    return {
        'recommendation': recommendation,
        'recommendation_color': recommendation_color,
        'recommendation_symbol': recommendation_symbol,
        'total_score': total_score,
        'scores': scores,
        'reasons': reasons,
        'summary_reason': summary_reason,
        'rsi_value': rsi_value,
        'price_action_trend': trend_data.get('trend', 'UNKNOWN') if trend_data else 'UNKNOWN',
        'analyst_recommendation': recommendation_mean
    }


