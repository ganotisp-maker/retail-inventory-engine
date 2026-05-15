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
# TITLE
# =====================================
st.title("📊 Retail Intelligence Dashboard")
st.markdown("### Integrated Business Monitoring System")

# =====================================
# HELPER FUNCTIONS
# =====================================
def clean_id(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    return s.replace('.', '') # Αφαιρούμε τελείες οριστικά

def clean_money_value(val):
    if pd.isna(val) or val == "": return 0.0
    s = str(val).replace("€", "").replace("\"", "").replace(" ", "").strip()
    s = s.replace(",", "")
    try: return float(s)
    except: return 0.0

# =====================================
# SIDEBAR - FILE UPLOADS
# =====================================
st.sidebar.header("📂 Upload Files")

toploss_file = st.sidebar.file_uploader("Upload TOP LOSS DASHBOARD (CSV)", type=["csv"], key="toploss")
broject_file = st.sidebar.file_uploader("Upload BROJECT (CSV)", type=["csv"], key="broject")
# Προσθήκη του νέου αρχείου Inventory (RAW DATA)
inventory_file = st.sidebar.file_uploader("Upload RAW DATA (Excel)", type=["xlsx"], key="inventory")

# =====================================
# NAVIGATION
# =====================================
menu = st.sidebar.radio("Navigate to:", ["Top Loss Analysis", "Inventory & Procurement"])

# =====================================
# SECTION 1: TOP LOSS ANALYSIS (Ο δικός σου κώδικας)
# =====================================
if menu == "Top Loss Analysis":
    if toploss_file and broject_file:
        try:
            top_df = pd.read_csv(toploss_file)
            broject_df = pd.read_csv(broject_file, skiprows=[0])
            
            # ... (εδώ μπαίνει όλη η δική σου λογική clean_id, KPIs, charts που ήδη έχεις) ...
            # Την κρατάμε ως έχει για να μην αλλάξει το functionality σου.
            st.success("Top Loss Data Loaded Successfully!")
            
            # [Εδώ συνεχίζει ο κώδικας που μου έστειλες για το Top Loss]
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.info("⬅️ Please upload Top Loss and Broject CSV files.")

# =====================================
# SECTION 2: INVENTORY & PROCUREMENT (Το νέο μας Project)
# =====================================
elif menu == "Inventory & Procurement":
    if inventory_file:
        try:
            # Διάβασμα του Excel Tab
            df_inv = pd.read_excel(inventory_file, sheet_name='RAW DATA')
            
            # Καθαρισμός Στηλών
            df_inv.columns = df_inv.columns.str.strip()
            df_inv['Product Code'] = df_inv['Product Code'].apply(clean_id)
            
            # Υπολογισμοί "On the Fly" (Order Suggestion & Values)
            # Χρήση clip(lower=0) για να μην έχουμε αρνητικά
            df_inv['Order Suggestion'] = (df_inv['Demand Forecast'] + df_inv['Safety Stock']) - df_inv['Current Stock']
            df_inv['Order Suggestion'] = df_inv['Order Suggestion'].clip(lower=0)
            
            df_inv['Stock Value'] = df_inv['Current Stock'] * df_inv['Product Price']
            df_inv['Order Value'] = df_inv['Order Suggestion'] * df_inv['Product Price']

            # Aggregation για το Executive Dashboard
            dashboard_df = df_inv.groupby('Category').agg({
                'Stock Value': 'sum',
                'Demand Forecast': 'sum',
                'Order Value': 'sum',
                'Product Price': 'mean'
            }).reset_index()

            # Υπολογισμός Turnover Ratio
            dashboard_df['Turnover Ratio'] = dashboard_df['Demand Forecast'] / (dashboard_df['Stock Value'] / dashboard_df['Product Price'])

            # Εμφάνιση KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Stock Value", f"{df_inv['Stock Value'].sum():,.0f} €".replace(",", "."))
            c2.metric("Procurement Need", f"{df_inv['Order Value'].sum():,.0f} €".replace(",", "."))
            c3.metric("Avg Turnover Ratio", f"{dashboard_df['Turnover Ratio'].mean():.2f}")

            st.divider()

            # Πίνακας Dashboard
            st.subheader("Category Performance & Procurement Needs")
            st.dataframe(dashboard_df.style.format({
                'Stock Value': '{:,.2f} €',
                'Order Value': '{:,.2f} €',
                'Turnover Ratio': '{:.2f}'
            }), use_container_width=True)

            # Chart: Turnover Ratio
            fig_turn = px.bar(dashboard_df, x='Category', y='Turnover Ratio', 
                              title="Turnover Ratio per Category", color='Turnover Ratio',
                              color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_turn, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error processing Inventory file: {e}")
    else:
        st.info("⬅️ Please upload the RAW DATA Excel file to see Inventory analysis.")
