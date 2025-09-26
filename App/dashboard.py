import os
import pymysql
from collections import defaultdict
from sqlalchemy import create_engine, text, func, inspect, Table, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime

metadata = MetaData()

# Database configuration from environment variables
DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

# Connect to MySQL
pymysql.install_as_MySQLdb() 
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"
engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Session Manager
class SessionManager:
    """Simple context manager to mimic the imported Session()"""
    def __enter__(self):
        self.session = SessionLocal()
        return self.session
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

Session = SessionManager 

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

# ----------------------------------------------------------------------
## Helper Function for User ID Determination

def has_user_transactions(user_id):
    """Quickly checks if a specific user_id has any transactions."""
    if not user_id:
        return False
    
    with Session() as session:
        for table_name in TRANSACTION_TABLES:
            try:
                query_str = f"SELECT 1 FROM {table_name} WHERE user_id = :user_id LIMIT 1"
                query = text(query_str)
                result = session.execute(query, {"user_id": user_id}).fetchone()
                
                if result:
                    return True
            except Exception:
                continue
    return False

def get_user_id_for_query(logged_in_user_id):
    """
    Determines which user_id to query: logged-in user's ID or None (for sample data).
    Returns: int or None: The user ID to use for database queries (None implies user_id IS NULL).
    """
    if logged_in_user_id is None:
        return None
    
    # Check if the logged-in user has any data uploaded
    if has_user_transactions(logged_in_user_id):
        return logged_in_user_id # User has data, fetch their data
    else:
        return None # User has no data, return None to trigger sample data query

# ----------------------------------------------------------------------
## Data Fetching Functions

def fetch_transactions(user_id=None):
    """
    Fetch transactions. If user_id is None, it fetches records where user_id IS NULL (sample data).
    """
    all_data = {}
    with SessionLocal() as session:
        for table in TRANSACTION_TABLES:
            
            query_str = f"SELECT date, amount FROM {table}"
            params = {}
            conditions = []
            
            try:
                # Use 'autoload_with=engine' to inspect the table for column presence
                table_meta = Table(table, metadata, autoload_with=engine)
            except Exception:
                all_data[table] = []
                continue

            # --- Query Logic ---
            if "user_id" in [c.name for c in table_meta.columns]:
                if user_id is not None:
                    conditions.append("user_id = :user_id")
                    params["user_id"] = user_id
                else:
                    conditions.append("user_id IS NULL")
            # -------------------
            
            if conditions:
                 query_str += " WHERE " + " AND ".join(conditions)
            
            query = text(query_str)
            try:
                result = session.execute(query, params).fetchall()
                transactions = [{'date': row[0], 'amount': row[1]} for row in result if row[1] is not None]
                all_data[table] = transactions
            except Exception as e:
                # print(f"Warning: Could not query table {table}. Error: {e}")
                all_data[table] = []
                
    return all_data

def get_total_transactions(user_id=None):
    """Count transactions. If user_id is None, it counts records where user_id IS NULL."""
    total = 0
    inspector = inspect(engine)
    try:
        tables = inspector.get_table_names()
    except Exception:
        return 0

    with Session() as session:
        for table_name in tables:
            try:
                table = Table(table_name, metadata, autoload_with=engine)
            except Exception:
                continue

            query = session.query(func.count()).select_from(table)

            if "user_id" in [c.name for c in table.columns]:
                if user_id is not None:
                    query = query.filter(table.c.user_id == user_id)
                else:
                    query = query.filter(table.c.user_id.is_(None))

            try:
                count = query.scalar() or 0
                total += count
            except Exception:
                continue
                
    return total

def get_total_amount(user_id=None):
    """Sum amounts. If user_id is None, it sums records where user_id IS NULL."""
    total_amount = 0.0
    inspector = inspect(engine)
    try:
        tables = inspector.get_table_names()
    except Exception:
        return 0.0

    with Session() as session:
        for table_name in tables:
            try:
                table = Table(table_name, metadata, autoload_with=engine)
            except Exception:
                continue

            if "amount" in [c.name for c in table.columns]:
                query = session.query(func.sum(table.c.amount))

                if "user_id" in [c.name for c in table.columns]:
                    if user_id is not None:
                        query = query.filter(table.c.user_id == user_id)
                    else:
                        query = query.filter(table.c.user_id.is_(None))

                try:
                    amount_sum = query.scalar() or 0.0
                    total_amount += amount_sum
                except Exception:
                    continue

    return total_amount

def get_most_used_transaction_type(user_id=None):
    """Find the most used transaction type. If user_id is None, considers transactions where user_id IS NULL."""
    inspector = inspect(engine)
    try:
        tables = inspector.get_table_names()
    except Exception:
        return None
    
    type_counts = {}

    with Session() as session:
        for table_name in tables:
            try:
                table = Table(table_name, metadata, autoload_with=engine)
            except Exception:
                continue

            if "tra_type" in [c.name for c in table.columns] and "user_id" in [c.name for c in table.columns]:
                query = session.query(
                    table.c.tra_type,
                    func.count().label("count")
                )

                if user_id is not None:
                    query = query.filter(table.c.user_id == user_id)
                else:
                    query = query.filter(table.c.user_id.is_(None))

                query = query.group_by(table.c.tra_type)

                try:
                    counts = query.all()
                    for tra_type, count in counts:
                        type_counts[tra_type] = type_counts.get(tra_type, 0) + count
                except Exception:
                    continue

    if not type_counts:
        return None

    most_used = max(type_counts.items(), key=lambda x: x[1])
    return {"transaction_type": most_used[0], "count": most_used[1]}

# ----------------------------------------------------------------------
## Chart Helper Functions

def get_transaction_volume_by_type(all_data):
    labels = TRANSACTION_TABLES
    data = [len(all_data[t]) for t in labels]
    return labels, data

def get_transaction_amount_by_type(all_data):
    labels = TRANSACTION_TABLES
    data = [sum(txn['amount'] for txn in all_data[t] if txn.get('amount') is not None) for t in labels]
    return labels, data

def get_monthly_transaction_trends(all_data):
    monthly_counter = defaultdict(int)
    for txns in all_data.values():
        for txn in txns:
            if txn['date']:
                date_obj = txn['date']
                if not isinstance(date_obj, datetime):
                    try:
                        date_obj = datetime.strptime(str(date_obj).split(' ')[0], '%Y-%m-%d')
                    except:
                        continue 
                
                month_str = date_obj.strftime('%Y-%m')
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
        amounts = [txn['amount'] for txn in all_data[t] if txn.get('amount') is not None]
        data.append(sum(amounts)/len(amounts) if amounts else 0)
    return labels, data

if __name__ == "__main__":
    pass