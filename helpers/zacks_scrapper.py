#!/usr/bin/env python3
"""
zacks_reco_scraper.py

Simple scraper to fetch Zacks recommendations (e.g., Strong Buy / Buy / Hold / Sell / Strong Sell)
for a given list of tickers. Uses requests + BeautifulSoup and keyword heuristics.

Usage:
    python zacks_reco_scraper.py AAPL MSFT TSLA

Notes:
 - Respect zacks.com terms of service and robots.txt.
 - This script uses simple heuristics — it may need updating if Zacks changes their HTML.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
from typing import Optional, Tuple, List

# ---- Configuration ----
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
REQUEST_TIMEOUT = 15  # seconds
SLEEP_BETWEEN_REQUESTS = 1.2  # be polite
# ------------------------

# Candidate URL patterns (Zacks uses a few structures; try the most common)
URL_PATTERNS = [
    "https://www.zacks.com/stock/quote/{ticker}",                # quote page
    "https://www.zacks.com/stock/research/{ticker}/stock-research",  # research page
    "https://www.zacks.com/stock/research/{ticker}",            # fallback
]


def fetch_page(url: str) -> Optional[str]:
    """Fetches the page HTML. Returns None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Warning: HTTP {resp.status_code} for {url}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_recommendation_from_html(html: str) -> Optional[Tuple[str, str]]:
    """
    Heuristic parsing:
    - Look for common labels and rating words in visible text and in meta tags.
    - Return tuple (rating_text, context_snippet) if found, else None.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True).lower()

    # Try common single-line meta or headline patterns first:
    # Look for phrases like "zacks rank: #1 (strong buy)" or "analyst rating: buy"
    # We'll search for known keywords in descending specificity.
    rating_keywords = [
        "strong buy",
        "buy",
        "hold",
        "sell",
        "strong sell",
        # sometimes phrased as "outperform", "underperform" — include those:
        "outperform",
        "underperform",
        "market perform",
    ]

    # Search within certain structural elements first (faster/more reliable)
    # 1) Look into possible rating containers (by id/class words commonly used)
    candidate_selectors = [
        '[class*="rating"]',
        '[class*="rank"]',
        '[class*="zacks"]',
        'meta[name="description"]',
        'meta[property="og:description"]',
        'title',
    ]
    for sel in candidate_selectors:
        if sel.startswith("meta") or sel == "title":
            # handle meta/title separately
            if sel == "title":
                content = soup.title.string if soup.title else ""
            else:
                meta = soup.select_one(sel)
                content = meta.get("content", "") if meta else ""
            if content:
                snippet = content.lower()
                for kw in rating_keywords:
                    if kw in snippet:
                        return (kw.title(), extract_snippet(snippet, kw))
        else:
            for el in soup.select(sel):
                txt = el.get_text(" ", strip=True).lower()
                for kw in rating_keywords:
                    if kw in txt:
                        return (kw.title(), extract_snippet(txt, kw))

    # 2) Fallback: search entire page text for rating keywords near Zacks terms
    # e.g., "Zacks Rank: #1 (Strong Buy)" or "Analyst Rating: Buy"
    # We'll use regex capturing a short surrounding window.
    for kw in rating_keywords:
        # search for 'zacks' within 80 chars of keyword, or the keyword with small context
        pattern1 = re.compile(rf".{{0,60}}zacks.{{0,60}}{re.escape(kw)}.{{0,40}}", re.IGNORECASE)
        m1 = pattern1.search(html)
        if m1:
            snippet = clean_snippet(m1.group(0))
            return (kw.title(), snippet)

        # generic near-match:
        pattern2 = re.compile(rf".{{0,60}}{re.escape(kw)}.{{0,60}}", re.IGNORECASE)
        m2 = pattern2.search(html)
        if m2:
            snippet = clean_snippet(m2.group(0))
            return (kw.title(), snippet)

    # 3) Nothing found
    return None


def extract_snippet(text: str, keyword: str, width: int = 80) -> str:
    """Return a short snippet centered around keyword."""
    idx = text.find(keyword)
    if idx == -1:
        return text[:width].strip()
    start = max(0, idx - width // 2)
    end = start + width
    return text[start:end].strip()


def clean_snippet(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    return s.strip()[:300]


def parse_zacks_data_from_html(html: str, url: str) -> dict:
    """
    Parse Zacks recommendation, rank, and style scores from HTML.
    Returns a dict with recommendation, rank, style_scores, and url.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    zacks_data = {
        'recommendation': None,
        'rank': None,
        'industry_rank': None,
        'industry_name': None,
        'total_industries': None,
        'percentile_text': None,
        'style_scores': {},
        'url': url
    }
    
    # Try to find Zacks Rank (1-5, where 1=Strong Buy, 5=Strong Sell)
    # Based on actual HTML structure: 
    # <dd width="50%"><strong>Hold</strong> <span class="rank_chip rankrect_3">3</span> </dd>
    
    # Method 1: Look for the <dd> element that follows <dt> containing "Zacks Rank"
    dd_elem = None
    for dt in soup.find_all('dt'):
        dt_text = dt.get_text()
        dt_link = dt.find('a')
        if ('Zacks Rank' in dt_text or 
            (dt_link and 'buy-list' in dt_link.get('href', ''))):
            dd_elem = dt.find_next_sibling('dd')
            if dd_elem:
                break
    
    if dd_elem:
        # Look for <strong> tag with recommendation text (e.g., "Hold", "Buy", "Sell")
        strong_elem = dd_elem.find('strong')
        if strong_elem:
            rec_text = strong_elem.get_text(strip=True)
            rec_lower = rec_text.lower()
            if 'strong buy' in rec_lower:
                zacks_data['recommendation'] = 'Strong Buy'
                zacks_data['rank'] = 1
            elif 'buy' in rec_lower and 'strong' not in rec_lower:
                zacks_data['recommendation'] = 'Buy'
                zacks_data['rank'] = 2
            elif 'hold' in rec_lower:
                zacks_data['recommendation'] = 'Hold'
                zacks_data['rank'] = 3
            elif 'strong sell' in rec_lower:
                zacks_data['recommendation'] = 'Strong Sell'
                zacks_data['rank'] = 5
            elif 'sell' in rec_lower and 'strong' not in rec_lower:
                zacks_data['recommendation'] = 'Sell'
                zacks_data['rank'] = 4
        
        # Also extract rank from rank_chip span (e.g., <span class="rank_chip rankrect_3">3</span>)
        rank_chip = dd_elem.select_one('span.rank_chip, span[class*="rankrect"]')
        if rank_chip:
            # Extract from class name like "rankrect_3"
            class_name = ' '.join(rank_chip.get('class', []))
            rank_match = re.search(r'rankrect[_-]?(\d)', class_name)
            if rank_match:
                rank_num = int(rank_match.group(1))
                if 1 <= rank_num <= 5:
                    zacks_data['rank'] = rank_num
                    # Only set recommendation if not already set from <strong> tag
                    if not zacks_data['recommendation']:
                        rank_map = {1: 'Strong Buy', 2: 'Buy', 3: 'Hold', 4: 'Sell', 5: 'Strong Sell'}
                        zacks_data['recommendation'] = rank_map.get(rank_num, 'Hold')
            else:
                # Fallback: extract from text content
                rank_text = rank_chip.get_text(strip=True)
                rank_match = re.search(r'(\d)', rank_text)
                if rank_match:
                    rank_num = int(rank_match.group(1))
                    if 1 <= rank_num <= 5:
                        zacks_data['rank'] = rank_num
                        if not zacks_data['recommendation']:
                            rank_map = {1: 'Strong Buy', 2: 'Buy', 3: 'Hold', 4: 'Sell', 5: 'Strong Sell'}
                            zacks_data['recommendation'] = rank_map.get(rank_num, 'Hold')
    
    # Method 2: Also check the quote ribbon section (alternative location)
    if not zacks_data.get('recommendation'):
        rank_view = soup.select_one('p.rank_view')
        if rank_view:
            # Look for pattern like "3-Hold" or just the rank number
            rank_text = rank_view.get_text()
            rank_match = re.search(r'(\d)[\s-]*(Strong\s+)?(Buy|Hold|Sell)', rank_text, re.IGNORECASE)
            if rank_match:
                rank_num = int(rank_match.group(1))
                if 1 <= rank_num <= 5:
                    zacks_data['rank'] = rank_num
                    rank_map = {1: 'Strong Buy', 2: 'Buy', 3: 'Hold', 4: 'Sell', 5: 'Strong Sell'}
                    zacks_data['recommendation'] = rank_map.get(rank_num, 'Hold')
            
            # Also check for rank_chip in rank_view
            if not zacks_data.get('rank'):
                rank_chip = rank_view.select_one('span.rank_chip[class*="rankrect"]')
                if rank_chip:
                    class_name = ' '.join(rank_chip.get('class', []))
                    rank_match = re.search(r'rankrect[_-]?(\d)', class_name)
                    if rank_match:
                        rank_num = int(rank_match.group(1))
                        if 1 <= rank_num <= 5:
                            zacks_data['rank'] = rank_num
                            rank_map = {1: 'Strong Buy', 2: 'Buy', 3: 'Hold', 4: 'Sell', 5: 'Strong Sell'}
                            zacks_data['recommendation'] = rank_map.get(rank_num, 'Hold')
    
    # Fallback: Use the heuristic parser if we haven't found recommendation yet
    if not zacks_data.get('recommendation'):
        res = parse_recommendation_from_html(html)
        if res:
            rating_text, snippet = res
            rating_map = {
                'Strong Buy': ('Strong Buy', 1),
                'Buy': ('Buy', 2),
                'Hold': ('Hold', 3),
                'Sell': ('Sell', 4),
                'Strong Sell': ('Strong Sell', 5),
                'Outperform': ('Buy', 2),
                'Underperform': ('Sell', 4),
                'Market Perform': ('Hold', 3),
            }
            recommendation, rank = rating_map.get(rating_text, (rating_text, None))
            zacks_data['recommendation'] = recommendation
            if rank and not zacks_data.get('rank'):
                zacks_data['rank'] = rank
    
    # Try to find Style Scores (Value, Growth, Momentum)
    # Based on actual HTML: 
    # <p class="float_right"><span class="composite_val">F</span> Value | <span class="composite_val">C</span> Growth | <span class="composite_val">D</span> Momentum | <span class="composite_val composite_val_vgm">F</span> VGM</p>
    
    # Look for the paragraph with class "float_right" that contains style scores
    style_scores_p = soup.select_one('p.float_right')
    if not style_scores_p:
        # Alternative: Look for paragraph within dt.score or following dt with "Style Scores"
        for dt in soup.find_all('dt'):
            if 'Style Scores' in dt.get_text():
                style_scores_p = dt.find_next('p')
                if style_scores_p and ('Value' in style_scores_p.get_text() or 'Growth' in style_scores_p.get_text()):
                    break
    
    if not style_scores_p:
        # Fallback: Try finding by text content
        for p in soup.find_all('p'):
            p_text = p.get_text()
            if 'Value' in p_text and 'Growth' in p_text and 'Momentum' in p_text:
                style_scores_p = p
                break
    
    if style_scores_p:
        # Map letter grades to numbers (A=5, B=4, C=3, D=2, F=1)
        grade_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
        
        # Get the text content - should be like "F Value | C Growth | D Momentum | F VGM"
        text_content = style_scores_p.get_text()
        
        # Extract using regex patterns
        value_match = re.search(r'([A-F])\s*Value', text_content, re.IGNORECASE)
        if value_match:
            value_grade = value_match.group(1).upper()
            zacks_data['style_scores']['value'] = grade_map.get(value_grade, 0)
            zacks_data['style_scores']['value_grade'] = value_grade
        
        growth_match = re.search(r'([A-F])\s*Growth', text_content, re.IGNORECASE)
        if growth_match:
            growth_grade = growth_match.group(1).upper()
            zacks_data['style_scores']['growth'] = grade_map.get(growth_grade, 0)
            zacks_data['style_scores']['growth_grade'] = growth_grade
        
        momentum_match = re.search(r'([A-F])\s*Momentum', text_content, re.IGNORECASE)
        if momentum_match:
            momentum_grade = momentum_match.group(1).upper()
            zacks_data['style_scores']['momentum'] = grade_map.get(momentum_grade, 0)
            zacks_data['style_scores']['momentum_grade'] = momentum_grade
        
        vgm_match = re.search(r'([A-F])\s*VGM', text_content, re.IGNORECASE)
        if vgm_match:
            vgm_grade = vgm_match.group(1).upper()
            zacks_data['style_scores']['vgm'] = grade_map.get(vgm_grade, 0)
            zacks_data['style_scores']['vgm_grade'] = vgm_grade
    
    # Try to find Zacks Industry Rank
    # Based on actual HTML structure: <div class="zr_rankbox industry_rank">
    # Pattern: "Bottom 6% (229 out of 244)" or "Top 10% (25 out of 265)"
    # Industry count can be 244, 256, or 265 depending on classification system
    # Be careful not to confuse with Zacks Rank (which is 1-5)
    
    # Method 1: Look for the industry_rank div with class "zr_rankbox industry_rank"
    industry_rank_div = soup.select_one('.zr_rankbox.industry_rank, [class*="industry_rank"]')
    if industry_rank_div:
        # Look for the rank_view paragraph with the pattern "X out of Y"
        rank_view = industry_rank_div.select_one('p.rank_view a.status, p.rank_view')
        if rank_view:
            rank_text = rank_view.get_text(strip=True)
            # Match patterns like "Bottom 6% (229 out of 244)" or "Top 10% (25 out of 265)"
            # Capture both the percentile text and the rank numbers
            full_match = re.search(r'(Top|Bottom|Middle)\s+(\d+)%\s*\((\d+)\s*out\s*of\s*(\d+)\)', rank_text, re.IGNORECASE)
            if full_match:
                percentile_position = full_match.group(1)  # "Top", "Bottom", or "Middle"
                percentile_value = int(full_match.group(2))  # e.g., 6
                industry_rank = int(full_match.group(3))  # e.g., 229
                total_industries = int(full_match.group(4))  # e.g., 244
                
                # Validate the numbers make sense
                if 1 <= industry_rank <= total_industries and total_industries <= 300:
                    zacks_data['industry_rank'] = industry_rank
                    zacks_data['total_industries'] = total_industries
                    zacks_data['percentile_text'] = f"{percentile_position} {percentile_value}%"
            else:
                # Fallback: Just try to extract the rank numbers without percentile
                rank_match = re.search(r'\((\d+)\s*out\s*of\s*(\d+)\)', rank_text, re.IGNORECASE)
                if rank_match:
                    industry_rank = int(rank_match.group(1))
                    total_industries = int(rank_match.group(2))
                    # Validate the numbers make sense (rank should be <= total)
                    if 1 <= industry_rank <= total_industries and total_industries <= 300:
                        zacks_data['industry_rank'] = industry_rank
                        zacks_data['total_industries'] = total_industries
        
        # Look for industry name in the second rank_view paragraph
        industry_name_elem = industry_rank_div.select_one('p.rank_view a.sector')
        if industry_name_elem:
            industry_text = industry_name_elem.get_text(strip=True)
            # Remove "Industry: " prefix if present
            industry_name = re.sub(r'^Industry:\s*', '', industry_text, flags=re.IGNORECASE)
            if industry_name and len(industry_name) > 3:
                zacks_data['industry_name'] = industry_name
    
    # Method 2: Look for dt/dd pairs with "Industry Rank" label (fallback)
    if not zacks_data.get('industry_rank'):
        for dt in soup.find_all('dt'):
            dt_text = dt.get_text()
            # Make sure we're looking for "Industry Rank" specifically, not "Zacks Rank"
            if 'Industry Rank' in dt_text and 'Zacks Rank' not in dt_text:
                dd_elem = dt.find_next_sibling('dd')
                if dd_elem:
                    dd_text = dd_elem.get_text(strip=True)
                    
                    # Try to match full pattern with percentile
                    full_match = re.search(r'(Top|Bottom|Middle)\s+(\d+)%\s*\((\d+)\s*out\s*of\s*(\d+)\)', dd_text, re.IGNORECASE)
                    if full_match:
                        percentile_position = full_match.group(1)
                        percentile_value = int(full_match.group(2))
                        industry_rank = int(full_match.group(3))
                        total_industries = int(full_match.group(4))
                        if 1 <= industry_rank <= total_industries and total_industries <= 300:
                            zacks_data['industry_rank'] = industry_rank
                            zacks_data['total_industries'] = total_industries
                            zacks_data['percentile_text'] = f"{percentile_position} {percentile_value}%"
                    else:
                        # Try to match patterns like "42 out of 244" or "42 out of 265"
                        rank_match = re.search(r'(\d+)\s*out\s*of\s*(\d+)', dd_text, re.IGNORECASE)
                        if rank_match:
                            industry_rank = int(rank_match.group(1))
                            total_industries = int(rank_match.group(2))
                            if 1 <= industry_rank <= total_industries and total_industries <= 300:
                                zacks_data['industry_rank'] = industry_rank
                                zacks_data['total_industries'] = total_industries
                    
                    # Try to extract industry name if present
                    industry_link = dd_elem.find('a')
                    if industry_link:
                        industry_name = industry_link.get_text(strip=True)
                        # Filter out numbers and short text
                        if industry_name and len(industry_name) > 5 and not industry_name.isdigit():
                            zacks_data['industry_name'] = industry_name
                    break
    
    # Method 3: Search for patterns in the entire page text
    if not zacks_data.get('industry_rank'):
        # Search for full pattern with percentile first
        full_pattern = re.compile(r'(Top|Bottom|Middle)\s+(\d+)%\s*\((\d+)\s*out\s*of\s*(\d+)\)', re.IGNORECASE)
        match = full_pattern.search(soup.get_text())
        if match:
            percentile_position = match.group(1)
            percentile_value = int(match.group(2))
            industry_rank = int(match.group(3))
            total_industries = int(match.group(4))
            # Look for reasonable industry counts (typically 244, 256, or 265)
            if 1 <= industry_rank <= total_industries and 200 <= total_industries <= 300:
                zacks_data['industry_rank'] = industry_rank
                zacks_data['total_industries'] = total_industries
                zacks_data['percentile_text'] = f"{percentile_position} {percentile_value}%"
        else:
            # Fallback: Search for patterns like "(229 out of 244)" anywhere in the page
            industry_rank_pattern = re.compile(r'\((\d+)\s*out\s*of\s*(\d+)\)', re.IGNORECASE)
            matches = industry_rank_pattern.findall(soup.get_text())
            for match in matches:
                industry_rank = int(match[0])
                total_industries = int(match[1])
                # Look for reasonable industry counts (typically 244, 256, or 265)
                if 1 <= industry_rank <= total_industries and 200 <= total_industries <= 300:
                    zacks_data['industry_rank'] = industry_rank
                    zacks_data['total_industries'] = total_industries
                    break
    
    return zacks_data


