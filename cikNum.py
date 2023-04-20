# Importing Libraries
import requests
import time
import schedule
import json
import os

# Fetches the CIK list from the SEC website
def get_cik_list():
    url = "https://www.sec.gov/include/ticker.txt"
    response = requests.get(url)

    if response.status_code == 200:
        cik_list = response.text.split('\n')
        cik_dict = {}

        for line in cik_list:
            if line:
                symbol, cik = line.split('\t')
                cik_dict[symbol] = cik

        return cik_dict
    else:
        print(f"Error {response.status_code}: Unable to fetch data from SEC")
        return None
    
#  Saves the CIK dictionary to a JSON file.
def save_cik_list(cik_dict):
    if not os.path.exists("cik_data"):
        os.mkdir("cik_data")
    with open("cik_data/cik_list.json", "w") as f:
        json.dump(cik_dict, f)

# Loads the saved CIK dictionary from the JSON file
def load_cik_list():
    with open("cik_data/cik_list.json", "r") as f:
        return json.load(f)
    
# Updates the CIK list
def update_cik_list():
    print("Updating CIK list...")
    cik_dict = get_cik_list()
    if cik_dict:
        save_cik_list(cik_dict)
        print("CIK list updated successfully.")
    else:
        print("Failed to update CIK list.")

# Returns the CIK number for a given ticker symbol
def get_cik_from_ticker(ticker):
    cik_dict = load_cik_list()
    return cik_dict.get(ticker.lower())

# 
def cik_main():
    if not os.path.exists("cik_data/cik_list.json"):
        update_cik_list()
    else:
        cik_dict = load_cik_list()

    # Schedule the update to run every day at 9:00 AM
    schedule.every().day.at("09:00").do(update_cik_list)

    while True:
        schedule.run_pending()
        time.sleep(60)
