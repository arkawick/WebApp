#cd desktop
#streamlit run <app name>.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet.plot import plot_plotly
from plotly import graph_objs as go

from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator

import streamlit as st

from datetime import date
import yfinance as yf

from prophet import Prophet

##########################################
# remove "·Streamlit" from the app title # 
##########################################

st.set_page_config(
   page_title="Stock Price Prediction",
   page_icon="📈",
   layout="wide",
   initial_sidebar_state="expanded",
)


st.title("Stock Visualizer")


##################
# Set up sidebar #
##################


option = st.sidebar.selectbox('Select Stock', ( 'AAPL', 'MSFT', 'TSLA', 'META'))


import datetime

today = date.today()
before = today - datetime.timedelta(days=700)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')


##############
# Stock data #
##############


df = yf.download(option,start= start_date,end= end_date, progress=False)

indicator_bb = BollingerBands(df['Close'])

bb = df
bb['Bollinger_high'] = indicator_bb.bollinger_hband()
bb['Bollinger_low'] = indicator_bb.bollinger_lband()
bb = bb[['Close','Bollinger_high','Bollinger_low']]

macd = MACD(df['Close']).macd()

rsi = RSIIndicator(df['Close']).rsi()


###################
# Set up main app #
###################

st.write('Bollinger Bands of Stock Dataset')

st.line_chart(bb)

progress_bar = st.progress(0)

st.write('Stock Moving Average Convergence Divergence (MACD)')
st.area_chart(macd)

st.write('Stock RSI ')
st.line_chart(rsi)


st.write('Recent Data Overview')
st.dataframe(df.tail())


################
# Download csv #
################

import base64
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="download.xlsx">Download excel file</a>' # decode b'abc' => abc

st.markdown(get_table_download_link(df), unsafe_allow_html=True)



################################################################################

start_date = "2015-01-01"
end_date = date.today().strftime("%Y-%m-%d")

df = yf.download(option,start= start_date,end= end_date, progress=False)
df.reset_index(inplace=True)


st.write("###")

#st.subheader("Raw data")
#st.write(df.tail())

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], name='stock_open'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='stock_close'))
fig.layout.update(title_text = "Time Series Data", xaxis_rangeslider_visible = True)
st.plotly_chart(fig)

st.title("Stock Prediction")

st.subheader("Choose Number of Years")
n_years = st.slider("", 1, 5)
period = n_years * 365


#Forecasting
df_train = df[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)

future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.write("***")
st.write("###")

st.subheader("Forecasted data")
st.write(forecast.tail())

fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.subheader("Forecast Components")
fig2 = m.plot_components(forecast)
st.write(fig2)

################################################################################

################################################################################