def get_zacks_recommendation_for_ticker(ticker: str) -> dict:
    """
    Tries multiple URL patterns and returns a dict with:
      { 'recommendation': str|None, 'rank': int|None, 'style_scores': dict, 'url': str|None }
    """
    ticker = ticker.strip().upper()
    for pattern in URL_PATTERNS:
        url = pattern.format(ticker=ticker)
        html = fetch_page(url)
        if not html:
            time.sleep(0.5)
            continue

        # Parse all Zacks data from HTML
        zacks_data = parse_zacks_data_from_html(html, url)
        
        # If we found at least a recommendation, return the data
        if zacks_data.get('recommendation'):
            return zacks_data
        
        # polite pause if we will try next URL for same ticker
        time.sleep(0.4)

    return {
        'recommendation': None,
        'rank': None,
        'industry_rank': None,
        'industry_name': None,
        'total_industries': None,
        'percentile_text': None,
        'style_scores': {},
        'url': None
    }


def check_robots_txt() -> bool:
    """
    A very small check: get zacks.com/robots.txt and see if /stock/quote is disallowed.
    Returns True if allowed (no explicit disallow seen for our paths), False otherwise.
    """
    try:
        r = requests.get("https://www.zacks.com/robots.txt", headers=HEADERS, timeout=5)
        if r.status_code != 200:
            return True  # can't fetch robots, we'll proceed but user should be cautious
        txt = r.text.lower()
        # naive check for disallow lines
        disallows = re.findall(r"disallow:\s*(\S+)", txt)
        # check if any of our common paths appear in the disallow list
        for d in disallows:
            if d.strip("/") in ("stock/quote", "stock/research", "stock"):
                return False
        return True
    except Exception:
        return True


def main(tickers: List[str]):
    if not check_robots_txt():
        print("robots.txt suggests scraping the stock pages may be disallowed. Aborting.")
        return

    results = []
    for i, t in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] Checking {t} ...")
        res = get_zacks_recommendation_for_ticker(t)
        if res.get("recommendation"):
            print(f"  -> {res['recommendation']} (Rank: {res.get('rank', 'N/A')}) (source: {res.get('url', 'N/A')})")
            if res.get('style_scores'):
                style_info = []
                for key in ['value_grade', 'growth_grade', 'momentum_grade', 'vgm_grade']:
                    if key in res['style_scores']:
                        score_name = key.replace('_grade', '').title()
                        style_info.append(f"{score_name}: {res['style_scores'][key]}")
                if style_info:
                    print(f"     Style Scores: {', '.join(style_info)}")
            print()
        else:
            print("  -> Recommendation not found on known pages.\n")
        results.append(res)
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # Optionally return or save results
    return results

