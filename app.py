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
                "target": 450,
                "source": "https://www.cnbc.com/article/microsoft-analyst-dan-ives"
            },
            "Brent Thill": {
                "summary": "Raised target to $450 citing strong Azure demand and Copilot monetization.",
                "rating": "Buy",
                "target": 450,
                "source": "https://www.marketwatch.com/story/microsofts-growth-in-azure-and-copilot-raises-targets-analyst-views"
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
                "target": 180,
                "source": "https://www.barrons.com/articles/google-ai-growth-opportunity"
            },
            "Brian Nowak": {
                "summary": "Expects strong ad revenue recovery and Gemini rollout upside.",
                "rating": "Overweight",
                "target": 185,
                "source": "https://www.reuters.com/markets/google-analyst-upgrade-ai-2025"
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
                "target": 25,
                "source": "https://www.fool.com/investing/2025/palantir-ai-growth-defense"
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
                "target": 110,
                "source": "https://www.fiercebiotech.com/biotech/biontech-analyst-targets-oncology-growth"
            }
        }
    }
}

watchlist = [
    {"ticker": "ZS", "name": "Zscaler", "sector": "Tech", "ytd": "+73%", "forecast": "$309+", "catalyst": "Breakout pattern", "analyst": "IBD", "source": "https://www.investors.com/research/zscaler-stock-analysis"},
    {"ticker": "SNOW", "name": "Snowflake", "sector": "Tech", "ytd": "+43%", "forecast": "$262 (MS target)", "catalyst": "AI/data infra", "analyst": "Morgan Stanley", "source": "https://www.barrons.com/articles/snowflake-stock-price-target"},
    {"ticker": "AVGO", "name": "Broadcom", "sector": "Semis", "ytd": "+37%", "forecast": "Strong demand", "catalyst": "AI chip boom", "analyst": "IBD", "source": "https://www.investors.com/research/broadcom-stock-analysis"},
    {"ticker": "DASH", "name": "DoorDash", "sector": "Consumer", "ytd": "+37%", "forecast": "+19% growth", "catalyst": "Institutional demand", "analyst": "IBD", "source": "https://www.investors.com/news/technology/doordash-stock-outlook"},
    {"ticker": "MRVL", "name": "Marvell", "sector": "Semis", "ytd": "-32%", "forecast": "Recovery", "catalyst": "Underpriced AI infra", "analyst": "Barron's", "source": "https://www.barrons.com/articles/marvell-technology-ai-stock-turnaround"}
]

# ----------------------- MAIN APP LOGIC -----------------------

# --- Sidebar Ticker Selection ---
ticker = st.selectbox("Choose a stock ticker", list(framework.keys()))
info = framework[ticker]

# --- Download stock data ---
df = yf.download(ticker, period="2y", group_by='ticker')

# Flatten multilevel columns if needed
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [' '.join(col).strip() for col in df.columns.values]

df = df.reset_index()
close_col = [col for col in df.columns if "Close" in col][0]
current_price = df[close_col].iloc[-1]

# --- Forecast with Prophet ---
df_train = df[["Date", close_col]].rename(columns={"Date": "ds", close_col: "y"})
model = Prophet(daily_seasonality=True)
model.fit(df_train)
future = model.make_future_dataframe(periods=180)
forecast = model.predict(future)
forecast_price = forecast['yhat'].iloc[-1]

# --- Evaluation Summary ---
st.markdown(f"### 📊 Evaluation Summary for `{ticker}`")
st.markdown(f"- **Category**: {info.get('category')}")
st.markdown(f"- **Innovation Catalyst**: {info.get('innovation')}")
st.markdown(f"- **Political Sensitivity**: {info.get('political')}")
st.markdown(f"- **Entry Price Target**: ${info.get('entry_price')}")
st.markdown(f"- **Current Price**: ${current_price:.2f}")
st.markdown(f"- **Forecast Price (6mo)**: ${forecast_price:.2f}")
st.markdown(f"- **Top Analysts**: {', '.join(info.get('analysts', []))}")

# --- Analyst Commentary Section ---
if "analyst_notes" in info:
    st.markdown("### 🧠 Analyst Commentary")
    for name, note in info["analyst_notes"].items():
        with st.expander(f"🗣 {name} ({note['rating']}, Target: ${note['target']})"):
            st.markdown(note["summary"])
            st.markdown(f"[🔗 Source]({note['source']})")

# --- Historical Price ---
st.subheader("📈 Historical Price")
st.line_chart(df.set_index("Date")[close_col])

entry_price = info.get("entry_price")
delta_pct = ((current_price - entry_price) / entry_price) * 100
st.metric(label="📌 Current vs Entry Price", value=f"${current_price:.2f}", delta=f"{delta_pct:.2f}%")

# --- Optional Date Range Selector ---
st.subheader("⏳ Interactive Time Range")
date_range = st.slider("Select time window", min_value=df["Date"].min().date(), max_value=df["Date"].max().date(), value=(df["Date"].min().date(), df["Date"].max().date()))
df_filtered = df[(df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))]
st.line_chart(df_filtered.set_index("Date")[close_col])

# --- Forecast Plot ---
st.subheader("🔮 Price Forecast")
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
fig.add_trace(go.Scatter(x=df_train['ds'], y=df_train['y'], name='Historical'))
fig.update_layout(title=f"{ticker} Forecast", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig)

# --- Watchlist Section ---
st.subheader("📋 Top Growth Forecast Watchlist")
st.markdown("These stocks have the highest momentum or upside into 2025:")

for stock in watchlist:
    with st.expander(f"{stock['name']} ({stock['ticker']}) - {stock['sector']}"):
        st.markdown(f"- **YTD Performance**: {stock['ytd']}")
        st.markdown(f"- **Forecast Target**: {stock['forecast']} ({stock['analyst']})")
        st.markdown(f"- **Catalyst**: {stock['catalyst']}")
        st.markdown(f"[🔎 Source]({stock['source']})")
