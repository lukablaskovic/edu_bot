import logging
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, insert, update
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from sqlalchemy import text
import os

from dotenv import load_dotenv
load_dotenv()
from llama_index.core.query_engine import NLSQLTableQueryEngine
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

default_db_path = "db/test.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_engine(db_path = default_db_path):
    return create_engine(f"sqlite:///{db_path}", echo=True)


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
        return None-

def main():
    engine = get_engine(default_db_path)
    metadata_obj = MetaData()
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("country", String(16), nullable=False),
    )
    metadata_obj.create_all(engine)
        
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])

    # Uncomment to insert initial rows
    
    rows = [
        {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
        {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
        {"city_name": "Chicago", "population": 2679000, "country": "United States"},
        {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
    ]

    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            cursor = connection.execute(stmt)
            logger.info(f"Inserted row: {row}")

    stmt = select(
        city_stats_table.c.city_name,
        city_stats_table.c.population,
        city_stats_table.c.country,
    ).select_from(city_stats_table)

    with engine.connect() as connection:
        results = connection.execute(stmt).fetchall()
        logger.info("Current table contents:")
        for result in results:
            logger.info(result)


    # Uncomment to fetch rows
    """
    with engine.connect() as con:
        rows = con.execute(text("SELECT city_name from city_stats"))
    for row in rows:
        print(row)
    """

    # Text-to-SQL Query Engine
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=["city_stats"], llm=llm
    )
    query_str = "Which city has the highest population?"
    response = query_engine.query(query_str)

    print("RESPONSE", response)

if __name__ == "__main__":
    main()
