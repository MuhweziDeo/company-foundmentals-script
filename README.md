# Stock Fundamentals Analyzer

A Python command-line tool that collects comprehensive company fundamental data using free APIs and displays it in a beautifully formatted, color-coded console output.

## Features

### 📊 Price Information
- **Current Price** - Real-time stock price
- **YTD % Change** - Year-to-date performance with color coding (green for positive, red for negative)
- **YTD High/Low** - Highest and lowest prices for the current year with dates
- **All-Time High/Low** - Historical price extremes with dates
- **Distance from ATH/ATL** - Percentage distance from all-time highs and lows

### 💰 Financial Metrics
- Revenue (Sales)
- Earnings / Net Income
- Earnings Per Share (EPS)
- Cash Flow (Operating)
- Debt-to-Equity Ratio
- Return on Equity (ROE)
- Gross Margin / Net Margin

### 📈 Valuation Metrics
- P/E (Price-to-Earnings) Ratio
- P/B (Price-to-Book) Ratio
- P/S (Price-to-Sales) Ratio
- EV/EBITDA

### 🏢 Operational Metrics
- Market Capitalization
- Business Model Summary
- Sector and Industry Classification
- Company Size (Full-Time Employees)

### 🌍 Macroeconomic & Sector Metrics
- Revenue Growth (Demand Proxy)
- Earnings Growth (Industry Trend Proxy)
- Beta (Market Correlation)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Setup

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or use the automated setup script:
   ```bash
   ./run.sh AAPL
   ```
   (The script will automatically create a virtual environment and install dependencies on first run)

## Usage

### Method 1: Using the Run Script (Recommended)

The `run.sh` script automatically sets up the environment and runs the program:

```bash
./run.sh <TICKER>
```

Example:
```bash
./run.sh AAPL
./run.sh MSFT
./run.sh TSLA
```

The script will:
- Create a virtual environment if it doesn't exist
- Install/update dependencies
- Run the stock analysis

### Method 2: Direct Python Execution

If you prefer to run directly:

```bash
python stock.py <TICKER>
```

Or make the script executable and run:
```bash
chmod +x stock.py
./stock.py AAPL
```

### Example Output

```
================================================================================
STOCK FUNDAMENTALS ANALYSIS FOR: AAPL
================================================================================
Analysis Date: 2025-01-XX XX:XX:XX

================================================================================
0. PRICE INFORMATION
================================================================================
Current Price: $XXX.XX
YTD % Change: +X.XX%
YTD High (2025): $XXX.XX (on 2025-XX-XX)
YTD Low (2025): $XXX.XX (on 2025-XX-XX)
All-Time High: $XXX.XX (on YYYY-MM-DD)
All-Time Low: $XXX.XX (on YYYY-MM-DD)
...

[Additional sections with color-coded output]
```

## Color Coding

The output uses color coding for easy reading:

- **🟡 Yellow** - Current price, important metrics, ratios
- **🟢 Green** - Positive values, high prices, revenue, positive margins
- **🔴 Red** - Negative values, low prices, losses, negative percentages
- **🔵 Cyan** - Section headers and labels
- **⚪ White** - N/A values and informational text
- **🔵 Blue** - Main header and title

## Requirements

- Python 3.7+
- yfinance >= 0.2.28
- requests >= 2.31.0

All dependencies are listed in `requirements.txt`.

## Data Sources

This tool uses **yfinance** (Yahoo Finance API) which is:
- ✅ Free to use
- ✅ No API key required
- ✅ Provides real-time and historical stock data
- ✅ Includes financial statements and company information

## Limitations

Some metrics are marked as "N/A" because they require:
- **Qualitative analysis** - Business model details, competitive advantage, management quality
- **External macroeconomic APIs** - Interest rates, inflation (would require additional API keys)
- **Industry-specific research** - Market share, regulations, commodity prices

## Troubleshooting

### Error: "Could not fetch data for ticker XXX"
- Verify the ticker symbol is correct (e.g., AAPL, MSFT, TSLA)
- Check your internet connection
- Some tickers may not be available on Yahoo Finance

### Virtual Environment Issues
If you encounter issues with the virtual environment:
```bash
rm -rf venv
./run.sh <TICKER>
```

### Permission Denied (run.sh)
If you get a permission denied error:
```bash
chmod +x run.sh
./run.sh <TICKER>
```

## Project Structure

```
stock-finder/
├── stock.py          # Main application script
├── run.sh            # Automated setup and execution script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## License

This project is open source and available for personal and educational use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Disclaimer

This tool is for informational purposes only. It does not provide financial advice. Always do your own research and consult with a financial advisor before making investment decisions.

