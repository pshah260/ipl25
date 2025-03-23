import pandas as pd
from sqlalchemy import create_engine

# Define the file path
file_path = 'schedule.txt'

# Read the file into a pandas DataFrame
df = pd.read_csv(file_path, sep='\t')

# Extract Home Team and Away Team from the Fixture column
df[['Home Team', 'Away Team']] = df['Fixture'].str.split(' vs ', expand=True)

# Preprocess the Date column to extract only the valid date part (e.g., "March 22")
df['Date'] = df['Date'].str.extract(r'([A-Za-z]+\s+\d+)')[0]

# Convert the Date column to a datetime object
df['Date'] = pd.to_datetime(df['Date'], format='%B %d')

# Update the year to 2025
df['Date'] = df['Date'].apply(lambda x: x.replace(year=2025))

# Add a new column for Day (extracted from the Date column)
df['Day'] = df['Date'].dt.day_name()

# Reorder columns to match the desired output
df = df[['Match', 'Date', 'Day', 'Fixture', 'Home Team', 'Away Team', 'Venue']]

# Display the transformed DataFrame
print("Transformed DataFrame:")
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
table_name = 'schedule'  # Replace with your desired table name
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"\nData has been successfully saved to the {table_name} table in the PostgreSQL database.")