import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="MWBE Vendor Intelligence",
    page_icon="📊",
    layout="wide"
)

DATA_PATH = Path("data/processed/mwbe_vendor_intelligence_enriched.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

df = load_data()

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1450px;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    [data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 800;
    }

    [data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        padding: 34px;
        border-radius: 24px;
        background: linear-gradient(135deg,#111827,#1e3a8a,#2563eb);
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px rgba(15,23,42,0.18);
    ">
        <h1 style="font-size:44px;margin-bottom:10px;">MWBE Vendor Intelligence Dashboard</h1>
        <p style="font-size:18px;color:#dbeafe;max-width:900px;">
            Operational analytics for certified MWBE vendors, procurement participation,
            vendor readiness, industry concentration, and supplier diversity intelligence.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar filters
st.sidebar.title("Filters")

boroughs = sorted(df["borough_clean"].dropna().unique()) if "borough_clean" in df else []
industries = sorted(df["naics_sector"].dropna().unique()) if "naics_sector" in df else []

selected_boroughs = st.sidebar.multiselect(
    "Borough",
    boroughs,
    default=boroughs
)

selected_industries = st.sidebar.multiselect(
    "Industry",
    industries,
    default=industries
)

filtered_df = df.copy()

if selected_boroughs:
    filtered_df = filtered_df[filtered_df["borough_clean"].isin(selected_boroughs)]

if selected_industries:
    filtered_df = filtered_df[filtered_df["naics_sector"].isin(selected_industries)]

# KPI section
total_vendors = len(filtered_df)
procurement_vendors = int(filtered_df["has_procurement_award"].sum())
procurement_rate = procurement_vendors / total_vendors * 100 if total_vendors else 0
total_procurement_value = filtered_df["total_procurement_value"].sum()
avg_readiness = filtered_df["operational_readiness_score"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Certified Vendors", f"{total_vendors:,}")
c2.metric("Procurement-Active Vendors", f"{procurement_vendors:,}")
c3.metric("Procurement Match Rate", f"{procurement_rate:.1f}%")
c4.metric("Avg Readiness Score", f"{avg_readiness:.2f}")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Executive Overview",
        "Procurement Intelligence",
        "Vendor Readiness",
        "Geography",
        "Data Explorer"
    ]
)

with tab1:
    st.subheader("Executive Overview")

    col1, col2 = st.columns(2)

    industry_counts = (
        filtered_df["naics_sector"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    industry_counts.columns = ["naics_sector", "vendor_count"]

    fig1 = px.bar(
        industry_counts,
        x="vendor_count",
        y="naics_sector",
        orientation="h",
        title="Top Industries by Certified Vendor Count",
        labels={"vendor_count": "Vendor Count", "naics_sector": "Industry"},
        template="plotly_white"
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"})

    col1.plotly_chart(fig1, use_container_width=True)

    readiness_counts = (
        filtered_df["operational_readiness_segment"]
        .value_counts(dropna=False)
        .reset_index()
    )
    readiness_counts.columns = ["segment", "vendor_count"]

    fig2 = px.pie(
        readiness_counts,
        names="segment",
        values="vendor_count",
        title="Operational Readiness Segmentation",
        hole=0.45,
        template="plotly_white"
    )

    col2.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Procurement Intelligence")

    col1, col2 = st.columns(2)

    proc_by_industry = (
        filtered_df.groupby("naics_sector", dropna=False)
        .agg(total_procurement_value=("total_procurement_value", "sum"))
        .sort_values("total_procurement_value", ascending=False)
        .head(10)
        .reset_index()
    )

    fig3 = px.bar(
        proc_by_industry,
        x="total_procurement_value",
        y="naics_sector",
        orientation="h",
        title="Top Industries by Procurement Value",
        labels={
            "total_procurement_value": "Procurement Value",
            "naics_sector": "Industry"
        },
        template="plotly_white"
    )
    fig3.update_layout(yaxis={"categoryorder": "total ascending"})

    col1.plotly_chart(fig3, use_container_width=True)

    participation = (
        filtered_df["has_procurement_award"]
        .value_counts()
        .reset_index()
    )
    participation.columns = ["has_procurement_award", "vendor_count"]
    participation["status"] = participation["has_procurement_award"].map(
        {0: "No Procurement Award", 1: "Has Procurement Award"}
    )

    fig4 = px.bar(
        participation,
        x="status",
        y="vendor_count",
        title="Procurement Participation",
        labels={"status": "", "vendor_count": "Vendor Count"},
        template="plotly_white"
    )

    col2.plotly_chart(fig4, use_container_width=True)

    st.markdown("### High Readiness / Low Procurement Activity Vendors")

    opportunity_df = filtered_df[
        (filtered_df["operational_readiness_score"] >= 0.70)
        & (filtered_df["procurement_activity_score"] <= 0.30)
    ][
        [
            "vendor_formal_name",
            "naics_sector",
            "borough_clean",
            "operational_readiness_score",
            "procurement_activity_score",
            "vendor_capacity_score"
        ]
    ].sort_values("operational_readiness_score", ascending=False)

    st.dataframe(opportunity_df.head(25), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Vendor Readiness")

    col1, col2 = st.columns(2)

    fig5 = px.histogram(
        filtered_df,
        x="operational_readiness_score",
        nbins=25,
        title="Operational Readiness Score Distribution",
        labels={"operational_readiness_score": "Readiness Score"},
        template="plotly_white"
    )

    col1.plotly_chart(fig5, use_container_width=True)

    fig6 = px.scatter(
        filtered_df,
        x="vendor_capacity_score",
        y="procurement_activity_score",
        color="operational_readiness_segment",
        hover_name="vendor_formal_name",
        title="Vendor Capacity vs Procurement Activity",
        labels={
            "vendor_capacity_score": "Vendor Capacity Score",
            "procurement_activity_score": "Procurement Activity Score"
        },
        template="plotly_white"
    )

    col2.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.subheader("Geographic Intelligence")

    col1, col2 = st.columns(2)

    borough_counts = (
        filtered_df["borough_clean"]
        .value_counts()
        .reset_index()
    )
    borough_counts.columns = ["borough", "vendor_count"]

    fig7 = px.bar(
        borough_counts,
        x="borough",
        y="vendor_count",
        title="Certified Vendor Distribution by Borough",
        labels={"borough": "Borough", "vendor_count": "Vendor Count"},
        template="plotly_white"
    )

    col1.plotly_chart(fig7, use_container_width=True)

    if {"latitude", "longitude"}.issubset(filtered_df.columns):
        map_df = filtered_df.dropna(subset=["latitude", "longitude"]).copy()

        fig8 = px.scatter_mapbox(
            map_df,
            lat="latitude",
            lon="longitude",
            color="borough_clean",
            hover_name="vendor_formal_name",
            hover_data=["naics_sector", "operational_readiness_score"],
            zoom=9,
            height=500,
            title="Vendor Geographic Distribution"
        )

        fig8.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )

        col2.plotly_chart(fig8, use_container_width=True)

with tab5:
    st.subheader("Data Explorer")

    search = st.text_input("Search vendor name")

    display_df = filtered_df.copy()

    if search:
        display_df = display_df[
            display_df["vendor_formal_name"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv = display_df.to_csv(index=False)

    st.download_button(
        "Download Filtered Data",
        csv,
        "mwbe_vendor_intelligence_filtered.csv",
        "text/csv"
    )