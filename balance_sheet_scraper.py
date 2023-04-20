# Importing Libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import warnings
from cikNum import *
from concurrent.futures import ThreadPoolExecutor

# defining headers and warnings to ignore
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

warnings.filterwarnings('ignore', category=FutureWarning)

# Extracting the links for the tables
def extract_link(ticker, cik_num):
    search_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + ticker + "&type=10-K&dateb=&owner=exclude&count=40"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "tableFile2"})
    if table is None:
        print(f"Table not found for ticker {ticker}")
        return []
    link = table.find_all("a")[1]["href"]
    acc_link = table.find_all("a")[0]["href"]
    acc_url = "https://www.sec.gov" + acc_link
    response = requests.get(acc_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    acc_num_section = soup.find("div" , {"id": "secNum"})
    acc_num = acc_num_section.strong.next_sibling.strip()
    modif_acc_num = acc_num.replace("-", "")
    filing_data_url = "https://www.sec.gov" + link
    response = requests.get(filing_data_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    pattern = r"/Archives/edgar/data/" + cik_num + "/" + modif_acc_num + "/R[0-9]+\.htm"
    matches = re.findall(pattern, str(soup))
    selected_indices = [0,1,2,3,4,5,6,7,8]
    result_links = [matches[i] for i in selected_indices]
    for i in range(len(result_links)):
        result_links[i] = "https://www.sec.gov" + result_links[i]
    return result_links

# Storing the table data in a list
def data_list(result_links):
    with ThreadPoolExecutor() as executor:
        table_data = list(executor.map(get_table_data, result_links))
    return table_data

def get_table_data(link):
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    if re.search("Parenthetical", soup.get_text(), flags=re.IGNORECASE):
        return None

    # Check if the text "balance sheet" is present in the content
    if re.search(r'(?i)balance sheet', soup.get_text()):
        table = soup.find("table", {"class": "report"})
        return table

    return None

# Formatting the data stored in table_data
def formatting_data(table_data):
    with ThreadPoolExecutor() as executor:
        dataframe_list = list(executor.map(format_single_data, table_data))
    dataframe_list = [df for df in dataframe_list if df is not None]
    return dataframe_list

def format_single_data(table):
    if table is None:
        return None

    df = pd.read_html(str(table))[0]

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map('_'.join)

    # Remove the duplicate empty column
    first_col_name = df.columns[0]
    duplicate_columns = df.columns[df.columns == first_col_name].tolist()
    if len(duplicate_columns) > 1:
        df = df.drop(duplicate_columns[1], axis=1)

    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df = df.drop(df.index[0])
    cols_to_convert = df.columns[1:]
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('$', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace(',', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('(', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace(')', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('%', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace(' ', ''))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('nan', '0'))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('None', '0'))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('N/A', '0'))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('n/a', '0'))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('N/a', '0'))
    df[cols_to_convert] = df[cols_to_convert].astype(str).apply(lambda x: x.str.replace('—', '0'))
    df = df[:-1]

    # Check if the DataFrame is empty before returning it
    if not df.empty:
        return df
    return None

# Printing the table data
if __name__ == "__main__":
    # Taking user input for the company's ticker and CIK number
    ticker = input("Enter the ticker of the company: ")
    cik_dict = get_cik_list()
    save_cik_list(cik_dict)
    load_cik_list()
    cik_num = get_cik_from_ticker(ticker)

    result_links = extract_link(ticker, cik_num)
    table_data = data_list(result_links)
    table_data = [data for data in table_data if data is not None]
    dataframe_list = formatting_data(table_data)

    print(dataframe_list)

    # convert the dataframe to an excel file
    convert = input("Do you want to convert the table to an excel file? (y/n): ")
    if convert == "y":
        for i, df in enumerate(dataframe_list):
            df.to_excel(f"table_{i}.xlsx")
    else:
        pass