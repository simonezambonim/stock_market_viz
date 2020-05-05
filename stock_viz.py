# import Libraries
import sys
import streamlit as st
import talib as ta #https://blog.quantinsti.com/install-ta-lib-python/
import numpy as np
import pandas as pd
#import html5lib
from pandas_datareader import data as pdr
import datetime 
import yfinance as yf
yf.pdr_override()

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from ta_funcs import *
import requests

@st.cache 
def load_tickers():

    """Scrap website to get ibrx100"""

    url = 'https://blog.toroinvestimentos.com.br/empresas-listadas-b3-bovespa'
    r = requests.get(url)
    ibrx100_df = pd.read_html(r.text, header=0)[1]
    return ibrx100_df.set_index('Código da ação')

@st.cache
def get_data(asset):
    
    """get stock info"""

    def encode_class_target(x):
        if x>0.01: 
            return int(1)
        elif x<-0.01:
            return int(-1)
        else:
            return int(0)

    if (asset != " "):
        try:
            #stock = yf.download(asset)
            stock = pdr.get_data_yahoo(asset)
            stock['return_t+1'] = stock['Adj Close'].pct_change(1).shift(-1)
            stock['cls_t+1'] = stock['return_t+1'].map(encode_class_target).astype('category')
            return stock
        except:
            sys.exit("No data collected from Yahoo Finance!")            

def get_date():

    """Select a period of time"""

    today = datetime.date.today()
    monthago = today - datetime.timedelta(days=30)
    start_date = st.sidebar.date_input('Start date', monthago)
    end_date = st.sidebar.date_input('End date', today)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
        return start_date, end_date
    else:
        st.error('Error: End date must fall after start date.')
        return None

def plot_candlestick(stock,asset):

    """ Plot stocks in candlestick format"""

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=stock.index,
                open=stock['Open'],
                high=stock['High'],
                low=stock['Low'],
                close=stock['Close']))

    # fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])            
    layout = fig.update_layout(dict(
        title = asset,
        title_x=0.5,
        xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1d',
                     step='day',
                     stepmode='backward'),
                dict(count=7,
                     label='1w',
                     step='day',
                     stepmode='backward'),
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                     label='1y',
                     step='year',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(
            visible = True),
        type='date',
        rangebreaks=[dict(bounds=["sat", "sun"])])))
    return fig 

def get_ticker(ibrx100):

    """format symbol according to yfinance asset ticker """

    symbol = st.sidebar.selectbox("Choose the stock", (list(ibrx100.index.sort_values())))
    asset = symbol+'.SA'    
    return symbol, asset

def func_ind(ind,list_ind):

    """Calculate indicators"""

    if ('ADX' == list_ind):
        #ADX - Average Directional Movement Index
        periodadx = st.sidebar.number_input(
            "ADX period", min_value=5, max_value=500, value=14, step=1, key='adx')
        series_ind = ind.adx(periodadx)
       
    if ('SAR' == list_ind):
        #SAR - Parabolic SAR
        series_ind = ind.sar()  

    if ('RSI' == list_ind):
        # RSI - Relative Strength Index
        periodsar = st.sidebar.number_input(
            "RSI period", min_value=5, max_value=500, value=14, step=1,key='rsi')
        series_ind = ind.rsi(periodsar)

    if ('CCI' == list_ind):
        #CCI - Commodity Channel Index
        periodcci= st.sidebar.number_input(
            "CCI period", min_value=5, max_value=500, value=14, step=1, key='cci')
        series_ind = ind.cci(periodcci)
        
    if ('EMA' == list_ind):
        # EMA - Exponential moving average
        periodema = st.sidebar.number_input(
            "EMA period", min_value=5, max_value=500, value=30, step=1, key='ema')
        series_ind = ind.ema(periodema)  
                       
    if ('SMA' == list_ind):
        #SMA - Simple Moving Average
        periodsma = st.sidebar.number_input(
            "SMA period", min_value=5, max_value=500, value=20, step=1,key='sma')
        series_ind =ind.sma(periodsma)  

    if ('STOCH' == list_ind):
        #STOCH - Stochastic
        series_ind = ind.stoch()

    if ('MACD' == list_ind):
        #MACD - Moving Average Convergence/Divergence
        periodmacd_fast = st.sidebar.number_input(
            "MACD period", min_value=5, max_value=500, value=12, step=1, key='macd')
        periodmacd_slow = st.sidebar.number_input(
            "MACD slow", min_value=5, max_value=500, value=26, step=1, key='macd')
        periodmacd_signal = st.sidebar.number_input(
            "MACD signal", min_value=5, max_value=500, value=9, step=1, key='macd')
        
        series_ind = ind.macd(periodmacd_fast, periodmacd_slow,periodmacd_signal) 
        
    if ('BBANDS' == list_ind):
        #BBANDS Bollinger Bands
        periodbbands = st.sidebar.number_input(
            "BBANDS period", min_value=5, max_value=500, value=30, step=1,key='bbands')
        series_ind = ind.bbands(periodbbands)
        
    if ('OBV' == list_ind):
        series_ind = ind.obv()


    # return plot_graph_ind_2(ind,series_ind)
    return series_ind

