import pandas as pd
from sqlalchemy import create_engine

# Define the file path
file_path = 'players.txt'

# Read the file into a pandas DataFrame
# Assuming the file is tab-separated and has no header
df = pd.read_csv(file_path, sep=',', header=None, names=['Team', 'Player', 'Price', 'Is_International', 'Role'])

# Display the DataFrame to verify
print(df.head())

# Database connection details
db_config = {
    'dbname': 'ipl25',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Create a connection string
connection_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

# Save the DataFrame to a PostgreSQL table
table_name = 'players'
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"Data has been successfully saved to the {table_name} table in the PostgreSQL database.")