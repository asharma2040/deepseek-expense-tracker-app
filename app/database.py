import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database credentials from .env
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
# DB_HOST = creds.POSTGRES_HOST
# DB_PORT = creds.POSTGRES_PORT
# DB_USER = creds.POSTGRES_USER
# DB_PASSWORD = creds.POSTGRES_PASSWORD
# DB_NAME = creds.POSTGRES_DB

# Establish database connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

# Create transactions table if it doesn't exist
def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS bank_transactions (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        date DATE NOT NULL,
        posting_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('Income', 'Expense')),
        description TEXT NOT NULL,
        month_year VARCHAR(7) NOT NULL
    );
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

# Insert transactions into the database (avoid duplicates)
def insert_transactions(df):
    conn = get_db_connection()
    cursor = conn.cursor()

    # print(DB_NAME)

    # SQL Query for inserting data (ignores duplicates)
    insert_query = """
    INSERT INTO bank_transactions (name, date, posting_date, amount, transaction_type, description, month_year)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    # Convert DataFrame to a list of tuples
    records = df[['Name', 'date', 'posting_date', 'amount', 'transaction_type', 'description', 'month_year']].values.tolist()

    # Execute batch insert
    cursor.executemany(insert_query, records)
    conn.commit()

    cursor.close()
    conn.close()

# Fetch transactions for a specific user
def get_transactions(name):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM bank_transactions WHERE name = %s ORDER BY date DESC"
    cursor.execute(query, (name,))
    records = cursor.fetchall()

    # Convert results to DataFrame
    columns = [ 'name', 'date', 'posting_date', 'amount', 'transaction_type', 'description', 'month_year']
    df = pd.DataFrame(records, columns=columns)

    cursor.close()
    conn.close()
    
    return df
