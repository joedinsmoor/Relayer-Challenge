import sqlite3
from datetime import datetime, timezone, timedelta


def datetime_to_hex_timestamp(dt): #Created because I was getting weird timezone issues that would return the timezone in GMT-5:00 instead of GMT-0:00
    dt_utc = dt.replace(tzinfo=timezone.utc)
    timestamp_utc = int(dt_utc.timestamp())
    hex_timestamp = hex(timestamp_utc)
    return hex_timestamp

def find_block_with_largest_volume(database, start_time, end_time):

    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    start_hex = datetime_to_hex_timestamp(start_dt) #Converts timestamps to hex as that is how they are retrieved and stored
    end_hex = datetime_to_hex_timestamp(end_dt)

    # Connect to the database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Execute SQL query to fetch block numbers and transaction values
    cursor.execute('''SELECT blockNumber, value
                      FROM transactions
                      WHERE timestamp BETWEEN ? AND ?''',
                   (start_hex, end_hex))
    
    # Fetch all rows
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Calculate total volume transferred for each block
    block_volumes = {}
    for block_number, value_hex in rows:
        # Convert hexadecimal value to decimal and then to ether
        value_eth = int(value_hex, 16) / 1e18
        # Update total volume transferred for the block
        block_volumes[block_number] = block_volumes.get(block_number, 0) + value_eth

    # Find the block with the largest volume transferred
    if block_volumes:
        block_number_with_largest_volume = max(block_volumes, key=block_volumes.get)
        largest_volume_transferred = block_volumes[block_number_with_largest_volume]
        return block_number_with_largest_volume, largest_volume_transferred
    else:
        return None, None


#Actual query and return here, I hardcoded timestamps here, but feel free to test with other timestamps
print("Database to query: ")
database = input()
start = "2024-01-01 00:00:00"
end = "2024-01-01 00:30:00"

result = find_block_with_largest_volume(database, start, end)

if result:
    block_number, total_volume_transferred = result
    print(f"Block number with the largest volume transferred: {block_number}")
    print(f"Total volume transferred for that block: {total_volume_transferred}")
else:
    print("No data found for the specified time range.")