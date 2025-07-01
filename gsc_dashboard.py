# -*- coding: utf-8 -*-
"""
GSC Analyzer Pro Edition - by Pravesh Patel

Supports:
- CSV Upload (Queries.csv)
- Excel Upload (.xlsx) from GSC
- Tab-based UI for clear separation
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

# Page Setup
st.set_page_config(page_title="GSC Analyzer Pro Edition", page_icon="📈", layout="wide")
st.title("📈 GSC Analyzer Pro Edition")
st.markdown("*Developed by **Pravesh Patel***", unsafe_allow_html=True)

# Sidebar Bio
st.sidebar.markdown("## 👨‍💻 About the Developer")
st.sidebar.markdown("""
Hi, I'm **Pravesh Patel** — a passionate SEO Manager and data enthusiast.

🔍 I specialize in SEO, analytics, and tools that simplify Google Search Console data.

💼 Working at Blow Horn Media, I build tools like this to find content opportunities faster.

🌐 [Visit praveshpatel.com](https://www.praveshpatel.com)
""")

# Tabs
tab1, tab2 = st.tabs(["📄 CSV Analyzer", "📊 Excel Analyzer"])

# =====================================
# TAB 1: CSV ANALYZER
# =====================================
with tab1:
    st.header("📄 GSC CSV Analyzer")
    uploaded_file = st.file_uploader("Upload `Queries.csv` file", type=["csv"], key="csv_uploader")
    
    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(raw_data))
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df.rename(columns={"top_queries": "query"}, inplace=True)

        required_cols = ["query", "clicks", "impressions", "ctr", "position"]
        if not all(col in df.columns for col in required_cols):
            st.error("❌ Missing required columns. Please upload a valid GSC Queries.csv file.")
            st.stop()

        # Data Cleaning
        for col in ["clicks", "impressions", "position"]:
            df[col] = df[col].astype(str).str.replace(",", "").astype(float)
        df["ctr"] = df["ctr"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
        df.dropna(subset=required_cols, how="all", inplace=True)

        # Performance Metrics
        st.subheader("📊 Performance Metrics")
        total_clicks = df["clicks"].sum()
        total_impr = df["impressions"].sum()
        avg_ctr = (df["ctr"] * df["impressions"]).sum() / total_impr if total_impr else 0
        avg_pos = (df["position"] * df["impressions"]).sum() / total_impr if total_impr else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clicks", f"{total_clicks:,.0f}")
        col2.metric("Total Impressions", f"{total_impr:,.0f}")
        col3.metric("Avg. CTR", f"{avg_ctr:.2f}%")
        col4.metric("Avg. Position", f"{avg_pos:.2f}")

        # Top Queries
        st.subheader("🔝 Top Queries by Clicks")
        st.dataframe(df.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

        # Opportunities
        st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
        opportunities = df[(df["position"].between(5, 15)) & (df["ctr"] < 5)]
        st.markdown(f"**Total Opportunities:** {len(opportunities)}")
        st.dataframe(opportunities.sort_values(by="impressions", ascending=False), use_container_width=True)

        st.download_button(
            label="📥 Download Opportunities as CSV",
            data=opportunities.to_csv(index=False),
            file_name="opportunity_keywords.csv",
            mime="text/csv"
        )

# =====================================
# TAB 2: EXCEL ANALYZER
# =====================================
with tab2:
    st.header("📊 GSC Excel Analyzer (.xlsx)")
    xlsx_file = st.file_uploader("Upload Excel Export from GSC", type=["xlsx"], key="xlsx_uploader")

    if xlsx_file:
        all_sheets = pd.read_excel(xlsx_file, sheet_name=None)
        queries_df = all_sheets.get("Queries")
        pages_df = all_sheets.get("Pages")
        countries_df = all_sheets.get("Countries")

        # Queries Sheet
        if queries_df is not None:
            st.subheader("🔎 Queries Overview")
            for col in ["Clicks", "Impressions", "CTR", "Position"]:
                queries_df[col] = queries_df[col].astype(str).str.replace(",", "").str.replace("%", "").astype(float)
            st.dataframe(queries_df.head(10), use_container_width=True)

            q_clicks = queries_df["Clicks"].sum()
            q_impr = queries_df["Impressions"].sum()
            q_ctr = (queries_df["CTR"] * queries_df["Impressions"]).sum() / q_impr if q_impr else 0
            q_pos = (queries_df["Position"] * queries_df["Impressions"]).sum() / q_impr if q_impr else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Clicks", f"{q_clicks:,.0f}")
            col2.metric("Impressions", f"{q_impr:,.0f}")
            col3.metric("Avg. CTR", f"{q_ctr:.2f}%")
            col4.metric("Avg. Position", f"{q_pos:.2f}")

        # Pages Sheet
        if pages_df is not None:
            st.subheader("📄 Top Pages Performance")
            for col in ["Clicks", "Impressions", "CTR", "Position"]:
                pages_df[col] = pages_df[col].astype(str).str.replace(",", "").str.replace("%", "").astype(float)
            st.dataframe(pages_df.sort_values(by="Clicks", ascending=False).head(10), use_container_width=True)

        # Countries Sheet
        if countries_df is not None:
            st.subheader("🌍 Country-wise Performance")
            for col in ["Clicks", "Impressions", "CTR", "Position"]:
                countries_df[col] = countries_df[col].astype(str).str.replace(",", "").str.replace("%", "").astype(float)
            top_countries = countries_df.sort_values(by="Impressions", ascending=False).head(10)
            st.dataframe(top_countries, use_container_width=True)

            st.bar_chart(top_countries.set_index("Country")[["CTR"]])

    else:
        st.info("📥 Please upload your GSC Excel export (.xlsx) to begin.")
