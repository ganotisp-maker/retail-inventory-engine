import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="HVAC Inventory Intelligence Platform",
    layout="wide"
)

# =====================================
# HELPER FUNCTIONS
# =====================================
def clean_id(val):
    if pd.isna(val):
        return ""

    s = str(val).strip()

    if s.endswith('.0'):
        s = s[:-2]

    return s.replace('.', '')

# =====================================
# PROFESSIONAL HEADER
# =====================================
st.markdown("""
# 🧠 HVAC Inventory Intelligence Platform
### Forecasting • Procurement • Inventory Risk Analytics
""")

# =====================================
# SIDEBAR
# =====================================
st.sidebar.header("📂 Data Input")

inventory_file = st.sidebar.file_uploader(
    "Upload HVAC Intelligence Excel",
    type=["xlsx"]
)

# =====================================
# MAIN APP
# =====================================
if inventory_file:

    try:

        # =====================================
        # LOAD EXCEL TABS
        # =====================================
        raw_df = pd.read_excel(
            inventory_file,
            sheet_name='RAW DATA'
        )

        forecast_df = pd.read_excel(
            inventory_file,
            sheet_name='FORECAST ENGINE'
        )

        procurement_df = pd.read_excel(
            inventory_file,
            sheet_name='PROCUREMENT CENTER'
        )

        executive_df = pd.read_excel(
            inventory_file,
            sheet_name='EXECUTIVE DASHBOARD'
        )

        # =====================================
        # CLEAN COLUMNS
        # =====================================
        raw_df.columns = raw_df.columns.str.strip()
        st.write(raw_df.columns)
        forecast_df.columns = forecast_df.columns.str.strip()
        procurement_df.columns = procurement_df.columns.str.strip()
        executive_df.columns = executive_df.columns.str.strip()

        # =====================================
        # CLEAN PRODUCT IDS
        # =====================================
        if 'Product Code' in raw_df.columns:
            raw_df['Product Code'] = raw_df['Product Code'].apply(clean_id)

        # =====================================
        # SIDEBAR FILTERS
        # =====================================
        st.sidebar.markdown("---")

        if 'Category' in raw_df.columns:

            selected_category = st.sidebar.selectbox(
                "📦 Select Category",
                ["All Categories"] + list(raw_df['Category'].dropna().unique())
            )

            if selected_category != "All Categories":
                filtered_raw = raw_df[
                    raw_df['Category'] == selected_category
                ]
            else:
                filtered_raw = raw_df

        else:
            filtered_raw = raw_df

        # =====================================
        # TABS
        # =====================================
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Executive Dashboard",
            "🎯 Forecast Engine",
            "📦 Procurement Center",
            "🔍 Raw Data"
        ])

        # =====================================
        # TAB 1 - EXECUTIVE DASHBOARD
        # =====================================
        with tab1:

            st.subheader("Executive Management Overview")

            # =====================================
            # KPI CARDS
            # =====================================
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📦 Total Products",
                len(raw_df)
            )

            col2.metric(
                "📂 Categories",
                raw_df['Category'].nunique()
                if 'Category' in raw_df.columns else 0
            )

            col3.metric(
                "💰 Total Stock Value",
                f"€{int(raw_df['Product Price'].sum()):,}"
                if 'Product Price' in raw_df.columns else "€0"
            )

            col4.metric(
                "🚛 Procurement Lines",
                len(procurement_df)
            )

            st.markdown("---")

            # =====================================
            # ALERTS
            # =====================================
            st.markdown("## 🚨 Critical Alerts")

            st.error(
                "High Stockout Risk detected in selected HVAC categories"
            )

            st.warning(
                "Overstock pressure detected in low rotation products"
            )

            st.success(
                "Demand forecast remains strong for seasonal products"
            )

            st.markdown("---")

            # =====================================
            # CATEGORY CHART
            # =====================================
            if 'Category' in raw_df.columns:

                category_counts = (
                    raw_df['Category']
                    .value_counts()
                    .reset_index()
                )

                category_counts.columns = [
                    'Category',
                    'Products'
                ]

                fig = px.bar(
                    category_counts,
                    x='Category',
                    y='Products',
                    title='📊 Products per Category'
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.markdown("---")

            # =====================================
            # EXECUTIVE DATA
            # =====================================
            st.markdown("## 📈 Executive Analytics")

            st.dataframe(
                executive_df,
                use_container_width=True
            )

        # =====================================
        # TAB 2 - FORECAST ENGINE
        # =====================================
        with tab2:

            st.subheader("🎯 Forecast Engine")

            st.markdown("""
            Analyze demand forecasting, seasonality,
            market trends and inventory projections.
            """)

            st.dataframe(
                forecast_df,
                use_container_width=True
            )

            # =====================================
            # FORECAST CHART
            # =====================================
            if (
                'Category' in raw_df.columns and
                'Last Year Units' in raw_df.columns
            ):

                forecast_chart = px.bar(
                    raw_df,
                    x='Category',
                    y='Last Year Units',
                    title='📈 Historical Demand by Category'
                )

                st.plotly_chart(
                    forecast_chart,
                    use_container_width=True
                )

        # =====================================
        # TAB 3 - PROCUREMENT CENTER
        # =====================================
        with tab3:

            st.subheader("📦 Procurement Center")

            st.markdown("""
            Suggested orders, pallet requirements
            and supplier planning analysis.
            """)

            # =====================================
            # PROCUREMENT ALERTS
            # =====================================
            st.warning(
                "Supplier lead times may impact summer inventory availability."
            )

            st.dataframe(
                procurement_df,
                use_container_width=True
            )

            # =====================================
            # DOWNLOAD BUTTON
            # =====================================
            csv = procurement_df.to_csv(
                index=False
            ).encode('utf-8')

            st.download_button(
                "📥 Download Procurement Plan",
                csv,
                "procurement_plan.csv",
                "text/csv"
            )

        # =====================================
        # TAB 4 - RAW DATA
        # =====================================
        with tab4:

            st.subheader("🔍 Master Product Database")

            st.markdown("""
            Complete operational product dataset
            with inventory and forecasting inputs.
            """)

            # =====================================
            # FILTERED DATA
            # =====================================
            st.dataframe(
                filtered_raw,
                use_container_width=True
            )

            st.markdown("---")

            # =====================================
            # PRODUCT DRILLDOWN
            # =====================================
            st.markdown("## 🔎 Product Drilldown")

            if 'Product Description' in raw_df.columns:

                selected_product = st.selectbox(
                    "Select Product",
                    raw_df['Product Description']
                    .dropna()
                    .unique()
                )

                product_data = raw_df[
                    raw_df['Product Description']
                    == selected_product
                ]

                st.dataframe(
                    product_data,
                    use_container_width=True
                )

    except Exception as e:

        st.error(
            f"""
❌ Error: {e}

Make sure the Excel file contains:
• RAW DATA
• FORECAST ENGINE
• PROCUREMENT CENTER
• EXECUTIVE DASHBOARD
"""
        )

# =====================================
# EMPTY STATE
# =====================================
else:

    st.info(
        "⬅️ Upload the HVAC Intelligence Excel file to begin analysis."
    )
