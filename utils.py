import pandas as pd
import plotly.express as px
import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime

# Following function get data for plotting the graph1 and graph2 on the App
def get_info(batch):    
    ld_info=pd.read_csv("ld_info.csv")
    ld_info['LD_STRT_TS']=pd.to_datetime(ld_info['LD_STRT_TS'].str.split(' EDT').str[0])
    ld_info['LD_END_TS']=pd.to_datetime(ld_info['LD_END_TS'].str.split(' EDT').str[0])
    ld_info['Date']=pd.to_datetime(ld_info['LD_STRT_TS'].dt.date)
    ld_info1=ld_info[ld_info['LD_STRT_TS']>(datetime.datetime.today()-datetime.timedelta(30))]
    ld_info2=ld_info1[ld_info1['BTCH_NM']==batch]
    ld_info2=ld_info2.sort_values('LD_STRT_TS')
    ld_info2['End_Time']=ld_info2['LD_END_TS'].dt.hour
    return ld_info2

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

# Following function plots the line graphs give x,y, titles
def get_fig1(df,x,y,x_title=' ',y_title=' ',tt=' '):
    fig1 = px.scatter(df, x=x, y=y,title=tt).update_traces(mode='lines+markers',marker_color='white',line_color='white').update_layout(dict(
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "white"},
            height=300,
            xaxis={
                "showline": True,
                "zeroline": False,
                "title":x_title, 
            },
            yaxis={
                "showgrid": True,
                "showline": True,
                "fixedrange": True,
                "zeroline": False,
                "gridcolor": app_color["graph_line"],
                "nticks": max(6, round(len(df[y]) / 10)),
                "title":y_title,
            },
        ))
    return fig1


# Following function loads the data and creates the 1st table in the App.
def get_df():
    ld_info=pd.read_csv("ld_info.csv")
    ld_info['LD_STRT_TS']=pd.to_datetime(ld_info['LD_STRT_TS'].str.split(' EDT').str[0])
    ld_info['LD_END_TS']=pd.to_datetime(ld_info['LD_END_TS'].str.split(' EDT').str[0])
    ld_info['Date']=pd.to_datetime(ld_info['LD_STRT_TS'].dt.date)
    ld_info=ld_info[ld_info['Date']==ld_info['Date'].max()]
    batch=pd.read_csv('BATCH_SLA.csv',encoding= 'unicode_escape')
    df=pd.merge(batch,ld_info.rename(columns={'BTCH_NM':'BATCH_NAME'}),on='BATCH_NAME',how='left')
    df['LD_STS']=df['LD_STS'].str.strip().fillna(' ')
    df=df.drop('Date',axis=1)
    df=df[df['LD_STS']!='ABORTED']
    df.columns=['BATCH TYPE','BATCH NAME','AVERAGE COMPLETION TIME','SLA','LD_INFO_SK','LD_STRT_TS','LD_END_TS','LD_DURTN_SCND','LD_STS','TNNT_SK','SRC_CD']
    df=df[['BATCH TYPE','BATCH NAME','AVERAGE COMPLETION TIME','SLA','LD_INFO_SK','LD_STRT_TS','LD_END_TS','LD_STS','LD_DURTN_SCND','TNNT_SK','SRC_CD']]
    return df

## Following fuction summarizes the data for the 2nd table in the App like last month loads etc."
def get_df1(n='BATCH_1'):
    df1=get_df()
    df1['BATCH NAME']=df1['BATCH NAME'].str.split('_').str.join('').str.capitalize().str.strip()
    df1['DATE']=pd.to_datetime(df1['LD_STRT_TS'].dt.date)
    df1['month']=df1['LD_STRT_TS'].dt.month
    df1['month']=df1['month']-1
    df1=df1.rename(columns={'BATCH NAME':'Batch_Name'})

    df11=pd.read_csv('cc_ds_job_stats.csv')
    df11['DATE']=pd.to_datetime(df11['DATE'])
    merged=pd.merge(df1,df11,on=['Batch_Name','DATE'],how='left').rename(columns={'COUNTS':'Current Load Counts'})

    df11['month']=pd.to_datetime(df11['DATE']).dt.month

    df_g=df11.groupby(['Batch_Name','month'])['COUNTS'].sum().reset_index()
    df12=df_g.rename(columns={'COUNTS':'Prev Month Load Count'})

    merged1=pd.merge(merged,df12,on=['Batch_Name','month'],how='left')
    merged1.drop_duplicates('Batch_Name',inplace=True)
    merged1['Prev month avg Load time']=None
    merged1['Prev month min Load time']=None
    merged1['Prev month max Load time']=None
    n=n.replace('_','').capitalize()
    k= merged1[merged1['Batch_Name']==n][['Batch_Name','Current Load Counts',
           'Prev Month Load Count', 'Prev month avg Load time',
           'Prev month min Load time', 'Prev month max Load time']].transpose().reset_index()
    k.columns=['Batch','Details']
    return k

# Following function creates the table from the dataframe.
def tb_color(df):

    return dash_table.DataTable(id='leads_table2',data=df.to_dict('rows'),columns=[{'name': i, 'id': i} for i in df.columns],
        style_header={
        'backgroundColor': '#082255',
        'color':'white',
        'border': 'thin lightgrey solid',
        'fontWeight': 'bold',
        'font_size': '16px',
        'text_align':'left',
        'whiteSpace':'normal',
        'height':'auto'
    },
        #fixed_rows={'headers': True, 'data': 0},
        sort_action="native",
        sort_mode="multi",
        row_selectable="single",
        selected_columns=[],
        selected_rows=[],
        style_as_list_view=True,
    style_cell = {
        'fontFamily':'Open Sans',
        'textAlign':'left',
        'width':'150px',
        'minWidth':'180px',
        'maxWidth':'180px',
        'whiteSpace':'no-wrap'},

    style_data_conditional=[
        {'if': {'filter_query': '{LD_STS} eq "STARTED"'},
            'backgroundColor': 'yellow',
            'color': 'black',},
        {'if': {'filter_query': '{LD_STS} eq " "'},
            'backgroundColor': 'red',
            'color': 'white',
        },{'if': {'filter_query': '{LD_STS} eq COMPLETED'},'backgroundColor': 'lightgreen','color': 'black',}])
    
# Following fuction is for creating the 2nd table
def tb_out(dfa):
    return [dash_table.DataTable(
    columns=[
        {"name": i, "id": i } for i in dfa.columns
    ],
    style_as_list_view=True,
    style_header={
    'backgroundColor': '#082255',
    'color':'white',
    'fontWeight': 'bold',
    'font_size': '16px',
    'text_align':'center',
    'minWidth': '120px',
    'whiteSpace':'normal',
    'height':'auto'
},

    fixed_rows={'headers': True, 'data': 0},
    style_cell = {
        'backgroundColor': '#082255',
        'color':'white',
        'fontFamily':'Open Sans',
        'font_size':'18px',
        'height':'70px',
        'textAlign':'left',
        'width':'100px',
        'textOverflow':'ellipsis'},
    data=dfa.to_dict('rows'),
    sort_action="native",
    sort_mode="multi",
    )]