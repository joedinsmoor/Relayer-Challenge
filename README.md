# Relayer-Challenge
My solution to the technical challenge for Relayer



Usage: 
```$ python challenge_solution.py https://rpc.quicknode.pro/$YOURAPIKEY db.sqlite3 200-300```


## Some explanation around my thought processes in certain spots:

### The Query Script
- Due to some odd behavior with the sqlite db, I ended up performing the query in a weird way, my original method of summing the value column and sorting by descending total had issues, so instead I performed the summing calculations in the python script, and got the volume and block number that way. 

### General Speed
- The retrieval function ```get_transactions()``` is pretty slow, if threading were introduced, and rate limits weren't a concern, this would be much much faster. Apart from the actual requests, the rest of the script is nearly instant

### Data Persistence
- In the data persistence function ```persist_transactions()```, I chose to leave a diagnostic print that would print out the number of transactions that would be sent to the SQLite database, but it is not really necessary beyond pure diagnostics. 

## Link to additional informational video:
[Loom Video](https://www.loom.com/share/2d70676c350a4261918e71b1ba9ce870?sid=b90b837a-4e3e-4ee9-b2c9-83fc8fb21255)