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

# The rest of the app logic remains unchanged.
# Analyst expander updated:
# ...
        with st.expander(f"🗣 {name} ({note['rating']}, Target: ${note['target']})"):
            st.markdown(note["summary"])
            st.markdown(f"[🔗 Source]({note['source']})")

# And Watchlist expander:
# ...
        st.markdown(f"- **Forecast Target**: {stock['forecast']} ({stock['analyst']})")
        st.markdown(f"- **Catalyst**: {stock['catalyst']}")
        st.markdown(f"[🔎 Source]({stock['source']})")
