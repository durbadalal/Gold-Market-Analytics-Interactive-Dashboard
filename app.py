import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. PAGE SETUP
st.set_page_config(page_title="Gold Market Tracker(INR)", page_icon="🪙", layout="wide")

st.title("🪙 Gold Market Analytics & Interactive Dashboard")
st.markdown("Historical and Live Market Data Analysis of Gold Futures (GC=F) from Yahoo Finance, with International Gold Prices Converted and Displayed in Indian Rupees (INR)")

# 2. SIDEBAR INPUT
st.sidebar.header("User Filters")
period = st.sidebar.selectbox("Select Time Period", ["1wk","1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

# 💡 DATA FETCHING FUNCTION
@st.cache_data
def get_gold_data_inr(p, i, rate=83.5, factor=1.0):
    gold = yf.Ticker("GC=F")
    df = gold.history(period=p, interval=i)
    
    # 1 Troy ounce = 31.1034 grams. The correct conversion for calculating the price of 10 grams of gold in INR is:
    conversion_factor = (10 / 31.1034) * rate * factor
    
    # Dollar to Rupee Conversion
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col] * conversion_factor
        
    return df

# Using an exchange rate of ₹83.5 per US dollar, call the data.
df = get_gold_data_inr(period, interval, rate=83.5, factor=1.0)

# ৩.Key Metrics Card
if not df.empty:
    latest_price = round(df['Close'].iloc[-1], 2)
    prev_price = round(df['Close'].iloc[-2], 2)
    price_change = round(latest_price - prev_price, 2)
    pct_change = round((price_change / prev_price) * 100, 2)

    col1, col2, col3 = st.columns(3)
    
    # খNote: Here, the $ symbol has been replaced with the ₹ (Rupee) symbol.
    col1.metric(
        label="Latest Closing Price (INR / 10g)", 
        value=f"₹{latest_price:,.2f}", 
        delta=f"₹{price_change:,.2f} ({pct_change}%)"
    )
    col2.metric(
        label="Highest Price (High)", 
        value=f"₹{round(df['High'].max(), 2):,.2f}"
    )
    col3.metric(
        label="Lowest Price (Low)", 
        value=f"₹{round(df['Low'].min(), 2):,.2f}"
    )

    st.markdown("---")

    # ৪. Interactive Candlestick Chart(Plotly)
    st.subheader("📈 Candlestick Price Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Gold Price"
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # ৫. Moving Average and Data Table
    st.subheader("📊 Moving Averages & Raw Data")
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.line_chart(df[['Close', 'SMA_20']])
    with col_table:
        st.dataframe(df[['Close', 'Volume']].tail(10))
else:
    st.error("Failed to load data. Please try again.")

