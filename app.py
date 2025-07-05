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
        "political": "High",
        "analyst_notes": {
            "Mark Mahaney": {
                "summary": "Highlights Google's AI strength and YouTube monetization growth.",
                "rating": "Buy",
                "target": 180
            },
            "Brian Nowak": {
                "summary": "Expects strong ad revenue recovery and Gemini rollout upside.",
                "rating": "Overweight",
                "target": 185
            }
        }
    },
    "PLTR": {
        "category": "Speculative",
        "entry_price": 22,
        "analysts": ["Alex Zukin"],
        "innovation": "Defense AI",
        "political": "Low",
        "analyst_notes": {
            "Alex Zukin": {
                "summary": "Cites Palantir's expanding defense contracts and AI platform Palantir AIP.",
                "rating": "Hold",
                "target": 25
            }
        }
    },
    "BNTX": {
        "category": "Biotech",
        "entry_price": 95,
        "analysts": ["Geoff Meacham"],
        "innovation": "Cancer Vaccines",
        "political": "Moderate",
        "analyst_notes": {
            "Geoff Meacham": {
                "summary": "Notes BioNTech's oncology pipeline and mRNA platform diversification.",
                "rating": "Buy",
                "target": 110
            }
        }
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

# --- Historical Close Price ---
close_col = [col for col in df.columns if "Close" in col][0]
current_price = df[close_col].iloc[-1]

# --- Evaluation Summary Card ---
st.markdown(f"### 📊 Evaluation Summary for `{ticker}`")
st.markdown(f"- **Category**: {info.get('category', 'N/A')}")
st.markdown(f"- **Innovation Catalyst**: {info.get('innovation', 'N/A')}")
st.markdown(f"- **Political Sensitivity**: {info.get('political', 'N/A')}")
st.markdown(f"- **Entry Price Target**: ${info.get('entry_price', 'N/A')}")
st.markdown(f"- **Current Price**: ${current_price:.2f}")

# --- Forecasting with Prophet (for Forecast Price) ---
forecast_df = df[["Date", close_col]].rename(columns={"Date": "ds", close_col: "y"})
model = Prophet(daily_seasonality=True)
model.fit(forecast_df)
future = model.make_future_dataframe(periods=180)
forecast = model.predict(future)
forecast_price = forecast['yhat'].iloc[-1]
st.markdown(f"- **Forecasted Price (6 months)**: ${forecast_price:.2f}")

st.markdown(f"- **Top Analysts**: {', '.join(info.get('analysts', [])) or 'N/A'}")

# --- Analyst Notes Section ---
if "analyst_notes" in info and isinstance(info["analyst_notes"], dict):
    st.markdown("### 🧠 Analyst Commentary")
    for name, note in info["analyst_notes"].items():
        with st.expander(f"🗣 {name} ({note['rating']}, Target: ${note['target']})"):
            st.markdown(note["summary"])

# --- Historical Price Chart and Metrics ---
st.subheader("📈 Historical Price")

# Plot full historical chart
st.line_chart(df.set_index("Date")[close_col])

# Entry price delta metric
entry_price = info.get("entry_price", None)
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

# --- Forecast Plot ---
st.subheader("🔮 Price Forecast")

# Plot forecast
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], name='Historical'))
fig.update_layout(title=f"{ticker} Forecast", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig)
