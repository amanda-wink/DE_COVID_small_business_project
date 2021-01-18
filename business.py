import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, Date, String


def connect_sql():
    """
    Connects to SQL. Requires SQL credentials being set in your env.

    :return: Connection to SQL
    """
    sql = os.getenv('SQL')
    str_sql = 'mysql+mysqlconnector://' + sql
    engine = create_engine(str_sql)
    return engine

def convert_time(dataframe):
    """
    Converts year, month, day columns to a datetime object and adds a date column.

    :param dataframe: dataframe with year, month, day columns
    :return: dataframe with a date column containing datetime objects
        and the year, month, day columns dropped
    """
    dataframe.replace({'month': {1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6:'06', 7:'07', 8:'08', 9:'09'},
                        'day': {1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6:'06', 7:'07', 8:'08', 9:'09'}}, inplace=True)
    dataframe['date'] = dataframe['year'].apply(str) + dataframe['month'].apply(str) + dataframe['day'].apply(str)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d', utc=False)
    dataframe.drop(columns=['year', 'month', 'day'], inplace = True)
    return dataframe

def get_data():
    """
    Pulls all four files from github to dataframes

    :return: List of dataframes
    """
    url='https://raw.githubusercontent.com/OpportunityInsights/EconomicTracker/main/data/'
    files = ['Womply%20Merchants%20-%20County%20-%20Daily.csv','Womply%20Merchants%20-%20State%20-%20Daily.csv','Womply%20Revenue%20-%20County%20-%20Daily.csv','Womply%20Revenue%20-%20State%20-%20Daily.csv']
    list_df = []
    for file in range(len(files)):
        dataframe = pd.read_csv(url + files[file])
        list_df.append(dataframe)
    print('Files acquired')
    return list_df

def setup_tables():
    """
    Creates 4 permanent tables if they do not exist in the database.
    Only run when you are first setting up the database.

    :return: None
    """
    con = connect_sql()
    meta = MetaData()

    tables_county('merchants', 'county_merch', meta)
    tables_state('merchants', 'state_merch', meta)
    tables_county('revenue', 'county_rev', meta)
    tables_state('revenue', 'state_rev', meta)

    meta.create_all(con)
    print("All tables have been created.")

def setup_temp_tables():
    """
    Creates 4 temporary tables. Used for make sure only
    new data is added to the permanent table.

    :return: None
    """

    con = connect_sql()
    meta = MetaData()

    tables_county('merchants', 'county_merch_temp', meta)
    tables_state('merchants', 'state_merch_temp', meta)
    tables_county('revenue', 'county_rev_temp', meta)
    tables_state('revenue', 'state_rev_temp', meta)

    meta.create_all(con)
    print("All temp tables have been created.")

def tables_state(type, name, meta):
    """
    Structures the table for the state revenue and state merchants files.

    :param type: String. Either 'revenue' or 'merchant' depending on the table being set up
    :param name: String representing the name of the table
    :param meta: Metadata() from sqlalchemy
    :return: None
    """
    state_table = Table(
        str(name), meta,
        Column('statefips', Integer),
        Column(str(type) + '_all', Float),
        Column(str(type) + '_inchigh', Float),
        Column(str(type) + '_inclow', Float),
        Column(str(type) + '_incmiddle', Float),
        Column(str(type) + '_ss40', Float),
        Column(str(type) + '_ss60', Float),
        Column(str(type) + '_ss65', Float),
        Column(str(type) + '_ss70', Float),
        Column('date', Date),
        Column('loc_date', String(20), primary_key=True)
    )

def tables_county(type, name, meta):
    """
    Structures the table for the county revenue and county merchants files.

    :param type: String. Either 'revenue' or 'merchant' depending on the table being set up
    :param name: String representing the name of the table
    :param meta: Metadata() from sqlalchemy
    :return: None
    """
    county_table = Table(
        str(name), meta,
        Column('countyfips', Integer),
        Column(str(type) + '_all', Float),
        Column('date', Date),
        Column('loc_date', String(20), primary_key=True)
    )

def write_sql(dataframe, engine, table):
    """
    Writes to SQL a database

    :param dataframe: Dataframe to be written
    :param engine: Connection to SQL
    :return: None
    """
    dataframe.to_sql(table, engine, if_exists='append', index=False)
    engine.dispose()
    print('Written to SQL.')

def main():
    """
    Gets updated data and adds it to the correct tables.

    :return: None
    """
    con = connect_sql()

    list_df = get_data()
    setup_temp_tables()

    #bus_county = pd.read_csv('Data/update/Womply_Merchants_County_Daily.csv')
    bus_county = list_df[0]
    bus_county = convert_time(bus_county)
    bus_county['loc_date'] = bus_county['countyfips'].astype(str) + " " + bus_county['date'].astype(str)
    write_sql(bus_county, con, 'county_merch_temp')
    con.execute('INSERT IGNORE INTO county_merch SELECT * FROM county_merch_temp')
    con.execute('DROP TABLE county_merch_temp;')

    #bus = pd.read_csv('Data/update/Womply_Merchants_State_Daily.csv')
    bus = list_df[1]
    bus = convert_time(bus)
    bus['loc_date'] = bus['statefips'].astype(str) + " " + bus['date'].astype(str)
    write_sql(bus, con, "state_merch_temp")
    con.execute('INSERT IGNORE INTO state_merch SELECT * FROM state_merch_temp')
    con.execute('DROP TABLE state_merch_temp;')

    #bus_county_rev = pd.read_csv('Data/update/Womply_Revenue_County_Daily.csv')
    bus_county_rev = list_df[2]
    bus_county_rev = convert_time(bus_county_rev)
    bus_county_rev['loc_date'] = bus_county_rev['countyfips'].astype(str) + " " + bus_county_rev['date'].astype(str)
    write_sql(bus_county_rev, con, 'county_rev_temp')
    con.execute('INSERT IGNORE INTO county_rev SELECT * FROM county_rev_temp')
    con.execute('DROP TABLE county_rev_temp;')
    
    #bus_rev = pd.read_csv('Data/update/Womply_Revenue_State_Daily.csv')
    bus_rev = list_df[3]
    bus_rev = convert_time(bus_rev)
    bus_rev['loc_date'] = bus_rev['statefips'].astype(str) + " " + bus_rev['date'].astype(str)
    write_sql(bus_rev, con, 'state_rev_temp')
    con.execute('INSERT IGNORE INTO state_rev SELECT * FROM state_rev_temp')
    con.execute('DROP TABLE state_rev_temp;')

    print("All tables writen to SQL")

if __name__ == "__main__":
    #setup_tables()
    main()