import logging
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, ForeignKeyConstraint, select, insert, update, ForeignKey
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from sqlalchemy import text
import os

from dotenv import load_dotenv
load_dotenv()
import streamlit as st
 
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import BaseSynthesizer

logging.basicConfig()
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

def get_engine():
    db_path = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
    db_uri = f'sqlite:///{db_path}'
    engine = create_engine(db_uri)
    print("engine created successfully")
    return engine

def create_users_table():
    try:
        engine = get_engine()
        metadata_obj = MetaData()
        table_name = "users"
        users_table = Table(
            table_name,
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("first_name", String(16), nullable=False),
            Column("last_name", String(16), nullable=False),
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


def run_query(query_str):
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query_str))
            
            results = [row for row in result.fetchall()]
            
            logger.info(f"Query executed successfully: {query_str}")
            
            return results
    except Exception as e:
        logger.error(f"An error occurred while running the query: {e}")
        return None

class SQLQueryEngine(CustomQueryEngine):
    prompt: PromptTemplate
    llm: OpenAI

    def custom_query(self, query_str: str):
        llm_prompt = self.prompt.format(query_str=query_str)
        generated_query = self.llm.complete(llm_prompt)
        result = run_query(generated_query.text)
        answer = self.llm.complete(f"Answer the user question: ${query_str} based on the result from the database query: {result}. Answer in Croatian.")
        return str(answer)


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
            Column("users_id", Integer, ForeignKey('users.id'), nullable=False),
            Column("exam_1_points", Integer, nullable=False, default=0),
            Column("exam_2_points", Integer, nullable=False, default=0),
            Column("exam_3_points", Integer, nullable=False, default=0),
            Column("exam_4_points", Integer, nullable=False, default=0),
            Column("exam_5_points", Integer, nullable=False),
            Column("feedback", String(256), nullable=False)
        )
        metadata_obj.create_all(engine)
        logger.info(f"Table 'PJS_points' created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating the table 'PJS_points': {e}", exc_info=True)


def table_exists(table_name):
    engine = get_engine()
    metadata = MetaData()
    metadata.reflect(engine)
    return table_name in metadata.tables


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
        logger.error(f"An error occurred while inserting rows: {e}", exc_info=True)

def main():
    
    """
    # Verify if the table is created successfully
    if not table_exists("PJS_points"):
        logger.error("Table 'PJS_points' was not created successfully.")
        return
    points = [85, 90, 78, 88, 92]
    pjs_points_data = [
        {"user_id": 1, "exam_1_points": points[0], "exam_2_points": points[1], "exam_3_points": points[2], "exam_4_points": points[3], "exam_5_points": points[4], "exam_total_points": sum(points)},
    ]
    insert_pjs_points(pjs_points_data)

    """

    """
    sample_users = [
    {
        "first_name": "Pero",
        "last_name": "Perić",
        "email": "pperic@gmail.com",
        "study_year": "1. prijediplomski",
        "about_me": "Volim programirati u Pythonu.",
        "programming_knowledge": 8
    },
    {
        "first_name": "Ana",
        "last_name": "Anić",
        "email": "aanic@gmail.com",
        "study_year": "2. prijediplomski",
        "about_me": "Zanima me web razvoj i dizajn.",
        "programming_knowledge": 7
    },
    {
        "first_name": "Marko",
        "last_name": "Marić",
        "email": "mmaric@gmail.com",
        "study_year": "3. prijediplomski",
        "about_me": "Uživam u učenju o umjetnoj inteligenciji.",
        "programming_knowledge": 9
    },
    {
        "first_name": "Ivana",
        "last_name": "Ivić",
        "email": "iivic@gmail.com",
        "study_year": "1. diplomski",
        "about_me": "Volim raditi na projektima s otvorenim kodom.",
        "programming_knowledge": 8
    },
    {
        "first_name": "Petar",
        "last_name": "Petrović",
        "email": "ppetrovic@gmail.com",
        "study_year": "2. diplomski",
        "about_me": "Strastveni sam ljubitelj računalne grafike.",
        "programming_knowledge": 7
    },
    {
        "first_name": "Jelena",
        "last_name": "Jelić",
        "email": "jjelic@gmail.com",
        "study_year": "3. diplomski",
        "about_me": "Fokusiram se na razvoj mobilnih aplikacija.",
        "programming_knowledge": 9
    }
]

    
    insert_rows("users", sample_users)

    """
    sample_points = [
        {"user_id": 1, "exam_1_points": 75, "exam_2_points": 80, "exam_3_points": 85, "exam_4_points": 90, "exam_5_points": 95, "exam_total_points": 425},
        {"user_id": 2, "exam_1_points": 70, "exam_2_points": 75, "exam_3_points": 80, "exam_4_points": 85, "exam_5_points": 90, "exam_total_points": 400},
        {"user_id": 3, "exam_1_points": 80, "exam_2_points": 85, "exam_3_points": 90, "exam_4_points": 95, "exam_5_points": 100, "exam_total_points": 450},
        {"user_id": 4, "exam_1_points": 78, "exam_2_points": 82, "exam_3_points": 88, "exam_4_points": 91, "exam_5_points": 94, "exam_total_points": 433},
        {"user_id": 5, "exam_1_points": 72, "exam_2_points": 76, "exam_3_points": 79, "exam_4_points": 84, "exam_5_points": 88, "exam_total_points": 399},
        {"user_id": 6, "exam_1_points": 85, "exam_2_points": 89, "exam_3_points": 92, "exam_4_points": 96, "exam_5_points": 99, "exam_total_points": 461},
    ]

    insert_pjs_points(sample_points)


if __name__ == "__main__":
    main()
