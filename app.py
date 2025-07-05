import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objs as go

st.title("📈 AI Investment Dashboard")

# Ticker selection
ticker = st.selectbox("Choose a stock ticker", ["MSFT", "GOOGL", "AMZN", "PLTR", "ASML", "BNTX"])

# Load data
df = yf.download(ticker, period="2y", group_by='ticker')

# Flatten multi-level column headers if present
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [' '.join(col).strip() for col in df.columns.values]

# Reset index to make "Date" a column
df = df.reset_index()

# Show column names for debugging
with st.expander("🛠 Show raw column names (dev only)"):
    st.write(df.columns.tolist())

st.subheader("Historical Price")

# Automatically find the correct "Close" column based on ticker
close_col = [col for col in df.columns if "Close" in col][0]

# Plot the closing price line chart
st.line_chart(df.set_index("Date")[close_col])


# Prepare for forecasting
df_train = df[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})

model = Prophet(daily_seasonality=True)
model.fit(df_train)
future = model.make_future_dataframe(periods=180)
forecast = model.predict(future)

st.subheader("Price Forecast")
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
fig.add_trace(go.Scatter(x=df_train['ds'], y=df_train['y'], name='Historical'))
fig.update_layout(title=f"{ticker} Forecast", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig)
