import streamlit as st
import pandas as pd
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime

# --- Framework metadata (example entries) ---
framework = {
    "MSFT": {
        "category": "Core",
        "entry_price": 415,
        "analysts": ["Dan Ives", "Brent Thill"],
        "innovation": "AI Copilot",
        "political": "Moderate",
        "analyst_notes": {
            "Dan Ives": {
                "summary": "Believes MSFT is leading in enterprise AI; expects 15% YoY growth.",
                "rating": "Buy",
                "target": 450
            },
            "Brent Thill": {
                "summary": "Raised target to $450 citing strong Azure demand and Copilot monetization.",
                "rating": "Buy",
                "target": 450
            }
        }
    },
    "GOOGL": {
        "category": "Core",
        "entry_price": 160,
        "analysts": ["Mark Mahaney", "Brian Nowak"],
        "innovation": "Gemini LLM",
        "political": "High"
    },
    "PLTR": {
        "category": "Speculative",
        "entry_price": 22,
        "analysts": ["Alex Zukin"],
        "innovation": "Defense AI",
        "political": "Low"
    },
    "BNTX": {
        "category": "Biotech",
        "entry_price": 95,
        "analysts": ["Geoff Meacham"],
        "innovation": "Cancer Vaccines",
        "political": "Moderate"
    }
}

# --- Sidebar Ticker Selection ---
ticker = st.selectbox("Choose a stock ticker", list(framework.keys()))
info = framework.get(ticker, {})

# --- Download stock data ---
df = yf.download(ticker, period="2y", group_by='ticker')

# Handle multi-index column headers
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [' '.join(col).strip() for col in df.columns.values]

# Reset index to bring Date into column
df = df.reset_index()

# --- Evaluation Summary Card ---
st.markdown(f"### 📊 Evaluation Summary for `{ticker}`")
st.markdown(f"- **Category**: {info.get('category', 'N/A')}")
st.markdown(f"- **Innovation Catalyst**: {info.get('innovation', 'N/A')}")
st.markdown(f"- **Political Sensitivity**: {info.get('political', 'N/A')}")
st.markdown(f"- **Entry Price Target**: ${info.get('entry_price', 'N/A')}")
st.markdown(f"- **Top Analysts**: {', '.join(info.get('analysts', [])) or 'N/A'}")

# --- Analyst Notes Section ---
if "analyst_notes" in info:
    st.markdown("### 🧠 Analyst Commentary")
    for name, note in info["analyst_notes"].items():
        with st.expander(f"🗣 {name} ({note['rating']}, Target: ${note['target']})"):
            st.markdown(note["summary"])

# --- Historical Price Chart and Metrics ---
st.subheader("📈 Historical Price")

close_col = [col for col in df.columns if "Close" in col][0]
current_price = df[close_col].iloc[-1]
entry_price = info.get("entry_price", None)

# Plot full historical chart
st.line_chart(df.set_index("Date")[close_col])

# Entry price delta metric
if entry_price:
    delta_pct = ((current_price - entry_price) / entry_price) * 100
    st.metric(
        label="📌 Current vs Entry Price",
        value=f"${current_price:.2f}",
        delta=f"{delta_pct:.2f}%"
    )
    if current_price < entry_price:
        st.success("✅ Potential entry opportunity: price is below your target.")
    elif current_price > entry_price * 1.15:
        st.warning("⚠️ Price is significantly above entry target (15%+).")

# --- Optional Date Range Selector ---
st.subheader("⏳ Interactive Time Range")

date_range = st.slider(
    "Select time window",
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
    value=(df["Date"].min().date(), df["Date"].max().date())
)

df_filtered = df[(df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))]
st.line_chart(df_filtered.set_index("Date")[close_col])

# --- Forecasting with Prophet ---
st.subheader("🔮 Price Forecast")

# Prepare data for forecasting
forecast_df = df[["Date", close_col]].rename(columns={"Date": "ds", close_col: "y"})

# Fit and forecast
model = Prophet(daily_seasonality=True)
model.fit(forecast_df)
future = model.make_future_dataframe(periods=180)
forecast = model.predict(future)

# Plot forecast
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], name='Historical'))
fig.update_layout(title=f"{ticker} Forecast", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig)
