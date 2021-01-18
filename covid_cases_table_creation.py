from sqlalchemy import create_engine, Column,VARCHAR, INT, DATE, FLOAT, Table
from sqlalchemy.sql.schema import MetaData
import os

url = os.getenv('URL')
engine = create_engine(url)
metadata = MetaData()

covid_cases_temp = Table('covid_cases_temp', metadata,
    Column('Zipcode', INT),
    Column('County', VARCHAR(45)),
    Column('Statistic', VARCHAR(60)),
    Column('Value', FLOAT),
    Column('Date used', VARCHAR(45)),
    Column('Unit', VARCHAR(100)),
    Column('Age adjusted', VARCHAR(60)),
    Column('Zipcode Population', INT),
    Column('Date', DATE),
    Column('Zipcode Date', VARCHAR(45), primary_key=True),
    Column('Zipcode latitude', FLOAT),
    Column('Zipcode longitude', FLOAT),)


covid_cases = Table('covid_cases', metadata,
    Column('Zipcode', INT),
    Column('County', VARCHAR(45)),
    Column('Statistic', VARCHAR(60)),
    Column('Value', FLOAT),
    Column('Date used', VARCHAR(45)),
    Column('Unit', VARCHAR(100)),
    Column('Age adjusted', VARCHAR(60)),
    Column('Zipcode Population', INT),
    Column('Date', DATE),
    Column('Zipcode Date', VARCHAR(45), primary_key=True),
    Column('Zipcode latitude', FLOAT),
    Column('Zipcode longitude', FLOAT),)

def create():
    metadata.create_all(engine)

if __name__ == "__main__":
    create()