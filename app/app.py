import vis
import choropleth
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

data = vis.restrict_df()
delaware_df1, delware_df2 = vis.get_state_data()
merch_data_Kent, merch_data_New_Castle, merch_data_Sussex = vis.get_county_merch()
rev_data_Kent, rev_data_New_Castle, rev_data_Sussex = vis.get_county_rev()
de_merch, de_rev = vis.get_state_data()

#Names for the correlating industries
ss40 = "Trade, Transportation, and Utilities"
ss60 = "Professional and Business Services"
ss65 = "Education and Health Services"
ss70 = "Leisure and Hospitality"

input_merch_ind = [[str(ss40), str(ss60), str(ss65), str(ss70)], [de_rev] * 4,
                   ['revenue_ss40', 'revenue_ss60', 'revenue_ss65', 'revenue_ss70']]
input_rev_ind = [[str(ss40), str(ss60), str(ss65), str(ss70)], [de_merch] * 4,
                 ['merchants_ss40', 'merchants_ss60', 'merchants_ss65', 'merchants_ss70']]
input_state = [['Revenue', 'Merchants'], [de_rev, de_merch], ['revenue_all', 'merchants_all']]

#--------------------------------------
app.layout = html.Div([

    html.H1("Delaware Merchant Closings, Revenue Changes, and State COVID-19 Mitigation Strategies", style={'text-align': 'center'}),
    dcc.Dropdown(id='dropdown',
                options=[
                {"label":"Sussex County", "value":"Sussex"},
                {"label":"New Castle County", "value":"New Castle"},
                {"label":"Kent County", "value":"Kent"},
                {"label":"State Merchant Closings by Industry", "value":"Industry Merchant"},
                {"label":"State Revenue by Industry", "value":"Industry Revenue"},
                ],
                multi=False,
                value="Industry Revenue",
                style={'width':"50%"}
                ),

    dcc.Graph(id ="graph1", figure={"layout": {"height":'100vh'}}),

    html.H1("Interactive Data Modeling of Delaware's COVID-19 Cases", style={'text-align':'center'}),
    html.Iframe(id ='map', srcDoc=open('map.html','r').read(), height=600, width='100%',
                style={'textAlign':'center'}),

    dcc.Markdown('''
    This project was developed by Zip Code Wilmington data engineering students Luke Roy, Deana Stuart, and Amanda Winkelmayer.
    
    Learn more about our project on our [Github](https://github.com/deanastuart/DE_COVID_small_business_project).
    
    The data used is the most current data available from our sources as of 9 am today. 
    ### Data from:
    * Covid Case Data:
        * [Delaware Environmental Public Health Tracking Network](https://myhealthycommunity.dhss.delaware.gov/locations/state)
    * Business Data:
        * [The Economic Tracker](https://tracktherecovery.org) and [accompanying paper](https://opportunityinsights.org/wp-content/uploads/2020/05/tracker_paper.pdf.)
   * Mitigation Strategies:
        * [Delaware Health and Social Services](https://myhealthycommunity.dhss.delaware.gov/locations/state/coronavirus-mitigation#contact-tracing-timeline)
    ''')
    ])

#_________________________
@app.callback(
    [Output(component_id="graph1", component_property ="figure")],
    [Input(component_id="dropdown", component_property="value")],
)

def update_graph(var):
    if var == "Sussex":
        x = vis.fig3([['Revenue', 'Merchants'], [rev_data_Sussex, merch_data_Sussex], ['revenue_all', 'merchants_all']], data, "Sussex County")
    elif var == "New Castle":
        x = vis.fig3([['Revenue', 'Merchants'], [rev_data_New_Castle, merch_data_New_Castle], ['revenue_all', 'merchants_all']], data, "New Castle County")
    elif var == "Kent":
        x = vis.fig3([['Revenue', 'Merchants'], [rev_data_Kent, merch_data_Kent], ['revenue_all', 'merchants_all']], data, "Kent County")
    elif var == "Industry Merchant":
        x = vis.fig3(input_merch_ind, data, "Delaware Merchant Closing by Industry")
    elif var == "Industry Revenue":
        x = vis.fig3(input_rev_ind, data, "Delaware Revenue Gains and Losses by Industry")
    return [x]


if __name__ == '__main__':
    choropleth.make_map()
    app.run_server(debug=True)