import pandas as pd
import os
from sqlalchemy import create_engine
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def connect_sql():
    """
    Connects to SQL. Requires SQL credentials being set in your env.

    :return: Connection to SQL
    """
    sql = os.environ['SQL']
    str_sql = 'mysql+mysqlconnector://' + sql
    engine = create_engine(str_sql)
    return engine

def get_state_data():
    """
    Gets merchant and revenue data from SQL for Delaware

    :return: Dataframes of merchant and revenue data for the state
    """
    con = connect_sql()
    de_merch = pd.read_sql('select * from state_merch where statefips = 10;',con)
    de_rev = pd.read_sql('select * from state_rev where statefips = 10', con)
    return de_merch, de_rev

def get_county_merch():
    """
    Gets merchant data from SQL for each Delaware county

    :return: A dataframe for each county
    """
    con = connect_sql()
    Kent_m = pd.read_sql('select date, merchants_all from county_merch where countyfips = 10001;', con)
    NCC_m = pd.read_sql('select date, merchants_all from county_merch where countyfips = 10003;', con)
    Sussex_m = pd.read_sql('select date, merchants_all from county_merch where countyfips = 10005;', con)
    return Kent_m, NCC_m, Sussex_m

def get_county_rev():
    """
    Gets revenue data from SQL for each Delaware county

    :return: A dataframe for each county
    """
    con = connect_sql()
    Kent_r = pd.read_sql('select date, revenue_all from county_rev where countyfips = 10001;', con)
    NCC_r = pd.read_sql('select date, revenue_all from county_rev where countyfips = 10003;', con)
    Sussex_r = pd.read_sql('select date, revenue_all from county_rev where countyfips = 10005;', con)
    return Kent_r, NCC_r, Sussex_r

def get_restrictions():
    """
    Gets dataframe of restrictions. Creates of list of lists.


    :return: A list of lists. First list is dates in ascending order.
    The second list is an integer used as a marker for the restriction.
    The third is the mitigations put in place on that date.
    """
    con = connect_sql()
    restrict = pd.read_sql('select * from mitigation;', con)
    restriction = [[],[],[]]
    event = 1
    for index, row in restrict.iterrows():
        date = row['Start']
        if index == 0 or date != restriction[0][0]:
            restriction[0].insert(0, date)
            restriction[1].insert(0, event)
            restriction[2].insert(0, str(row['Mitigation']))
            event += 1
        else:
            restriction[2][0] += ', ' + str(row['Mitigation'])

    return restriction

def restrict_df():
    """
    Flips the numbering for the events from desc to asc order and makes the date a date object.

    :return: Dataframe with event number, date, and mitigation
    """
    restrictions = get_restrictions()
    restrict_line = []

    for i in range(len(restrictions[0])):
        event_flip = len(restrictions[1]) - restrictions[1][i] + 1
        line = (event_flip, pd.to_datetime(restrictions[0][i]).date(), restrictions[2][i])
        restrict_line.append(line)
    restrict_date = pd.DataFrame(restrict_line, columns=['event', 'date', 'mitigation'])

    return restrict_date

def max_val2(df, column):
    """
    Calculates the max value of the data. Used for the mitigation lines on the graph.

    :param df: List of dataframes
    :param column: List of strings representing the columns in the dataframe of which to calculate the max
    :return: Float of max value turned into a percentage
    """
    maxs = []
    for ind in range(len(df)):
        maxs.append(df[ind][str(column[ind])].max())
    val_max = max(maxs)
    return val_max * 100

def min_val2(df, column):
    """
    Calculates the min value of the data. Used for the mitigation lines on the graph.

    :param df: List of dataframes
    :param column: List of strings representing the columns in the dataframe of which to calculate the min
    :return: Float of min value turned into a percentage
    """
    mins = []
    for ind in range(len(df)):
        mins.append(df[ind][str(column[ind])].min())
    val_min = min(mins)
    return val_min * 100

