import pandas as pd
from sqlalchemy import create_engine
import os

def update_data():
    #webscraping
    page_url = "https://myhealthycommunity.dhss.delaware.gov/locations/state/coronavirus-mitigation#contact-tracing-timeline"
    list1 = pd.read_html(page_url)
    df = list1[0]
    df = df.rename(columns={'From': 'Start'})
    #cleaning the data
    df["Start"].apply(lambda x: str(2020) + " " + x)
    df["Start"] = df["Start"].apply(lambda x: str(2020) + " " + x)
    df["Start"] = pd.to_datetime(df["Start"], format="%Y %b %d")
    df.loc[(df.Until != 'Further Notice'), 'Until'] = df["Until"].apply(lambda x: str(2020) + " " + x)
    df["Until"] = pd.to_datetime(df.loc[(df.Until != 'Further Notice'), 'Until'], format="%Y %b %d")
    df = df.drop(['Status'], axis=1)

    #Gets MySQL password from my local machine
    mysql_connection = os.environ.get("group_sql")

    #Create connection to MySQL database
    engine = create_engine(mysql_connection)

    #Drops yesterday's steam table
    connection = engine.raw_connection()
    cursor = connection.cursor()
    command = "DROP TABLE IF EXISTS {};".format('mitigation')
    cursor.execute(command)

    #uploads today's mitigation table
    df.to_sql('mitigation',con=engine, index=False)

update_data()
