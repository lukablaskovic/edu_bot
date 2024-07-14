import os

import logging
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, insert, update, ForeignKey, text
from sqlalchemy.schema import CreateTable

from dotenv import load_dotenv
load_dotenv()
from llama_index.llms.ollama import Ollama
from llama_index.llms.anthropic import Anthropic

from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from llama_index.core.query_engine import CustomQueryEngine

logging.basicConfig()
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

def get_engine():
    db_path = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
    db_uri = f'sqlite:///{db_path}'
    engine = create_engine(db_uri)
    return engine

def get_sql_template(schemas_str: str):
    sql_prompt = PromptTemplate(
                    f"Context information is below.\n"
                    f"---------------------\n"
                    f"You are a professional SQL developer. You are given a task to write a SQL query to retrieve data from the database.\n"
                    f"You must ALWAYS return SQL query only and nothing else.\n"
                    f"---------------------\n"
                    f"{schemas_str}\n"
                    f"---------------------\n"
                    f"Given the database schemas and example rows, structure the SQL query from given User prompt\n"
                    f"User prompt: {{query_str}}\n"
                )
    return sql_prompt

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
        logger.debug(f"Engine created: {engine}")

        with engine.connect() as connection:
            logger.debug(f"Executing query: {query_str}")

            result = connection.execute(text(query_str))
            
            results = [row for row in result.fetchall()]
            
            logger.info(f"Query executed successfully: {query_str}")
            logger.debug(f"Number of rows returned: {len(results)}")
            
            for row in results:
                logger.debug(f"Row: {row}")

            return results
    except Exception as e:
        logger.error(f"An error occurred while running the query: {e}")
        return None

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

def get_create_table_statement(table_name: str) -> str:
    try:
        engine = get_engine()
        metadata = MetaData()
        metadata.reflect(bind=engine)

        if table_name not in metadata.tables:
            raise ValueError(f"Table '{table_name}' does not exist in the database.")

        table = metadata.tables[table_name]
        create_table_stmt = str(CreateTable(table))

        return create_table_stmt
    except Exception as e:
        logger.error(f"An error occurred while generating the CREATE TABLE statement: {e}")
        return None

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

class SQLQueryEngine(CustomQueryEngine):
    """Custom query engine for SQL queries."""

    llm_openai: OpenAI | None
    llm_ollama: Ollama | None
    llm_anthropic: Anthropic | None
    prompt: PromptTemplate

    def custom_query(self, query_str: str):
        if self.llm_openai is not None:
            llm = self.llm_openai
        elif self.llm_ollama is not None:
            llm = self.llm_ollama
        elif self.llm_anthropic is not None:
            llm = self.llm_anthropic
        else:
            raise ValueError("No LLM available for querying.")

        llm_prompt = self.prompt.format(query_str=query_str)
        
        generated_query = llm.complete(llm_prompt)
        
        query_normalized = remove_sql_markdown(generated_query.text)
        
        # Run the SQL query
        result = run_query(query_normalized)
        
        print(f"SQL result: {result}")
        
        st.session_state["generated_query.text"] = query_normalized
        
        #answer_prompt = f"Answer the user question: {query_str} based on the result from the database query: {result}. Answer in Croatian."
        #answer = llm.complete(answer_prompt)
        
        return str(result)
        return str(answer)


def remove_sql_markdown(input_string: str) -> str:
    if input_string.startswith("```sql") and input_string.endswith("```"):
        return input_string[6:-3].strip()
    return input_string



def main():
    
    table_name = "users"
    create_table_stmt = get_create_table_statement(table_name)
    if create_table_stmt:
        print(create_table_stmt)


if __name__ == "__main__":
    main()
