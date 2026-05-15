import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    layout="wide"
)

# =====================================
# HELPER FUNCTIONS
# =====================================
def clean_id(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    return s.replace('.', '')

# =====================================
# SIDEBAR - DATA INPUT
# =====================================
st.sidebar.header("📂 Data Input")
inventory_file = st.sidebar.file_uploader(
    "Upload Retail Intelligence Excel", 
    type=["xlsx"], 
    key="multi_tab_loader"
)

# =====================================
# MAIN LOGIC
# =====================================
st.title("📊 Retail Intelligence Dashboard")

if inventory_file:
    try:
        # 1. Φόρτωση όλων των απαραίτητων Tabs
        # Διαβάζουμε κάθε tab σε ξεχωριστό DataFrame
        raw_df = pd.read_excel(inventory_file, sheet_name='RAW DATA')
        forecast_df = pd.read_excel(inventory_file, sheet_name='FORECAST ENGINE')
        procurement_df = pd.read_excel(inventory_file, sheet_name='PROCUREMENT CENTER')
        executive_df = pd.read_excel(inventory_file, sheet_name='EXECUTIVE DASHBOARD')

        # Καθαρισμός IDs όπου χρειάζεται
        if 'Product Code' in raw_df.columns:
            raw_df['Product Code'] = raw_df['Product Code'].apply(clean_id)

        # 2. Πλοήγηση στην εφαρμογή (Tabs στο Streamlit)
        st.markdown("---")
        st_tabs = st.tabs(["📈 Executive Dashboard", "🎯 Forecast Engine", "📦 Procurement Center", "🔍 Raw Data"])

        # --- TAB 1: EXECUTIVE DASHBOARD ---
        with st_tabs[0]:
            st.subheader("Executive Management Overview")
            # Εμφάνιση των KPIs από το Executive tab
            st.dataframe(executive_df, use_container_width=True)
            
            # Δημιουργία γραφήματος αν υπάρχει στήλη Turnover ή Category
            if 'Category' in executive_df.columns:
                fig = px.bar(executive_df, x='Category', y=executive_df.columns[1], 
                             title="Category Analysis Overview")
                st.plotly_chart(fig, use_container_width=True)

        # --- TAB 2: FORECAST ENGINE ---
        with st_tabs[1]:
            st.subheader("Sales Forecasting Analysis")
            st.dataframe(forecast_df, use_container_width=True)

        # --- TAB 3: PROCUREMENT CENTER ---
        with st_tabs[2]:
            st.subheader("Suggested Orders & Stock Requirements")
            st.dataframe(procurement_df, use_container_width=True)
            
            # Download button για το πλάνο παραγγελιών
            csv = procurement_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Procurement Plan", csv, "orders.csv", "text/csv")

        # --- TAB 4: RAW DATA ---
        with st_tabs[3]:
            st.subheader("Master Product Database")
            st.dataframe(raw_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}. Βεβαιωθείτε ότι το Excel περιέχει τα tabs: 'RAW DATA', 'FORECAST ENGINE', 'PROCUREMENT CENTER', 'EXECUTIVE DASHBOARD'.")
else:
    st.info("⬅️ Ανεβάστε το ολοκληρωμένο αρχείο Excel για να δείτε την ανάλυση ανά tab.")
