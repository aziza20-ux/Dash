import re
import uuid
import os
from .parser import parser
from sqlalchemy import Column, String, create_engine, DateTime, Float, text, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
DB = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_NAME")
HOST = os.getenv("HOST")
PASSWORD = os.getenv("PASSWORD")

# Connect to MySQLpip
try:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        connection_string = f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}:3306/{DB}"
        engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Connected successfully to {DB} using MySQLdb.")
    except ModuleNotFoundError:
        connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"
        engine = create_engine(connection_string, pool_pre_ping=True, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Connected successfully to {DB} using PyMySQL.")
except Exception as e:
    raise ConnectionError(f"Error connecting to {DB}: {e}")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def sanitize_table_name(name: str) -> str:
    cleaned_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name).lower()
    return re.sub(r'_{2,}', '_', cleaned_name).strip('_')

def inserting_in_database(parsed_data: dict, user_id: int):
    with SessionLocal() as session:
        for table_name, transactions in parsed_data.items():
            table_name_safe = sanitize_table_name(table_name)

            # Define dynamic table class
            attrs = {
                '__tablename__': table_name_safe,
                'id': Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
                'date': Column(DateTime),
                'tra_type': Column(String(255)),
                'new_balance': Column(Float),
                'transaction_id': Column(String(255)),
                'receiver_name': Column(String(255)),
                'fee': Column(Float),
                'amount': Column(Float),
                'agent_number': Column(String(255)),
                'sender_number': Column(String(255)),
                'receiver_number': Column(String(255)),
                'sender_name': Column(String(255)),
                'third_party_name': Column(String(255)),
                'user_id':Column(Integer, nullable=False)
            }
            DynamicTable = type(table_name_safe, (Base,), attrs)

            try:
                DynamicTable.__table__.create(bind=engine, checkfirst=True)
            except Exception as e:
                print(f"Error creating table '{table_name_safe}': {e}")
                continue

            rows_to_insert = []
            for txn in transactions:
                txn['user_id'] = user_id
                # Clean numeric fields before inserting
                if 'amount' in txn and txn['amount'] is not None:
                    txn['amount'] = float(str(txn['amount']).replace(',', ''))
                if 'fee' in txn and txn['fee'] is not None:
                    txn['fee'] = float(str(txn['fee']).replace(',', ''))

                filtered_data = {k: v for k, v in txn.items() if v is not None}
                if 'id' not in filtered_data:
                    filtered_data['id'] = str(uuid.uuid4())
                row_instance = DynamicTable(**filtered_data)
                rows_to_insert.append(row_instance)

            if rows_to_insert:
                try:
                    session.add_all(rows_to_insert)
                    session.commit()
                    print(f"{len(rows_to_insert)} rows inserted into '{table_name_safe}' table.")
                except Exception as e:
                    session.rollback()
                    print(f"Failed to insert rows into '{table_name_safe}': {e}")
            else:
                print(f"No valid transactions for table '{table_name_safe}'.")
if __name__ == '__main__':
    file_path = r'C:\Users\user\Desktop\Dash\App\data.xml'
    parsed_data = parser(file_path)
    inserting_in_database(parsed_data)
    print('done inserting')
    #result = parser('sample_sms.xml')