def fig3(data, restrictions, title):
    """
    Creates a line graph of the data you give it and the government restrictions

    :param data: A list of lists
                data[0]: strings representing each set of data for the legend
                data[1]: dataframes
                data[2]: strings representing the columns you want to graph
    :param restrictions: dataframe of restrictions
    :param title: String representing the title of the graph
    :return: None
    """
    max = max_val2(data[1], data[2])
    min = min_val2(data[1], data[2])

    fig = go.Figure()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        specs=[[{"type": "scatter"}],
               [{"type": "table"}]]
    )

    for i in range(len(data[1])):
        fig.add_trace(go.Scatter(x=data[1][i]['date'], y=data[1][i][str(data[2][i])] * 100, name=data[0][i]), row=1, col=1)

    marker = []
    for index, row in restrictions.iterrows():
        marker.append({'type': 'line',
                       'xref': 'x',
                       'yref': 'y',
                       'x0': row['date'],
                       'y0': min - 5,
                       'x1': row['date'],
                       'y1': max +20})
        if index % 2 == 0:
            y = max + 24.5
        elif index % 2 != 0:
            y = max + 28.5
        fig.add_annotation(x=row['date'], y=y,
                           text=str(row['event']),
                           showarrow=False,
                           textangle=-90,
                           align='center', font=dict(size=8)
                           )

    fig.update_layout(plotly.graph_objs.Layout(shapes=marker))

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Events", "Date", "Mitigation"],
                font=dict(size=14),
                align="center"
            ),
            cells=dict(
                values=[restrictions[k].tolist() for k in restrictions.columns[0:]],
                align="center")
        ),
        row=2, col=1
    )

    fig.update_layout(height=800, title=title, title_x=0.5, xaxis=dict(title='Date'),
                      yaxis=dict(title='(%)'))
    return fig

if __name__ == "__main__":
    #Gets the dataframe of restrictions
    restrict = restrict_df()

    #Gets the dataframes with state and county business data
    de_merch, de_rev = get_state_data()
    Kent_m, NCC_m, Sussex_m = get_county_merch()
    Kent_r, NCC_r, Sussex_r = get_county_rev()

    #Names for the correlating industries
    ss40 = "Trade, Transportation, and Utilities"
    ss60 = "Professional and Business Services"
    ss65 = "Education and Health Services"
    ss70 = "Leisure and Hospitality"

    #Sets up list of lists for the first input to the graph
    #First list: Strings for legend. Second list: Dataframes, Third list: String of column name to get data
    input_r = [['Kent', 'New Castle', 'Sussex'],[Kent_r, NCC_r, Sussex_r], ['revenue_all']*3]
    input_m = [['Kent', 'New Castle', 'Sussex'], [Kent_m, NCC_m, Sussex_m], ['merchants_all']*3]
    input_state = [['Revenue', 'Merchants'], [de_rev, de_merch], ['revenue_all', 'merchants_all']]
    input_state_40 = [['Revenue', 'Merchants'], [de_rev, de_merch], ['revenue_ss40', 'merchants_ss40']]
    input_state_70 = [['Revenue', 'Merchants'], [de_rev, de_merch], ['revenue_ss70', 'merchants_ss70']]
    input_merch_ind = [[str(ss40), str(ss60), str(ss65), str(ss70)], [de_rev] * 4, ['revenue_ss40', 'revenue_ss60', 'revenue_ss65', 'revenue_ss70']]
    input_rev_ind = [[str(ss40), str(ss60), str(ss65), str(ss70)], [de_merch] * 4, ['merchants_ss40', 'merchants_ss60', 'merchants_ss65', 'merchants_ss70']]

    #Graphs
    fig3(input_r, restrict, "Revenue")
    fig3(input_m, restrict, "Merchants")
    #fig3(input_state, restrict, "Delaware Revenue and Merchants")
    #fig3(input_state_40, restrict, "Delaware Revenue and Merchants " + str(ss40))
    #fig3(input_state_70, restrict, "Delaware Revenue and Merchants " + str(ss70))
    fig3(input_merch_ind, restrict, "Delaware Merchants by Industry")
    fig3(input_rev_ind, restrict, "Delaware Revenue by Industry")

    fig3([['Revenue', 'Merchants'], [Sussex_r, Sussex_m], ['revenue_all', 'merchants_all']], restrict, "Sussex County")
    fig3([['Revenue', 'Merchants'], [Kent_r, Kent_m], ['revenue_all', 'merchants_all']], restrict, "Kent County")
    fig3([['Revenue', 'Merchants'], [NCC_r, NCC_m], ['revenue_all', 'merchants_all']], restrict, "New Castle County")


