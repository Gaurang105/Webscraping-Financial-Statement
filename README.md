
# SEC 10-K Balance Sheet Scraper

This Python script allows users to scrape Balance Sheet from a company's 10-K filings on the U.S. Securities and Exchange Commission (SEC) website. The script automatically formats the extracted tables and provides an option to save the output as Excel files.


## Features

- Extracts financial statements from 10-K filings on the SEC's EDGAR database
- Concurrently downloads and processes data using ThreadPoolExecutor for faster performance
- Automatically formats the extracted tables for easier analysis
- Provides an option to save the output as Excel files
## Dependencies

- requests
- pandas
- beautifulsoup4
- re
- warnings
- concurrent.futures

To install the dependencies, run:

```bash
pip install requests pandas beautifulsoup4
```

## Usage

1. Clone or download the repository.
2. Run the script by executing python balance_sheet_scraper.py in your terminal.
3. Enter the ticker symbol of the company you want to extract financial statements for.
4. The script will display the extracted tables as pandas dataframes.
5. Enter y if you want to save the tables as Excel files, or n to skip this step.
## Example

```python
Enter the ticker of the company: AAPL
[...output...]
Do you want to convert the table to an excel file? (y/n): y

```

