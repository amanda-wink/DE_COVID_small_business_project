import folium
import os
import json
from sqlalchemy import create_engine
import pandas as pd
from datetime import date, timedelta, datetime


def make_map():
    #Saves environment variable to local variable
    mysql_pw = os.environ.get("SQL")

    #Creates connection to database
    engine = create_engine('mysql://'+ mysql_pw)
    con = engine.connect()
    df = pd.read_sql('covid_cases', con)

    #Finds most recent covid case rates
    df['Date'] = pd.to_datetime(df['Date'])
    recent_date = df['Date'].max()
    new = df.loc[df['Date'] == recent_date]
    current_cases = new[['Zipcode', 'Value']]

    #Finds yesterday's covid case rates
    yesterday_data = date.today() - timedelta(days=3)
    yesterday = yesterday_data.strftime('%Y%m%d')
    yesterday_date = datetime.strptime(yesterday, '%Y%m%d')
    yes_case = df.loc[(df['Date'] == yesterday_date)]
    yesterday_cases = yes_case[['Zipcode', 'Value']]

    #Dictionaries of zipcodes with covid rates
    current_dict = dict(zip(current_cases.Zipcode, current_cases.Value))
    yesterday_dict = dict(zip(yesterday_cases.Zipcode, yesterday_cases.Value))
    difference_dict = {key: current_dict[key] - yesterday_dict.get(key, 0) for key in current_dict}
    tomorrow_dict = {key: current_dict[key] + difference_dict.get(key, 0) for key in current_dict}

    #Predicts tomorrow's covid case rates
    tomorrow_cases = pd.DataFrame(list(tomorrow_dict.items()), columns=['Zipcode', 'Value'])

    #Opens geojson of Delaware's zip codes
    zipcodes = os.path.join("de_delaware_zip_codes_geo.min.json")

    #Sets maps coordinates to be Dover, Delaware when first opened
    m = folium.Map(location = [39.1582,-75.5244], zoom_start=8, overlay=True)

    #Creates Choropleth layer of Delaware's zip codes using today's values
    c1 = folium.Choropleth(
        geo_data = zipcodes,
        name = 'Current Cases',
        data = current_cases,
        columns = ['Zipcode','Value'],
        key_on = "properties.ZCTA5CE10",
        fill_color = 'YlOrRd',
        fill_opacity = 0.7,
        line_opacity = 0.3,
        legend_name = "Covid Cases (per 100,000 people)",
    ).add_to(m)

    #Creates Choropleth layer of Delaware's zip codes using yesterday's values
    c2 = folium.Choropleth(
        geo_data=zipcodes,
        name="Yesterday's Cases",
        data= yesterday_cases,
        columns=['Zipcode', 'Value'],
        key_on="properties.ZCTA5CE10",
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name="Covid Cases (per 100,000 people) yesterday",
        show=False,
    ).add_to(m)

    #Creates Choropleth layer of Delaware's zip codes using "tomorrow's" values
    c3 = folium.Choropleth(
        geo_data=zipcodes,
        name="Tomorrow's Cases",
        data= tomorrow_cases,
        columns=['Zipcode', 'Value'],
        key_on="properties.ZCTA5CE10",
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name="Covid Cases (per 100,000 people) Tomorrow",
        show=False,
    ).add_to(m)

    #When hovering over marker below message will pop up on screen
    tooltip = 'Click for More Info'

    #Opens geojsons of Delaware's zip code's center Lats/Longs
    file_path = 'markers.json'
    with open(file_path, 'r') as f:
        zipcode_central = json.load(f)


    #Creates markers for each zip code using today's data
    for key, item in zipcode_central.items():
        zipcode_cases = 0
        if int(key) in current_dict:
            zipcode_cases = current_dict[int(key)]

        folium.Marker(location=item,
                      #pops up when clicked
                      popup = folium.Popup(
                          (f'<strong>Zip Code:</strong> {key}<br>'
                           f'<strong>Number of Reported Cases per 100,000:</strong> {zipcode_cases}'),
                          max_width=300,min_width=300),
                      #hover over it says "message"
                      tooltip=tooltip).add_to(c1)

    #Creates markers for each zip code using yesterday's data
    for key, item in zipcode_central.items():
        zipcode_cases = 0
        if int(key) in yesterday_dict:
            zipcode_cases = yesterday_dict[int(key)]

        folium.Marker(location=item,
                      #pops up when clicked
                      popup = folium.Popup(
                          (f'<strong>Zip Code:</strong> {key}<br>'
                           f'<strong>Number of Reported Cases per 100,000:</strong> {zipcode_cases}'),
                          max_width=300,min_width=300),
                      #hover over it says "message"
                      tooltip=tooltip).add_to(c2)

    #Creates markers for each zip code using "tomorrow's" data
    for key, item in zipcode_central.items():
        zipcode_cases = 0
        if int(key) in tomorrow_dict:
            zipcode_cases = tomorrow_dict[int(key)]

        folium.Marker(location=item,
                      # pops up when clicked
                      popup=folium.Popup(
                          (f'<strong>Zip Code:</strong> {key}<br>'
                           f'<strong>Number of Reported Cases per 100,000:</strong> {round(zipcode_cases,2)}'),
                          max_width=300, min_width=300),
                      # hover over it says "message"
                      tooltip=tooltip).add_to(c3)



    #Allows for layer selection
    folium.LayerControl().add_to(m)
    #Saves map
    m.save('map.html')
    #return m

make_map()