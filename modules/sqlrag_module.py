import logging
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, insert
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI

llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

db_path = "db/test.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    def main():
        engine = create_engine(f"sqlite:///{db_path}", echo=True)
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
        logger.info(f"Table '{table_name}' created successfully.")

        sql_database = SQLDatabase(engine, include_tables=["city_stats"])

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
      
    main()