def get_plot_indicators(ind, multi_indicator, start_date,end_date):

    """ Calculate and plot indicators 
    Returns fig and dataframe with [multi_indicator] indicators
    """

    nrows = len(multi_indicator)+1
    fig = make_subplots(rows=nrows, 
        cols=1, shared_xaxes=False,vertical_spacing=0.06, subplot_titles=tuple(multi_indicator))
    
    aux_df = pd.DataFrame()
    for j,i in enumerate(multi_indicator):
        indicator_series = func_ind(ind,i)
        aux_df = pd.concat([aux_df,indicator_series], axis =1)
        if (i not in ['SAR','SMA', 'EMA', 'BBANDS']): 
            for col_ in indicator_series:
                fig.add_trace(go.Scatter(
                                x=indicator_series.loc[start_date:].index,  
                                y=indicator_series.loc[start_date:,col_],
                                mode ='lines',
                                name = indicator_series[col_].name.upper(),
                                opacity = 1), row = j+1, col=1 )
        elif i in (['SAR','SMA', 'EMA', 'BBANDS']):
            fig.add_trace(go.Candlestick(
                x=ind.df.loc[start_date:].index,
                open=ind.df.loc[start_date:,'Open'],
                high=ind.df.loc[start_date:,'High'],
                low=ind.df.loc[start_date:,'Low'],
                close=ind.df.loc[start_date:,'Close']), row = j+1, col=1)

            for col_ in indicator_series:
                fig.add_trace(go.Scatter(
                                    x=indicator_series.loc[start_date:].index,  
                                    y=indicator_series.loc[start_date:,col_],
                                    mode ='lines',
                                    name = indicator_series[col_].name.upper(),
                                    opacity = 1), row = j+1, col=1 )

        if i == 'MACD':
            fig.add_shape( {
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':0,
                    'x1':end_date,
                    'y1':0,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

        if (i == 'STOCH' or i == 'RSI') :
            fig.add_shape( {
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':80,
                    'x1':end_date,
                    'y1':80,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

            fig.add_shape( {
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':20,
                    'x1':end_date,
                    'y1':20,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

        if (i == 'ADX') :
            fig.add_shape( {
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':50,
                    'x1':end_date,
                    'y1':50,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

            fig.add_shape( {
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':25,
                    'x1':end_date,
                    'y1':25,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

        if i == "CCI":
            fig.add_shape({
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':100,
                    'x1':end_date,
                    'y1':100,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

            fig.add_shape({
                    'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':-100,
                    'x1':end_date,
                    'y1':-100,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dashdot")}, row = j+1, col=1)

            fig.add_shape({
                'type':"line",
                    'xref':"x",
                    'yref':"y",
                    'x0':start_date,
                    'y0':0,
                    'x1':end_date,
                    'y1':0,
                    'line' : dict(color="Black",
                    width=0.5,
                    dash="dot")}, row = j+1, col=1)

    fig.for_each_trace(lambda trace: trace.update(mode ='markers') if trace.name == "SAR" else ())
    for j,i in enumerate(multi_indicator):
        fig.update_xaxes(rangeslider=dict(visible = False), type='date', row=j+1, col=1)
        #fig.update_traces(marker=dict(color="RoyalBlue"), row=j+1, col=1)
            
    layout = fig.update_layout(
        xaxis_rangeslider_visible=False,
        title = f'Indicators {ind.symbol}',
        title_x=0.5,
        xaxis = dict(rangeslider=dict(visible = False), type='date'),
        height=250*(len(multi_indicator)+1),
        width = 900, 
        showlegend=False)

    st.plotly_chart(fig, use_container_width=True) 
    return aux_df


def main():
    st.title("Stock Market")
       
    #load a list of 100 stocks from iBRX100
    b3_df = load_tickers()

    #choose a specific stock
    symbol, asset = get_ticker(b3_df)
    st.title(b3_df.loc[symbol].Empresa)
    if st.sidebar.checkbox("View company info", True):
        st.dataframe(b3_df.loc[symbol])

    #get historical data    
    stock_df_raw = get_data(asset)

    #propagate last valid observation forward to next valid 
    stock_df = stock_df_raw.copy().fillna(method='ffill')
    stock_df.index.name = None

    #display data using the st.dataframe command
    slider = st.slider("Choose # of lines to display", 3, 100)
    st.dataframe(stock_df.tail(slider).astype('object'))

    #plot candlestick
    fig = plot_candlestick(stock_df,symbol)
    st.plotly_chart(fig, use_container_width=True)

    #create multiselect -> for comparison of indicators
    st.sidebar.subheader("Select period of visualization")

    end_date = datetime.date.today()
    period_analysis = st.sidebar.radio("Period", ("1d", "1w", "1m", "3m", "6m", "1y", '2y'))

    if period_analysis == "1d":
        start_date = end_date - datetime.timedelta(days=1) 
    elif period_analysis == "1w":
        start_date = end_date - datetime.timedelta(days=7)
    elif period_analysis == "1m":
        start_date = end_date - datetime.timedelta(days=31)
    elif period_analysis == "3m":
        start_date = end_date - datetime.timedelta(days=91)
    elif period_analysis == "6m":
        start_date = end_date - datetime.timedelta(days=183)
    elif period_analysis == "1y":
        start_date = end_date - datetime.timedelta(days=365)
    elif period_analysis == "2y":
        start_date = end_date - datetime.timedelta(days=365*2)

    st.write("from", start_date, "to", end_date)
    list_of_indicators = ['ADX','SAR', 'RSI','STOCH', 'CCI', 'MACD', 'OBV', \
        'SMA', 'EMA', 'BBANDS']
    multi_indicator = st.sidebar.multiselect("Select Indicators", (list_of_indicators))#,format_func = str.upper)
   
    ind = IND_TA(stock_df,symbol)

    df_ind = get_plot_indicators(ind, multi_indicator, start_date, end_date)

    if st.sidebar.checkbox("View statistic"):
        st.subheader("Statistics")
        st.dataframe(stock_df.describe())
    
    st.sidebar.title("About")
    st.sidebar.info("This code was developed by [Simone](https://www.linkedin.com/in/simonezambonim/). \
        More info about Ta-lib functions on [TA-lib repository](https://mrjbq7.github.io/ta-lib/func.html)")


if __name__=='__main__':
    main()