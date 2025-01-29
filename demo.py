import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('logs.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Get the schema of the 'logs' table
cursor.execute("PRAGMA table_info(logs);")
columns = cursor.fetchall()

# Print the column details
print("Schema for table 'logs':")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")

# Close the connection
conn.close()
