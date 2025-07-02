# -*- coding: utf-8 -*-
"""
GSC Analyzer Pro Edition - by Pravesh Patel
Supports:
- CSV Upload (Queries.csv)
- Excel Upload (.xlsx) from GSC
- Alerts Dashboard in both tabs
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
# TAB 1: CSV ANALYZER (with Alerts Dashboard)
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

        for col in ["clicks", "impressions", "position"]:
            df[col] = df[col].astype(str).str.replace(",", "").astype(float)
        df["ctr"] = df["ctr"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
        df.dropna(subset=required_cols, how="all", inplace=True)

        # Filter Controls
        with st.expander("🔍 Filter Data"):
            min_impr = st.slider("Minimum Impressions", 0, int(df["impressions"].max()), 100)
            keyword_filter = st.text_input("Filter by Query (Optional)", "")
            df = df[df["impressions"] >= min_impr]
            if keyword_filter:
                df = df[df["query"].str.contains(keyword_filter, case=False, na=False)]

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

        # Alerts Dashboard
        st.subheader("🔔 Alerts Dashboard (SEO Performance Signals)")
        critical = df[(df["ctr"] < 1.0) & (df["impressions"] > 1000)]
        warnings = df[(df["impressions"] > 1000) & (df["clicks"] < 10)]
        wins = df[(df["ctr"] > 10.0) & (df["position"] > 10)]

        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Critical Issues", f"{len(critical):,}")
        col2.metric("🟠 Warnings", f"{len(warnings):,}")
        col3.metric("🟢 Potential Wins", f"{len(wins):,}")

        with st.expander("🔴 View Critical Issues"):
            st.markdown("**Low CTR (<1%) with High Impressions (>1000)**")
            if not critical.empty:
                st.dataframe(critical, use_container_width=True)
            else:
                st.info("No critical issues found.")

        with st.expander("🟠 View Warning Keywords"):
            st.markdown("**Impression Surge but Low Clicks (<10)**")
            if not warnings.empty:
                st.dataframe(warnings, use_container_width=True)
            else:
                st.info("No warnings found.")

        with st.expander("🟢 View High-CTR, Low-Rank Wins"):
            st.markdown("**High CTR (>10%) but Low Ranking (Position >10)**")
            if not wins.empty:
                st.dataframe(wins, use_container_width=True)
            else:
                st.info("No wins found.")

        st.subheader("🔝 Top Queries by Clicks")
        st.dataframe(df.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

        st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
        opp = df[(df["position"].between(5, 15)) & (df["ctr"] < 5)]
        st.markdown(f"**Total Opportunities:** {len(opp)}")
        st.dataframe(opp.sort_values(by="impressions", ascending=False), use_container_width=True)

        st.download_button("📥 Download Opportunities as CSV", data=opp.to_csv(index=False), file_name="opportunity_keywords.csv", mime="text/csv")

    st.info("📌 Please upload a Queries.csv file from Google Search Console > Performance or Search Results > Export > Download CSV > Extract Zip File.")

# =====================================
# TAB 2: EXCEL ANALYZER (Enhanced with Alerts)
# =====================================
with tab2:
    st.header("📊 GSC Excel Analyzer")
    excel_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"], key="excel_uploader")

    if excel_file:
        all_sheets = pd.read_excel(excel_file, sheet_name=None)

        tabs = st.tabs(["🧠 Queries", "📄 Pages", "🌍 Countries"])

        # --------------------------------
        # QUERIES TAB
        # --------------------------------
        with tabs[0]:
            queries_df = all_sheets.get("Queries")
            if queries_df is not None:
                queries_df.columns = [col.strip().lower().replace(" ", "_") for col in queries_df.columns]
                queries_df.rename(columns={"top_queries": "query"}, inplace=True)
                for col in ["clicks", "impressions", "position"]:
                    queries_df[col] = queries_df[col].astype(str).str.replace(",", "").astype(float)
                queries_df["ctr"] = queries_df["ctr"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
                queries_df.dropna(subset=["query", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)

                with st.expander("🔍 Filter Data"):
                    min_impr = st.slider("Minimum Impressions", 0, int(queries_df["impressions"].max()), 100, key="excel_min_impr")
                    keyword_filter = st.text_input("Filter by Query (Optional)", "", key="excel_kw_filter")
                    queries_df = queries_df[queries_df["impressions"] >= min_impr]
                    if keyword_filter:
                        queries_df = queries_df[queries_df["query"].str.contains(keyword_filter, case=False, na=False)]

                st.subheader("📊 Performance Metrics")
                total_clicks = queries_df["clicks"].sum()
                total_impr = queries_df["impressions"].sum()
                avg_ctr = (queries_df["ctr"] * queries_df["impressions"]).sum() / total_impr if total_impr else 0
                avg_pos = (queries_df["position"] * queries_df["impressions"]).sum() / total_impr if total_impr else 0

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Clicks", f"{total_clicks:,.0f}")
                col2.metric("Total Impressions", f"{total_impr:,.0f}")
                col3.metric("Avg. CTR", f"{avg_ctr:.2f}%")
                col4.metric("Avg. Position", f"{avg_pos:.2f}")

                st.subheader("🔔 Alerts Dashboard (SEO Performance Signals)")
                critical = queries_df[(queries_df["ctr"] < 1.0) & (queries_df["impressions"] > 1000)]
                warnings = queries_df[(queries_df["impressions"] > 1000) & (queries_df["clicks"] < 10)]
                wins = queries_df[(queries_df["ctr"] > 10.0) & (queries_df["position"] > 10)]

                col1, col2, col3 = st.columns(3)
                col1.metric("🔴 Critical Issues", f"{len(critical):,}")
                col2.metric("🟠 Warnings", f"{len(warnings):,}")
                col3.metric("🟢 Potential Wins", f"{len(wins):,}")

                with st.expander("🔴 View Critical Issues"):
                    st.markdown("**Low CTR (<1%) with High Impressions (>1000)**")
                    st.dataframe(critical, use_container_width=True) if not critical.empty else st.info("No critical issues found.")

                with st.expander("🟠 View Warning Keywords"):
                    st.markdown("**Impression Surge but Low Clicks (<10)**")
                    st.dataframe(warnings, use_container_width=True) if not warnings.empty else st.info("No warnings found.")

                with st.expander("🟢 View High-CTR, Low-Rank Wins"):
    st.markdown("**High CTR (>10%) but Low Ranking (Position >10)**")
    if not wins.empty:
        st.dataframe(wins, use_container_width=True)
    else:
        st.info("No wins found.")

                st.subheader("🔝 Top Queries by Clicks")
                st.dataframe(queries_df.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

                st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
                opp = queries_df[(queries_df["position"].between(5, 15)) & (queries_df["ctr"] < 5)]
                st.markdown(f"**Total Opportunities:** {len(opp)}")
                st.dataframe(opp.sort_values(by="impressions", ascending=False), use_container_width=True)

                st.download_button("📥 Download Opportunities as CSV", data=opp.to_csv(index=False), file_name="excel_opportunity_keywords.csv", mime="text/csv")

        # --------------------------------
        # PAGES TAB
        # --------------------------------
        with tabs[1]:
            pages_df = all_sheets.get("Pages")
            if pages_df is not None:
                pages_df.columns = [col.strip().lower().replace(" ", "_") for col in pages_df.columns]
                st.subheader("📄 Top Pages by Clicks")
                pages_df["clicks"] = pages_df["clicks"].astype(str).str.replace(",", "").astype(float)
                pages_df["impressions"] = pages_df["impressions"].astype(str).str.replace(",", "").astype(float)
                pages_df["ctr"] = pages_df["ctr"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
                pages_df["position"] = pages_df["position"].astype(str).str.replace(",", "").astype(float)
                st.dataframe(pages_df.sort_values(by="clicks", ascending=False).head(20), use_container_width=True)
            else:
                st.warning("⚠️ No 'Pages' sheet found in the Excel file.")

        # --------------------------------
        # COUNTRIES TAB
        # --------------------------------
        with tabs[2]:
            countries_df = all_sheets.get("Countries")
            if countries_df is not None:
                countries_df.columns = [col.strip().lower().replace(" ", "_") for col in countries_df.columns]
                st.subheader("🌍 Top Countries by Clicks")
                countries_df["clicks"] = countries_df["clicks"].astype(str).str.replace(",", "").astype(float)
                countries_df["impressions"] = countries_df["impressions"].astype(str).str.replace(",", "").astype(float)
                countries_df["ctr"] = countries_df["ctr"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
                countries_df["position"] = countries_df["position"].astype(str).str.replace(",", "").astype(float)
                st.dataframe(countries_df.sort_values(by="clicks", ascending=False).head(20), use_container_width=True)
            else:
                st.warning("⚠️ No 'Countries' sheet found in the Excel file.")
