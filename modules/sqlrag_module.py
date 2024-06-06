import logging
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, ForeignKeyConstraint, select, insert, update, ForeignKey
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from sqlalchemy import text
import os

from dotenv import load_dotenv
load_dotenv()
from llama_index.core.query_engine import NLSQLTableQueryEngine

llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
import streamlit as st
default_db_path = "db/test.db"

logging.basicConfig()
logger = logging.getLogger(__name__)

logger.setLevel(logging.WARNING)

def get_engine(db_path=default_db_path):
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    logger.info(f"Using database path: {db_path}")
    
    return create_engine(f"sqlite:///{db_path}", echo=True)

def create_users_table():
    try:
        engine = get_engine()
        metadata_obj = MetaData()
        table_name = "users"
        users_table = Table(
            table_name,
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(16), nullable=False),
            Column("email", String(32), nullable=False),
            Column("study_year", String(16), nullable=False),
            Column("about_me", String(256), nullable=False),
            Column("programming_knowledge", Integer, nullable=False),
        )
        metadata_obj.create_all(engine)
        logger.info(f"Table '{table_name}' created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating the table: {e}")


def insert_rows(table_name : str, rows):
    try:
        engine = get_engine()
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        with engine.begin() as connection:
            for row in rows:
                stmt = insert(table).values(**row)
                connection.execute(stmt)
                logger.info(f"Inserted row: {row}")

        logger.info(f"All rows inserted successfully into '{table_name}' table.")
    except Exception as e:
        logger.error(f"An error occurred while inserting rows: {e}")

def upsert_user(user_info):
    try:
        engine = get_engine()
        metadata = MetaData()
        table = Table("users", metadata, autoload_with=engine)

        # Check if user exists
        stmt = select(table).where(table.c.email == user_info["email"])
        with engine.connect() as connection:
            result = connection.execute(stmt).fetchone()
        
        if result:
            # User exists, update the record
            stmt = (
                update(table)
                .where(table.c.email == user_info["email"])
                .values(**user_info)
            )
            with engine.begin() as connection:
                connection.execute(stmt)
                logger.info(f"Updated row: {user_info}")
        else:
            # User does not exist, insert a new record
            stmt = insert(table).values(**user_info)
            with engine.begin() as connection:
                connection.execute(stmt)
                logger.info(f"Inserted row: {user_info}")

        logger.info(f"Upsert operation completed successfully for 'users' table.")
    except Exception as e:
        logger.error(f"An error occurred while upserting the user: {e}")

def get_user_by_email(email):
    try:
        engine = get_engine()
        metadata = MetaData()
        table = Table("users", metadata, autoload_with=engine)

        stmt = select(table).where(table.c.email == email)
        with engine.connect() as connection:
            result = connection.execute(stmt).fetchone()
        
        if result:
            user_info = {column.name: value for column, value in zip(table.columns, result)}
            logger.info(f"Retrieved user: {user_info}")
            return user_info
        else:
            logger.info(f"No user found with email: {email}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while retrieving the user: {e}")
        return None
    
 
def get_sql_engine(tables: list):
    print("tables included:", tables)
    sql_database = SQLDatabase(get_engine(), include_tables=tables)
    nl_sql_retriever = NLSQLRetriever(
    sql_database, tables=["users"], return_raw=True)
    query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever)
    return query_engine

def get_tables():
    engine = get_engine()
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        table_names = metadata.tables.keys()
        
        logger.info(f"Tables in the database: {table_names}")
        return list(table_names)
    except Exception as e:
        logger.error(f"An error occurred while retrieving the tables: {e}")
        return []

def create_pjs_points_table():
    try:
        engine = get_engine()
        metadata_obj = MetaData()
        table_name = "PJS_points"
        pjs_points_table = Table(
            table_name,
            metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
            Column("exam_1_points", Integer, nullable=False, default=0),
            Column("exam_2_points", Integer, nullable=False, default=0),
            Column("exam_3_points", Integer, nullable=False, default=0),
            Column("exam_4_points", Integer, nullable=False, default=0),
            Column("exam_5_points", Integer, nullable=False),
            Column("feedback", String(256), nullable=False)
        )
        metadata_obj.create_all(engine)
        logger.info(f"Table '{table_name}' created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating the table: {e}")


def insert_pjs_points(rows):
    try:
        engine = get_engine()
        metadata = MetaData()
        table = Table("PJS_points", metadata, autoload_with=engine)
        
        with engine.begin() as connection:
            for row in rows:
                stmt = insert(table).values(**row)
                connection.execute(stmt)
                logger.info(f"Inserted row: {row}")

        logger.info("All rows inserted successfully into 'PJS_points' table.")
    except Exception as e:
        logger.error(f"An error occurred while inserting rows: {e}")

def main():
    create_pjs_points_table()

    pjs_points_data = [
        {"user_id": 1, "exam_1_points": 85, "exam_2_points": 90, "exam_3_points": 78, "exam_4_points": 88, "exam_5_points": 92, "feedback": "Good progress overall, keep up the good work."},
    ]

    # Insert sample data into 'PJS_points' table
    insert_pjs_points(pjs_points_data)

if __name__ == "__main__":
    main()
