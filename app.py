import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="投資趨勢監控", layout="centered")

# --- CSS 視覺校準：色光 30 漸變至 250 ---
st.markdown("""
    <style>
    /* 銳利化字體與布局 */
    .price-font { font-size: 26px; font-weight: bold; }
    .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    
    /* 進度條底槽：深黑色背景 */
    div[data-testid="stProgress"] > div > div {
        background-color: #050505 !important;
        height: 18px;
        border-radius: 4px;
    }
    
    /* 能量條漸層：色光 30 -> 250 */
    div[data-testid="stProgress"] > div > div > div > div {
        background-image: var(--bar-gradient) !important;
        background-color: transparent !important;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 ETF 趨勢監控 App")

# 1. 金額輸入 (整數格式)
st.subheader("💰 投資金額輸入")
c_in1, c_in2 = st.columns(2)
with c_in1:
    amt_ndx = st.number_input("NDX 投入金額", min_value=0, value=30, step=1, format="%d")
with c_in2:
    amt_sox = st.number_input("SOX 投入金額",
