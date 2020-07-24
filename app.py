from utils import *
app = dash.Dash(__name__)
server = app.server
######################################## MAIN APP #########################################
app.layout = html.Div(
    [
        # Banner display
        html.Div(
            className="header-title",
            children=[
                html.H2(
                    id="title",
                    children="Batch Jobs Tracker App",
                ),
            ],
        ),
        html.Div(
            id="grid",
            children=[
                html.Div(
                    id="controls",
                    className="six_columns",
                    children=[
                        html.Div(
                            id="dataset-picker",
                            children=[
                                html.Div(
                                    children=[
                                        html.H6(children="STATUS"),
                                        dcc.RadioItems(
                                            id='radio-items',
                    options = [
                        {'label': 'ALL', 'value': 'all'},
                        {'label': 'Not Started', 'value':'n'},
                        {'label': 'Started', 'value': 's'},
                        {'label': 'Completed', 'value': 'c'}
                        ],
                    value = "all",
                    labelStyle={'display': 'inline-block'}
                    ),
                                        html.Div(id="output-container"),
                                    ],
                                ),
                                # Strain dropdown picker
                            ],
                        ),
                    ],
                ),
                html.Div(
                    tb_color(get_df()),
                    id="leads_table", 
                    className="row pretty_container table"
                    ),
                html.Div(tb_out(pd.DataFrame({'Batch':[],'Details':[]})),id="leads_table1", className="row pretty_container table"),
                dcc.Graph(id="map-graph", className="div-card",figure=get_fig1(get_info('BATCH_1'),'LD_STRT_TS','LD_DURTN_SCND','LD_STRT_TS','LD_DURTN_SCND','30 Days Trend of Load Duration')),
                dcc.Graph(id="histo-graph", className="div-card",figure=get_fig1(get_info('BATCH_1'),'Date','End_Time','Date','End_Time','30 Days Trend of Load End Time')),
            ],
        ),
    ]
)

@app.callback(
    Output("leads_table", "children"),
    [Input("radio-items", "value")],
)
def leads_table_callback(val):
    df=get_df()#pd.read_csv('joined.csv')
    if val == "n":
        df = df[df['LD_STS']==' ']
    if val == "s":
        df = df[df['LD_STS']=='STARTED']
    elif val == "c":
        df = df[df['LD_STS']=='COMPLETED']
    else:
        df=df.copy()
    #df = df[["CreatedDate", "Status", "Company", "State", "LeadSource"]]
    return tb_color(df)

@app.callback(
    [Output('leads_table1', "children"),
    Output('map-graph','figure'),
    Output('histo-graph','figure')],
    [Input('leads_table2', "derived_virtual_data"),
     Input('leads_table2', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    dff=pd.DataFrame()
    b='BATCH_1'
    #dff=df.iloc[derived_virtual_selected_rows]
    if derived_virtual_selected_rows !=None:
        dff=pd.DataFrame(rows).iloc[derived_virtual_selected_rows]
    if dff.shape[0]==0:
        dffb=pd.DataFrame({'Batch':[],'Details':[]})
    else:
        dffa=dff
        b=dffa['BATCH NAME'].values[0]
        dffb=get_df1(b)

    return tb_out(dffb),get_fig1(get_info(b),'LD_STRT_TS','LD_DURTN_SCND','LD_STRT_TS','LD_DURTN_SCND','30 Days Trend of Load Duration'),get_fig1(get_info(b),'Date','End_Time','Date','End_Time','30 Days Trend of Load End Time')


if __name__ == "__main__":
    app.run_server(debug=False)
