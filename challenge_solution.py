import requests
import sqlite3
import sys
import re
import os
from datetime import datetime


#Input validation functions start here


def is_valid_url(url): #URL input validation, spaghetti regex, I know, but it works
    pattern = r"^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$"
    if re.match(pattern=pattern, string=url):
        return True
    raise Exception(f'The endpoint provided {url} is not a valid URL, please enter a valid endpoint')

def is_valid_range(size): #Checks whether the range contains a hyphen, ignores if range is in the wrong order
    if "-" in size:
        return True
    raise ValueError(f'Range {size} does not contain a range, denoted by a "-"')


#Retrieval and storage functions here:

def get_transactions(endpoint, starting_block, ending_block):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [],
        "id": 1
    } #Payload initialization, the params value will change based off of the calculated block number below. 
    transactions = [] #List for temporary storage of data

    for block_num in range(starting_block, ending_block + 1):
        payload["params"] = [hex(block_num), True] #Params value modified here
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "result" in data and data["result"] is not None:
                if data["result"]["transactions"]: #If data exists, then we initialize timestamp variable
                    timestamp = None
                    if "timestamp" in data["result"]:
                        timestamp = data["result"]["timestamp"]

                txs = data["result"]["transactions"] 
                for tx in txs:
                    transactions.append({
                        "hash": tx["hash"],
                        "blockHash": tx["blockHash"],
                        "blockNumber": tx["blockNumber"],
                        "from": tx["from"],
                        "to": tx["to"],
                        "value": tx["value"],
                        "timestamp": timestamp
                    })
            else:
                print(f"No transactions found for block {block_num}")
        else:
            print(f"Error fetching block {block_num}: HTTP Status Code {response.status_code}")

    return transactions

# Function to create a SQLite database and table if they don't exist
def create_database(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        hash TEXT PRIMARY KEY,
                        blockHash TEXT,
                        blockNumber TEXT,
                        sender TEXT,
                        receiver TEXT,
                        value TEXT,
                        timestamp TEXT
                    )''')
    conn.commit()
    conn.close()

# Function to insert transactions into the database
def persist_transactions(database, transactions):
    if len(transactions) > 0:
        print(f"Number of transactions to insert: {len(transactions)}") #Debugging print, not necessary, but helpful 
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        try:
            for tx in transactions:
                cursor.execute('''INSERT OR IGNORE INTO transactions (hash, blockHash, blockNumber, sender, receiver, value, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', #Abstraction here to prevent SQL Injection
                        (tx["hash"], tx["blockHash"], tx["blockNumber"], tx["from"], tx["to"], tx["value"], tx["timestamp"]))
        except sqlite3.Error as e:
            print(f'Error occured during insertion: {e}')
        finally:
            conn.commit()
            conn.close()
    else:
        print("No transactions to persist to SQLite database")





if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python challenge_solution.py <JSON-RPC Endpoint> <database> <starting_block-ending_block>")
        sys.exit(1)
    
    #Validate inputs before processing:
    try:
        if is_valid_url(sys.argv[1]):
            endpoint = sys.argv[1]
    except Exception as e:
        print({e})
        exit()

    
    try:
        if is_valid_range(sys.argv[3]):
            size = sys.argv[3]
            splits = size.split("-")
            start = int(min(splits))
            end = int(max(splits))
    except ValueError as v:
        print(v)
        exit()
    
    database = sys.argv[2]



    transactions = get_transactions(endpoint, start, end)
    create_database(database)
    persist_transactions(database, transactions)


    print(f"Transactions retrieved from {endpoint} and persisted to database.")
