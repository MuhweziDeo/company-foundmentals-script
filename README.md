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

### 📈 Earnings Trend

- Historical earnings data (quarterly or annual)
- Period-over-period percentage changes
- Overall trend direction (increasing/decreasing/stable)
- Last 8 periods displayed

### 📊 Analyst Ratings & Price Targets

- Average, High, and Low price targets
- Upside/Downside percentage vs current price
- Average recommendation (Strong Buy, Buy, Hold, Underperform, Sell)
- Recommendation breakdown by category
- Recent analyst recommendations with firm names and dates

### 📉 Price Action Trend & Swing Structures (1D Timeframe)

- **Trend Analysis**: Determines uptrend, downtrend, or sideways based on swing structure
- **Current Swing High/Low**: Most recent swing points with prices and dates
- **Swing Structure Pattern**: Identifies classic patterns (higher highs/lows, lower highs/lows, potential reversals)
- **Recent Swing History**: Last 5 swing highs and lows with comparison to previous swings

### 🎯 Trading Recommendation

- **Comprehensive Analysis**: Combines price action, analyst ratings, and RSI indicators
- **Buy/Sell/Hold Signal**: Clear recommendation with strength indicator
- **Score Breakdown**: Shows contribution from each indicator (Price Action, Analyst Ratings, RSI)
- **Detailed Reasoning**: Explains why each indicator contributes to the recommendation
- **Risk Assessment**: Includes disclaimer about using technical analysis for investment decisions

### 🌍 Macroeconomic & Sector Metrics

- **Interest Rate** (Federal Funds Rate) - From FRED API
- **Inflation** (CPI Year-over-Year) - From FRED API
- **Unemployment Rate** - From FRED API
- **Real GDP** - From FRED API
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

3. **Set up FRED API Key (Optional but Recommended)**

   To get macroeconomic data (interest rates, inflation, unemployment, GDP), you need a free FRED API key:

   - Get your free API key from: https://fred.stlouisfed.org/docs/api/api_key.html
   - Set it as an environment variable:

   **On macOS/Linux:**

   ```bash
   export FRED_API_KEY="your_api_key_here"
   ```

   **On Windows (PowerShell):**

   ```powershell
   $env:FRED_API_KEY="your_api_key_here"
   ```

   **On Windows (Command Prompt):**

   ```cmd
   set FRED_API_KEY=your_api_key_here
   ```

   **Persistent setup (recommended):**

   Add to your `~/.bashrc`, `~/.zshrc`, or `~/.profile`:

   ```bash
   export FRED_API_KEY="your_api_key_here"
   ```

   **Note:** If the FRED API key is not set, the program will still work but macroeconomic data will show as "N/A". The program will display a note indicating that the API key is not set.

4. **Use the automated setup script:**
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

This tool uses multiple data sources:

### yfinance (Yahoo Finance API)

- ✅ Free to use
- ✅ No API key required
- ✅ Provides real-time and historical stock data
- ✅ Includes financial statements and company information

### FRED API (Federal Reserve Economic Data)

- ✅ Free to use (requires free API key)
- ✅ Provides macroeconomic data:
  - Federal Funds Rate (Interest Rates)
  - Consumer Price Index (Inflation)
  - Unemployment Rate
  - Real GDP
- 🔑 Get your free API key: https://fred.stlouisfed.org/docs/api/api_key.html
- Set the `FRED_API_KEY` environment variable to enable macroeconomic data

## Limitations

Some metrics are marked as "N/A" because they require:

- **Qualitative analysis** - Business model details, competitive advantage, management quality
- **FRED API Key** - Interest rates, inflation, unemployment, and GDP data require a FRED API key (set via `FRED_API_KEY` environment variable). If not set, these metrics will show as "N/A"
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

### FRED API Key Not Working

If macroeconomic data shows as "N/A":

- Verify your API key is set correctly: `echo $FRED_API_KEY` (macOS/Linux) or `echo %FRED_API_KEY%` (Windows)
- Make sure you've exported the environment variable in your current shell session
- Check that your API key is valid at https://fred.stlouisfed.org/docs/api/api_key.html
- The program will work without the API key, but macroeconomic metrics will be unavailable

## Project Structure

```
stock-finder/
├── stock.py          # Main application script
├── run.sh            # Automated setup and execution script
├── requirements.txt   # Python dependencies
├── README.md         # This file
├── LICENSE           # MIT License with liability disclaimers
├── DISCLAIMER.md     # Comprehensive disclaimer and liability notice
└── helpers/          # Helper modules
    ├── __init__.py
    ├── calculators.py    # Technical analysis calculations
    ├── constants.py      # Constants and configuration
    ├── data_fetcher.py   # Data fetching functions
    ├── display.py        # Display formatting functions
    ├── export.py         # Export to Excel/PDF functions
    └── formatters.py     # Number/price formatting utilities
```

## Export Options

The tool supports exporting analysis data to Excel (.xlsx) or PDF (.pdf) formats:

```bash
python stock.py AAPL -o analysis.xlsx
python stock.py AAPL -o report.pdf
```

## License

This project is licensed under the MIT License with additional liability disclaimers. See [LICENSE](LICENSE) file for details.

## Disclaimer & Liability

**IMPORTANT: USE AT YOUR OWN RISK**

This tool is provided for informational and educational purposes only. It does NOT provide financial, investment, or trading advice. See [DISCLAIMER.md](DISCLAIMER.md) for complete disclaimer and liability information.

**Key Points:**
- ⚠️ **Not Financial Advice**: All recommendations and analysis are for informational purposes only
- ⚠️ **Use at Your Own Risk**: You are solely responsible for any investment decisions
- ⚠️ **No Warranty**: The software is provided "as is" without any warranties
- ⚠️ **No Liability**: The authors and contributors are not liable for any losses or damages
- ⚠️ **Do Your Own Research**: Always consult with qualified financial advisors before making investment decisions

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- Data provided by Yahoo Finance (via yfinance)
- Macroeconomic data from FRED (Federal Reserve Economic Data)
