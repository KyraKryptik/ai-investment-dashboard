import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objs as go
import datetime

# Define framework info
framework = {
    "MSFT": {"category": "Core", "entry_price": 415, "analysts": ["Dan Ives 🚀", "Brent Thill"], "innovation": "AI Copilot", "political": "Moderate (Regulation)"},
    "GOOGL": {"category": "Core", "entry_price": 160, "analysts": ["Mark Mahaney", "Brian Nowak"], "innovation": "Gemini LLM", "political": "High (AI policy)"},
    # Add others as needed...
}

st.title("📈 AI Investment Dashboard")

# Ticker selection
ticker = st.selectbox("Choose a stock ticker", ["MSFT", "GOOGL", "AMZN", "PLTR", "ASML", "BNTX"])

# Pull evaluation info from framework dictionary
info = framework.get(ticker, {})

# Display evaluation summary
st.markdown(f"### 📊 Evaluation Summary for `{ticker}`")

# Safely display each value (with fallback if missing)
st.markdown(f"- **Category**: {info.get('category', 'N/A')}")
st.markdown(f"- **Innovation Catalyst**: {info.get('innovation', 'N/A')}")
st.markdown(f"- **Political Sensitivity**: {info.get('political', 'N/A')}")
st.markdown(f"- **Entry Price Target**: ${info.get('entry_price', 'N/A')}")
st.markdown(f"- **Top Analysts**: {', '.join(info.get('analysts', [])) or 'N/A'}")

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

# 🟦 Historical Price Chart Section
st.subheader("📈 Historical Price")

# 📈 Use "Date" as index, and plot the Close column
st.line_chart(df.set_index("Date")[close_col])

# 📌 Entry price comparison metric
current_price = df[close_col].iloc[-1]
entry_price = info.get("entry_price", None)

if entry_price:
    st.metric(
        label="📌 Current vs Entry Price",
        value=f"${current_price:.2f}",
        delta=f"${current_price - entry_price:.2f}"
    )



# Automatically find the correct "Close" column based on ticker
close_col = [col for col in df.columns if "Close" in col][0]

# Plot the closing price line chart
st.line_chart(df.set_index("Date")[close_col])


# Prepare for forecasting
close_col = [col for col in df.columns if "Close" in col][0]
df_train = df[['Date', close_col]].rename(columns={"Date": "ds", close_col: "y"})

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
