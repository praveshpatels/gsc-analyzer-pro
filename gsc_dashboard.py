import streamlit as st
import pandas as pd
import io
import plotly.express as px

# Page Config
st.set_page_config(page_title="GSC Analyzer Pro - Pravesh Patel", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .css-18e3th9 {padding-top: 1rem;}
    .css-1d391kg {padding-top: 0rem; padding-bottom: 0rem;}
    .css-1kyxreq {padding-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

st.title("🔍 Google Search Console Analyzer Pro")
st.caption("Developed by Pravesh Patel")

# Tabs
tab1, tab2 = st.tabs(["📄 CSV Analyzer", "📊 Excel Analyzer"])

# =============================
# 📄 CSV Analyzer
# =============================
with tab1:
    with st.expander("🔍 Filter Data for KPIs & Top Queries", expanded=True):
        csv_file = st.file_uploader("Upload CSV File (Performance > Queries)", type=["csv"])

    if csv_file:
        raw = csv_file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(raw))
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        df.rename(columns={"top_queries": "query"}, inplace=True)

        for col in ["clicks", "impressions", "position"]:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors='coerce')
        df["ctr"] = pd.to_numeric(df["ctr"].astype(str).str.replace("%", "").str.replace(",", ""), errors='coerce')
        df.dropna(subset=["query", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)

        min_impr = st.slider("Minimum Impressions", 0, int(df["impressions"].max()), 0)
        keyword_filter = st.text_input("Filter by Query (Optional)", "")

        filtered = df[df["impressions"] >= min_impr]
        if keyword_filter:
            filtered = filtered[filtered["query"].str.contains(keyword_filter, case=False, na=False)]

        st.subheader("📊 Overall Performance (Filtered)")
        total_clicks = filtered["clicks"].sum()
        total_impr = filtered["impressions"].sum()
        avg_ctr = (filtered["ctr"] * filtered["impressions"]).sum() / total_impr if total_impr else 0
        avg_pos = (filtered["position"] * filtered["impressions"]).sum() / total_impr if total_impr else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", f"{total_clicks:,.0f}")
        col2.metric("Clicks", f"{total_impr:,.0f}")
        col3.metric("Avg. CTR", f"{avg_ctr:.2f}%")
        col4.metric("Avg. Position", f"{avg_pos:.2f}")

        st.subheader("📈 CTR vs Position Trend")
        fig = px.scatter(filtered, x="position", y="ctr", hover_data=["query"], trendline="ols")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔝 Top Queries by Clicks")
        st.dataframe(filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

        st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
        opp = df[(df["position"].between(5, 15)) & (df["ctr"] < 5)]
        st.markdown(f"**Total Opportunities**: {len(opp)}")
        st.dataframe(opp.sort_values(by="impressions", ascending=False), use_container_width=True)
        st.download_button("📥 Download Opportunities as CSV", opp.to_csv(index=False), file_name="csv_opportunity_keywords.csv", mime="text/csv")

# =============================
# 📊 Excel Analyzer
# =============================
with tab2:
    with st.expander("🔍 Filter Data", expanded=True):
        excel_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

    if excel_file:
        sheets = pd.read_excel(excel_file, sheet_name=None)
        queries_df = sheets.get("Queries")
        if queries_df is not None:
            queries_df.columns = [c.strip().lower().replace(" ", "_") for c in queries_df.columns]
            queries_df.rename(columns={"top_queries": "query"}, inplace=True)

            for col in ["clicks", "impressions", "position"]:
                queries_df[col] = pd.to_numeric(queries_df[col].astype(str).str.replace(",", ""), errors='coerce')
            queries_df["ctr"] = pd.to_numeric(queries_df["ctr"].astype(str).str.replace("%", "").str.replace(",", ""), errors='coerce')
            if queries_df["ctr"].max() <= 1:
                queries_df["ctr"] *= 100

            queries_df.dropna(subset=["query", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)

            min_impr = st.slider("Minimum Impressions", 0, int(queries_df["impressions"].max()), 100)
            keyword_filter = st.text_input("Filter by Query (Optional)", "")

            filtered = queries_df[queries_df["impressions"] >= min_impr]
            if keyword_filter:
                filtered = filtered[filtered["query"].str.contains(keyword_filter, case=False, na=False)]

            st.subheader("📊 Performance Metrics")
            total_clicks = filtered["clicks"].sum()
            total_impr = filtered["impressions"].sum()
            avg_ctr = (filtered["ctr"] * filtered["impressions"]).sum() / total_impr if total_impr else 0
            avg_pos = (filtered["position"] * filtered["impressions"]).sum() / total_impr if total_impr else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Clicks", f"{total_clicks:,.0f}")
            col2.metric("Total Impressions", f"{total_impr:,.0f}")
            col3.metric("Avg. CTR", f"{avg_ctr:.2f}%")
            col4.metric("Avg. Position", f"{avg_pos:.2f}")

            st.subheader("🔔 Alerts Dashboard")
            critical = queries_df[(queries_df["ctr"] < 1.0) & (queries_df["impressions"] > 1000)]
            warnings = queries_df[(queries_df["impressions"] > 1000) & (queries_df["clicks"] < 10)]
            wins = queries_df[(queries_df["ctr"] > 10.0) & (queries_df["position"] > 10)]

            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 Critical", f"{len(critical)}")
            col2.metric("🟠 Warnings", f"{len(warnings)}")
            col3.metric("🟢 Wins", f"{len(wins)}")

            with st.expander("🔴 View Critical Issues"):
                st.dataframe(critical.head(20), use_container_width=True)
            with st.expander("🟠 View Warning Keywords"):
                st.dataframe(warnings.head(20), use_container_width=True)
            with st.expander("🟢 View Wins"):
                st.dataframe(wins.head(20), use_container_width=True)

            st.subheader("🧠 AI-Powered Recommendations")
            insights = []
            if len(critical): insights.append(f"Improve meta for **{len(critical)}** low CTR keywords with high impressions.")
            if len(warnings): insights.append(f"Check **{len(warnings)}** keywords gaining impressions but low clicks.")
            if len(wins): insights.append(f"Boost **{len(wins)}** high CTR keywords ranking low using internal linking.")
            opp = queries_df[(queries_df["position"].between(5, 15)) & (queries_df["ctr"] < 5)]
            if len(opp): insights.append(f"You have **{len(opp)} opportunity keywords** between position 5–15 and CTR < 5%.")
            for i in insights:
                st.markdown(f"- {i}")
            if not insights:
                st.info("No significant issues or opportunities found in this dataset.")

            st.subheader("🔝 Top Queries by Clicks")
            st.dataframe(filtered.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)

            st.subheader("💡 Opportunity Keywords (Position 5–15, CTR < 5%)")
            st.markdown(f"**Total Opportunities**: {len(opp)}")
            st.dataframe(opp.sort_values(by="impressions", ascending=False), use_container_width=True)
            st.download_button("📥 Download Opportunities as CSV", opp.to_csv(index=False), file_name="excel_opportunity_keywords.csv", mime="text/csv")

        # ========== PAGES SHEET ==========
        pages_df = sheets.get("Pages")
        if pages_df is not None:
            st.subheader("🌐 Top Pages Performance")
            pages_df.columns = [c.strip().lower().replace(" ", "_") for c in pages_df.columns]
            pages_df.rename(columns={"top_pages": "page"}, inplace=True)
            for col in ["clicks", "impressions", "position"]:
                pages_df[col] = pd.to_numeric(pages_df[col].astype(str).str.replace(",", ""), errors='coerce')
            pages_df["ctr"] = pd.to_numeric(pages_df["ctr"].astype(str).str.replace("%", "").str.replace(",", ""), errors='coerce')
            if pages_df["ctr"].max() <= 1:
                pages_df["ctr"] *= 100
            pages_df.dropna(subset=["page", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)
            st.dataframe(pages_df.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)
            st.download_button("📥 Download Pages Data", pages_df.to_csv(index=False), file_name="pages_data.csv", mime="text/csv")

        # ========== COUNTRIES SHEET ==========
        countries_df = sheets.get("Countries")
        if countries_df is not None:
            st.subheader("🌍 Top Countries Performance")
            countries_df.columns = [c.strip().lower().replace(" ", "_") for c in countries_df.columns]
            countries_df.rename(columns={"top_countries": "country"}, inplace=True)
            for col in ["clicks", "impressions", "position"]:
                countries_df[col] = pd.to_numeric(countries_df[col].astype(str).str.replace(",", ""), errors='coerce')
            countries_df["ctr"] = pd.to_numeric(countries_df["ctr"].astype(str).str.replace("%", "").str.replace(",", ""), errors='coerce')
            if countries_df["ctr"].max() <= 1:
                countries_df["ctr"] *= 100
            countries_df.dropna(subset=["country", "clicks", "impressions", "ctr", "position"], how="all", inplace=True)
            st.dataframe(countries_df.sort_values(by="clicks", ascending=False).head(10), use_container_width=True)
            st.download_button("📥 Download Countries Data", countries_df.to_csv(index=False), file_name="countries_data.csv", mime="text/csv")
