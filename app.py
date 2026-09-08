import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ১. পেজ সেটআপ
st.set_page_config(page_title="Gold Market Tracker(INR)", page_icon="🪙", layout="wide")

st.title("🪙 Gold Market Analytics & Interactive Dashboard")
st.markdown("Historical and Live Market Data Analysis of Gold Futures (GC=F) from Yahoo Finance, with International Gold Prices Converted and Displayed in Indian Rupees (INR)")

# ২. সাইডবার ইনপুট
st.sidebar.header("User Filters")
period = st.sidebar.selectbox("Select Time Period", ["1wk","1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

# 💡 ডাটা ফেচিং ফাংশন
@st.cache_data
def get_gold_data_inr(p, i, rate=83.5, factor=1.0):
    gold = yf.Ticker("GC=F")
    df = gold.history(period=p, interval=i)
    
    # ১ ট্রয় আউন্স = ৩১.১০৩৪ গ্রাম। ১০ গ্রাম সোনার দাম (INR)-এ বের করার সঠিক কনভার্সন:
    conversion_factor = (10 / 31.1034) * rate * factor
    
    # ডলার থেকে টাকা তে রূপান্তর
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col] * conversion_factor
        
    return df

# ডলার রেট ৮৩.৫ ধরে ডাটা কল
df = get_gold_data_inr(period, interval, rate=83.5, factor=1.0)

# ৩. কি-মেট্রিক্স (Key Metrics Card)
if not df.empty:
    latest_price = round(df['Close'].iloc[-1], 2)
    prev_price = round(df['Close'].iloc[-2], 2)
    price_change = round(latest_price - prev_price, 2)
    pct_change = round((price_change / prev_price) * 100, 2)

    col1, col2, col3 = st.columns(3)
    
    # খেয়াল করুন: এখানে $ কেটে ₹ (Rupee Symbol) বসানো হয়েছে
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

    # ৪. ইন্টারঅ্যাক্টিভ ক্যান্ডেলস্টিক চার্ট (Plotly)
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

    # ৫. মুভিং অ্যাভারেজ ও ডাটা টেবিল
    st.subheader("📊 Moving Averages & Raw Data")
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.line_chart(df[['Close', 'SMA_20']])
    with col_table:
        st.dataframe(df[['Close', 'Volume']].tail(10))
else:
    st.error("Failed to load data. Please try again.")

