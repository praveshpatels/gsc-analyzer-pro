import streamlit as st
import pandas as pd
import numpy as np
import io

# Page Setup
st.set_page_config(page_title="GSC Analyzer Pro - Pravesh Patel", page_icon="🔍", layout="wide")
st.title("🔍 Google Search Console Analyzer Pro")
st.markdown("*Developed by **Pravesh Patel***", unsafe_allow_html=True)

# Sidebar Bio
st.sidebar.markdown("## 👨‍💻 About the Developer")
st.sidebar.markdown("""
Hi, I'm **Pravesh Patel** — a passionate SEO Manager and Data Enthusiast.

🔍 I specialize in SEO, analytics, and tools that simplify Google Search Console data.

💼 I build tools like this to find content opportunities faster.
""")

# Tabs
tab1, tab2 = st.tabs(["📄 CSV Analyzer", "📊 Excel Analyzer"])

# ====================
# TAB 1: CSV ANALYZER
# ====================
with tab1:
    st.header("📄 GSC CSV Analyzer")
    uploaded_file = st.file_uploader("📁 Upload CSV File (Performance > Queries)", type=["csv"], key="csv_uploader")

    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(raw_data))
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df.rename(columns={"top_queries": "query"}, inplace=True)

        for col in ["clicks", "impressions", "position"]:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["ctr"] = df["ctr"].astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False)
        df["ctr"] = pd.to_numeric(df["ctr"], errors="coerce")
        df.dropna(subset=["clicks", "impressions", "ctr", "position"], how="all", inplace=True)

        with st.expander("🔍 Filter Data for KPIs & Top Queries"):
            min_impr = st.slider("Minimum Impressions", 0, int(df["impressions"].max()), 0, key="csv_min_impr")
            keyword_filter = st.text_input("Filter by Query (Optional)", "", key="csv_kw_filter")

        df_filtered = df.copy()
        if min_impr > 0:
            df_filtered = df_filtered[df_filtered["impressions"] >= min_impr]
        if keyword_filter:
            df_filtered = df_filtered[df_filtered["query"].str.contains(keyword_filter, case=False, na=False)]

        # KPIs
        st.subheader("📊 Overall Performance (Filtered)")
        total_clicks = df_filtered["clicks"].sum()
        total_impressions = df_filtered["impressions"].sum()
        avg_ctr = (df_filtered["ctr"] * df_filtered["impressions"]).sum() / total_impressions if total_impressions else 0
        avg_position = (df_filtered["position"] * df_filtered["impressions"]).sum() / total_impressions if total_impressions else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clicks", f"{total_clicks:,.0f}")
        col2.metric("Total Impressions", f"{total_impressions:,.0f}")
        col3.metric("Avg. CTR", f"{avg_ctr:.2f}%")
        col4.metric("Avg. Position", f"{avg_position:.2f}")

        # Top Queries
        st.subheader("🔝 Top Queries by Clicks (Filtered)")
        st.dataframe(df_filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

        # Opportunities from full data
        st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
        opportunities = df[(df["position"] >= 5) & (df["position"] <= 15) & (df["ctr"] < 5)]
        st.markdown(f"**Total Opportunities:** {len(opportunities)}")
        st.dataframe(opportunities.sort_values(by="impressions", ascending=False), use_container_width=True)
        st.download_button(
            "📥 Download Opportunities as CSV",
            data=opportunities.to_csv(index=False),
            file_name="csv_opportunity_keywords.csv",
            mime="text/csv"
        )

        # Alerts from full data
        st.subheader("🚨 Keyword Alerts (SEO Insights)")
        low_ctr_alerts = df[(df["impressions"] > 1000) & (df["ctr"] < 1.0)]
        surge_alerts = df[(df["impressions"] > 1000) & (df["clicks"] < 10) & (df["ctr"] < 1.0)]
        booster_alerts = df[(df["ctr"] > 10.0) & (df["position"] > 10)]

        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Critical Issue", f"{len(low_ctr_alerts):,}")
        col2.metric("🟠 Warning", f"{len(surge_alerts):,}")
        col3.metric("🟢 Potential Win", f"{len(booster_alerts):,}")

        with st.expander("🔴 Low CTR (<1%) with High Impressions"):
            st.dataframe(low_ctr_alerts.head(20), use_container_width=True)

        with st.expander("🟠 Impression Surge but Low Clicks (<10)"):
            st.dataframe(surge_alerts.head(20), use_container_width=True)

        with st.expander("🟢 High CTR (>10%) but Low Ranking (Position >10)"):
            st.dataframe(booster_alerts.head(20), use_container_width=True)

# =====================================
# TAB 2: EXCEL ANALYZER (Enhanced with Alerts)
# =====================================
with tab2:
    st.header("📊 GSC Excel Analyzer")
    excel_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"], key="excel_uploader")

    if excel_file:
        all_sheets = pd.read_excel(excel_file, sheet_name=None)

        # ========== QUERIES SHEET ==========
        queries_df = all_sheets.get("Queries")
        if queries_df is not None:
            queries_df.columns = [col.strip().lower().replace(" ", "_") for col in queries_df.columns]
            queries_df.rename(columns={"top_queries": "query"}, inplace=True)

            for col in ["clicks", "impressions", "position"]:
                queries_df[col] = queries_df[col].astype(str).str.replace(",", "").astype(float)

            queries_df["ctr"] = (
                queries_df["ctr"]
                .astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False)
                .astype(float)
            )

            if queries_df["ctr"].max() <= 1:
                queries_df["ctr"] *= 100

            queries_df.dropna(subset=["query", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)

            with st.expander("🔍 Filter Data"):
                min_impr = st.slider("Minimum Impressions", 0, int(queries_df["impressions"].max()), 100, key="excel_min_impr")
                keyword_filter = st.text_input("Filter by Query (Optional)", "", key="excel_kw_filter")

            queries_filtered = queries_df.copy()
            if min_impr > 0:
                queries_filtered = queries_filtered[queries_filtered["impressions"] >= min_impr]
            if keyword_filter:
                queries_filtered = queries_filtered[queries_filtered["query"].str.contains(keyword_filter, case=False, na=False)]

            st.subheader("📊 Performance Metrics")
            total_clicks = queries_filtered["clicks"].sum()
            total_impr = queries_filtered["impressions"].sum()
            avg_ctr = (queries_filtered["ctr"] * queries_filtered["impressions"]).sum() / total_impr if total_impr else 0
            avg_pos = (queries_filtered["position"] * queries_filtered["impressions"]).sum() / total_impr if total_impr else 0

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
                st.dataframe(critical if not critical.empty else pd.DataFrame(), use_container_width=True)

            with st.expander("🟠 View Warning Keywords"):
                st.markdown("**Impression Surge but Low Clicks (<10)**")
                st.dataframe(warnings if not warnings.empty else pd.DataFrame(), use_container_width=True)

            with st.expander("🟢 View High-CTR, Low-Rank Wins"):
                st.markdown("**High CTR (>10%) but Low Ranking (Position >10)**")
                st.dataframe(wins if not wins.empty else pd.DataFrame(), use_container_width=True)
            
            # 🧠 AI Summary
            st.subheader("🧠 AI-Powered Recommendations")

            insights = []

            if len(critical) > 0:
                insights.append(f"You have **{len(critical)} keywords** with high impressions but CTR below 1%. Improve meta titles and descriptions.")
            if len(warnings) > 0:
                insights.append(f"Found **{len(warnings)} keywords** gaining impressions but not enough clicks. Consider content freshness or intent mismatch.")
            if len(wins) > 0:
                insights.append(f"Spotted **{len(wins)} high-CTR keywords** ranking low. These are strong candidates for internal linking or schema enhancements.")
            if 'opp' in locals() and len(opp) > 0:
                insights.append(f"Identified **{len(opp)} opportunity keywords** between position 5–15 and CTR under 5%. You might push these to top 3 positions.")

            if insights:
                for tip in insights:
                    st.markdown(f"- {tip}")
            else:
                st.info("No significant issues or opportunities found in this dataset.")
            

            st.subheader("🔝 Top Queries by Clicks")
            st.dataframe(queries_filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

            st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
            opp = queries_df[(queries_df["position"].between(5, 15)) & (queries_df["ctr"] < 5)]
            st.markdown(f"**Total Opportunities:** {len(opp)}")
            st.dataframe(opp.sort_values(by="impressions", ascending=False), use_container_width=True)
            st.download_button("📥 Download Opportunities as CSV", data=opp.to_csv(index=False), file_name="excel_opportunity_keywords.csv", mime="text/csv")

        # ========== PAGES SHEET ==========
        pages_df = all_sheets.get("Pages")
        if pages_df is not None:
            st.subheader("🌐 Top Pages Performance")
            pages_df.columns = [col.strip().lower().replace(" ", "_") for col in pages_df.columns]
            pages_df.rename(columns={"top_pages": "page"}, inplace=True)
            for col in ["clicks", "impressions", "position"]:
                pages_df[col] = pages_df[col].astype(str).str.replace(",", "").astype(float)
            pages_df["ctr"] = pages_df["ctr"].astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False).astype(float)
            if pages_df["ctr"].max() <= 1:
                pages_df["ctr"] *= 100
            pages_df.dropna(subset=["page", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)
            with st.expander("🔍 Filter Pages Data"):
                min_page_impr = st.slider("Minimum Impressions (Pages)", 0, int(pages_df["impressions"].max()), 0, key="page_min_impr")
                pages_df_filtered = pages_df[pages_df["impressions"] >= min_page_impr]
            st.markdown(f"**Total Pages:** {len(pages_df_filtered)}")
            st.dataframe(pages_df_filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)
            st.download_button("📥 Download Pages Data", data=pages_df_filtered.to_csv(index=False), file_name="pages_data.csv", mime="text/csv")

        # ========== COUNTRIES SHEET ==========
        countries_df = all_sheets.get("Countries")
        if countries_df is not None:
            st.subheader("🌍 Top Countries Performance")
            countries_df.columns = [col.strip().lower().replace(" ", "_") for col in countries_df.columns]
            countries_df.rename(columns={"top_countries": "country"}, inplace=True)
            for col in ["clicks", "impressions", "position"]:
                countries_df[col] = countries_df[col].astype(str).str.replace(",", "").astype(float)
            countries_df["ctr"] = countries_df["ctr"].astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False).astype(float)
            if countries_df["ctr"].max() <= 1:
                countries_df["ctr"] *= 100
            countries_df.dropna(subset=["country", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)
            with st.expander("🔍 Filter Countries Data"):
                min_country_impr = st.slider("Minimum Impressions (Countries)", 0, int(countries_df["impressions"].max()), 0, key="country_min_impr")
                countries_df_filtered = countries_df[countries_df["impressions"] >= min_country_impr]
            st.markdown(f"**Total Countries:** {len(countries_df_filtered)}")
            st.dataframe(countries_df_filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)
            st.download_button("📥 Download Countries Data", data=countries_df_filtered.to_csv(index=False), file_name="countries_data.csv", mime="text/csv")

