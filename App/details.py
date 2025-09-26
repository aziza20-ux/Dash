import os
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime 

DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

try:
    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"
    engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Database connection successful.")
except Exception as e:
    print(f"Error connecting to database: {e}")
    engine = None 

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

# ---
## fetch_tra_details (UPDATED LOGIC)

def fetch_tra_details(user_id=None):
    if not engine:
        return {}
        
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            query_str = f"SELECT amount, date, tra_type FROM {table}"
            params = {}
            conditions = []

            if user_id is not None:
                conditions.append("user_id = :user_id")
                params['user_id'] = user_id
            else: 
                conditions.append("user_id IS NULL")
            
            if conditions:
                query_str += " WHERE " + " AND ".join(conditions)
            
            query_str += " ORDER BY date DESC"

            try:
                query = text(query_str)
                result = session.execute(query, params).fetchall()
                
                transactions = [
                    {'amount': row[0], 'date': row[1], 'tra_type': row[2]}
                    for row in result
                ]
                all_data[table] = transactions
            except Exception as e:
                print(f"Error fetching data from table {table}: {e}")
                all_data[table] = [] 
    return all_data

# ---
## fetch_filtered_tra_details (UPDATED LOGIC)

def fetch_filtered_tra_details(user_id=None, start_date=None, end_date=None, transaction_type=None):
    if not engine:
        return {}
        
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            query_str = f"SELECT amount, date, tra_type FROM {table}"
            params = {}
            conditions = []

            if user_id is not None:
                conditions.append("user_id = :user_id")
                params['user_id'] = user_id
            else:
                conditions.append("user_id IS NULL")

            if start_date:
                conditions.append("date >= :start_date")
                params['start_date'] = start_date

            if end_date:
                conditions.append("date <= :end_date")
                params['end_date'] = end_date

            if transaction_type and transaction_type.lower().replace(' ', '_') == table:
                conditions.append("tra_type = :tra_type")
                params['tra_type'] = transaction_type.replace(' ', '_')

            if conditions:
                query_str += " WHERE " + " AND ".join(conditions)

            query_str += " ORDER BY date DESC"

            query = text(query_str)
            try:
                result = session.execute(query, params).fetchall()

                transactions = [
                    {'amount': row[0], 'date': row[1], 'tra_type': row[2]}
                    for row in result
                ]

                if not transaction_type or (transaction_type and transaction_type.lower().replace(' ', '_') == table):
                    all_data[table] = transactions
            except Exception as e:
                print(f"Error fetching filtered data from table {table}: {e}")
                all_data[table] = []

    return all_data
if __name__ == "__main__":
    # NOTE: This will now attempt to fetch data where user_id IS NULL
    print("--- Fetching Sample Data (user_id=None, expects user_id IS NULL) ---")
    sample_data = fetch_tra_details(user_id=None)
    print(sample_data)