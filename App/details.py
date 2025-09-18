import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pymysql # Ensure pymysql is installed
from datetime import datetime # Import datetime for type checking if needed

# Assuming you have these environment variables set correctly
DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

# Connect to MySQL
try:
    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"
    engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
    # Test connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Database connection successful.")
except Exception as e:
    print(f"Error connecting to database: {e}")
    # Depending on your app structure, you might want to exit or raise an exception here
    # For a Flask app, you'd typically handle this in your app factory or main app file.
    engine = None # Set engine to None if connection fails

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

TRANSACTION_TABLES = [
    'bank_transfers',
    'withdrawals_from_agents',
    'transactions_initiated_by_third_parties',
    'bundle_purchases',
    'cash_power_bill_payments',
    'airtime_bill_payments',
    'bank_deposits',
    'transfers_to_mobile_numbers',
    'payments_to_code_holders',
    'incoming_money'
]

def fetch_tra_details(user_id=None):
    if not engine:
        # Handle the case where the database connection failed
        # You might want to return an empty dict or raise a specific error
        return {}
        
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            # Ensure table name is safe Aif it comes from user input (though here it's static)
            # A more robust check might involve inspecting actual table names from metadata
            safe_table_name = table # In this case, we trust TRANSACTION_TABLES

            # Use parameterized query for the LIMIT
            query = text(f"SELECT amount, date, tra_type FROM {safe_table_name} WHERE user_id = :user_id  ORDER BY date DESC")
            try:
                # Pass the limit parameter using a dictionary
                result = session.execute(query, {"user_id": user_id}).fetchall()
                
                transactions = []
                for row in result:
                    # Ensure the date object is correctly handled. SQLAlchemy usually returns datetime objects.
                    # You might need to ensure your column type in the database is DATETIME or TIMESTAMP.
                    transactions.append({
                        'amount': row[0],
                        'date': row[1], # This should already be a datetime object from SQLAlchemy
                        'tra_type': row[2]
                    })
                all_data[table] = transactions
            except Exception as e:
                # Log the error for debugging
                print(f"Error fetching data from table {table}: {e}")
                all_data[table] = [] # Assign an empty list if an error occurs for a specific table
    return all_data
def fetch_filtered_tra_details(user_id=None, start_date=None, end_date=None, transaction_type=None):
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            # Base query
            query_str = f"SELECT amount, date, tra_type FROM {table} WHERE 1=1"
            params = {}

            # Add user filter if provided
            if user_id:
                query_str += " AND user_id = :user_id"
                params['user_id'] = user_id

            # Add a start date filter if provided
            if start_date:
                query_str += " AND date >= :start_date"
                params['start_date'] = start_date

            # Add an end date filter if provided
            if end_date:
                query_str += " AND date <= :end_date"
                params['end_date'] = end_date

            # Add transaction type filter if provided & matches the table
            if transaction_type and transaction_type.lower().replace(' ', '_') == table:
                query_str += " AND tra_type = :tra_type"
                params['tra_type'] = transaction_type.replace(' ', '_')

            # Order by date descending
            query_str += " ORDER BY date DESC"

            # Execute
            query = text(query_str)
            result = session.execute(query, params).fetchall()

            transactions = [
                {'amount': row[0], 'date': row[1], 'tra_type': row[2]}
                for row in result
            ]

            # Only add data if no specific type filter OR if it matches this table
            if not transaction_type or (transaction_type and transaction_type.lower().replace(' ', '_') == table):
                all_data[table] = transactions

    return all_data

if __name__ == '__main__':
    data = fetch_filtered_tra_details(transaction_type= 'incoming_money')
    print(data)