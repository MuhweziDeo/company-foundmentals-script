#!/usr/bin/env python3
"""
Stock Fundamentals Analyzer
Collects company fundamental data using free APIs and displays it in the console.
Usage: python stock.py <TICKER>
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Import from helpers package
from helpers import (
    Colors,
    get_financial_data,
    display_price_data,
    display_financial_data,
    display_valuation_data,
    display_operation_data,
    display_macro_sector_data,
    display_earnings_trend,
    display_analyst_ratings,
    display_price_action_trend,
    display_trading_recommendation,
    collect_all_data,
    export_to_excel,
    export_to_pdf
)


def main():
    parser = argparse.ArgumentParser(
        description='Stock Fundamentals Analyzer - Collects company fundamental data'
    )
    parser.add_argument('ticker', type=str.upper, help='Stock ticker symbol (e.g., AAPL, MSFT)')
    parser.add_argument('-o', '--output', type=str, help='Output file path (supports .xlsx or .pdf extension)')
    
    args = parser.parse_args()
    ticker = args.ticker
    output_path = args.output
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}STOCK FUNDAMENTALS ANALYSIS FOR: {Colors.YELLOW}{ticker}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.WHITE}Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Disclaimer notice
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ DISCLAIMER:{Colors.END} {Colors.WHITE}This tool is for informational and educational purposes only.")
    print(f"{Colors.WHITE}It does NOT provide financial, investment, or trading advice.")
    print(f"{Colors.WHITE}Use at your own risk. See DISCLAIMER.md and LICENSE for details.{Colors.END}\n")
    
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
    display_earnings_trend(data)
    display_analyst_ratings(data)
    display_price_action_trend(data)
    display_trading_recommendation(data)
    
    # Export to file if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect all data for export
        export_data = collect_all_data(data, ticker)
        
        # Determine format from extension
        if output_path.suffix.lower() == '.xlsx':
            print(f"\n{Colors.YELLOW}📊 Exporting to Excel: {output_path}{Colors.END}")
            if export_to_excel(export_data, str(output_path)):
                print(f"{Colors.GREEN}✓ Successfully exported to {output_path}{Colors.END}")
            else:
                sys.exit(1)
        elif output_path.suffix.lower() == '.pdf':
            print(f"\n{Colors.YELLOW}📄 Exporting to PDF: {output_path}{Colors.END}")
            if export_to_pdf(export_data, str(output_path)):
                print(f"{Colors.GREEN}✓ Successfully exported to {output_path}{Colors.END}")
            else:
                sys.exit(1)
        else:
            print(f"{Colors.RED}Error: Unsupported file format. Use .xlsx or .pdf extension.{Colors.END}")
            sys.exit(1)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}Analysis Complete{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}\n")
    
    # Note about data availability
    print(f"{Colors.YELLOW}Note: Some metrics (marked as N/A) require:{Colors.END}")
    print(f"{Colors.WHITE}  - Qualitative analysis (business model, competitive advantage, management){Colors.END}")
    print(f"{Colors.WHITE}  - External macroeconomic data APIs (interest rates, inflation){Colors.END}")
    print(f"{Colors.WHITE}  - Industry-specific research (market share, regulations){Colors.END}")
    print()
    
    # Final disclaimer reminder
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠ REMINDER:{Colors.END} {Colors.WHITE}This analysis is for informational purposes only.")
    print(f"{Colors.WHITE}Always do your own research and consult with qualified financial advisors before making investment decisions.{Colors.END}")
    print()


if __name__ == "__main__":
    main()
