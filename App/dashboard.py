import os
from collections import defaultdict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import func, inspect, Table, MetaData
from .database import Session, engine  # import your DB setup

metadata = MetaData()


# Database configuration from environment variables
DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

# Connect to MySQL
import pymysql
pymysql.install_as_MySQLdb()
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"
engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# List all your transaction tables (sanitized names)
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

def fetch_transactions(user_id=None):
    """Fetch all transactions from all tables and return as dict of lists"""
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            query = text(f"SELECT date, amount FROM {table} WHERE user_id = :user_id")
            result = session.execute(query,  {"user_id": user_id}).fetchall()
            transactions = [{'date': row[0], 'amount': row[1]} for row in result if row[1] is not None]
            all_data[table] = transactions
    return all_data

# === Individual chart functions ===

def get_transaction_volume_by_type(all_data):
    labels = TRANSACTION_TABLES
    data = [len(all_data[t]) for t in labels]
    return labels, data

def get_transaction_amount_by_type(all_data):
    labels = TRANSACTION_TABLES
    data = [sum(txn['amount'] for txn in all_data[t]) for t in labels]
    return labels, data

def get_monthly_transaction_trends(all_data):
    monthly_counter = defaultdict(int)
    for txns in all_data.values():
        for txn in txns:
            if txn['date']:
                month_str = txn['date'].strftime('%Y-%m')
                monthly_counter[month_str] += 1
    labels = sorted(monthly_counter.keys())
    data = [monthly_counter[m] for m in labels]
    return labels, data

def get_transaction_distribution(all_data):
    labels = TRANSACTION_TABLES
    volume_data = [len(all_data[t]) for t in labels]
    total_txns = sum(volume_data)
    data = [(v / total_txns * 100 if total_txns else 0) for v in volume_data]
    return labels, data

def get_average_transaction_amount(all_data):
    labels = TRANSACTION_TABLES
    data = []
    for t in labels:
        amounts = [txn['amount'] for txn in all_data[t]]
        data.append(sum(amounts)/len(amounts) if amounts else 0)
    return labels, data

metadata = MetaData()

def get_total_transactions(user_id=None):
    """
    Count all transactions across all dynamic tables, optionally filtered by user_id.
    """
    total = 0
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with Session() as session:
        for table_name in tables:
            table = Table(table_name, metadata, autoload_with=engine)

            query = session.query(func.count()).select_from(table)

            # If user_id filter is provided, apply it
            if user_id is not None and 'user_id' in table.c:
                query = query.filter(table.c.user_id == user_id)

            count = query.scalar() or 0
            total += count

    return total



def get_total_amount(user_id=None):
    """
    Sum all amounts across all dynamic tables for a given user_id (if provided).
    """
    total_amount = 0.0
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with Session() as session:
        for table_name in tables:
            table = Table(table_name, metadata, autoload_with=engine)

            # Only proceed if the table has an 'amount' column
            if "amount" in [c.name for c in table.columns]:
                query = session.query(func.sum(table.c.amount))

                # Add user_id filter if requested and table has user_id column
                if user_id and "user_id" in [c.name for c in table.columns]:
                    query = query.filter(table.c.user_id == user_id)

                amount_sum = query.scalar() or 0.0
                total_amount += amount_sum

    return total_amount



def get_most_used_transaction_type(user_id=None):
    """
    Find the most used transaction type for the given user_id.
    If user_id is None, consider all users.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    type_counts = {}

    with Session() as session:
        for table_name in tables:
            table = Table(table_name, metadata, autoload_with=engine)

            if "tra_type" in [c.name for c in table.columns] and "user_id" in [c.name for c in table.columns]:
                query = session.query(
                    table.c.tra_type,
                    func.count().label("count")
                )

                # Apply filter if user_id is passed
                if user_id is not None:
                    query = query.filter(table.c.user_id == user_id)

                query = query.group_by(table.c.tra_type)

                counts = query.all()

                for tra_type, count in counts:
                    type_counts[tra_type] = type_counts.get(tra_type, 0) + count

    if not type_counts:
        return None

    most_used = max(type_counts.items(), key=lambda x: x[1])
    return {"transaction_type": most_used[0], "count": most_used[1]}

# === Example usage ===
if __name__ == "__main__":
    all_data = fetch_transactions(user_id=1)
    
    labels, data = get_transaction_volume_by_type(all_data)
    print("Volume by Type:", labels, data)

    labels, data = get_transaction_amount_by_type(all_data)
    print("Amount by Type:", labels, data)

    labels, data = get_monthly_transaction_trends(all_data)
    print("Monthly Trends:", labels, data)

    labels, data = get_transaction_distribution(all_data)
    print("Distribution:", labels, data)

    labels, data = get_average_transaction_amount(all_data)
    print("Average Amount:", labels, data)
    print("Total transactions:", get_total_transactions())
    print("Total amount:", get_total_amount())
    print("Most used transaction type:", get_most_used_transaction_type())