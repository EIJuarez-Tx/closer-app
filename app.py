import streamlit as st
import pandas as pd
from datetime import date
from st_supabase_connection import SupabaseConnection

# 1. Initialize the Cloud Connection
# This looks for the URL and Key in your Streamlit Secrets automatically
conn = st.connection("supabase", type=SupabaseConnection)

st.set_page_config(page_title="The Closer's Command Center", layout="wide")
st.title("🏠 The Closer's Command Center")

# --- 2. Database Functions ---
def load_data():
    # Fetch all rows from the 'deals' table in Supabase
    # ttl="0" ensures we always get fresh data, not a cached version
    response = conn.query("*", table="deals", ttl="0").execute()
    return pd.DataFrame(response.data)

def save_data(prop, close_date, comm):
    # Insert a new row into the cloud database
    conn.table("deals").insert({
        "property": prop,
        "closing_date": str(close_date),
        "commission": comm
    }).execute()

def delete_data(deal_id):
    # Remove a specific deal by its unique ID
    conn.table("deals").delete().eq("id", deal_id).execute()

# --- 3. Main Dashboard Logic ---
df = load_data()

# Sidebar for Input
st.sidebar.header("Add New Transaction")
with st.sidebar.form("input_form", clear_on_submit=True):
    prop_name = st.text_input("Property Address")
    close_dt = st.date_input("Closing Date", value=date.today())
    comm_val = st.number_input("Commission ($)", min_value=0, value=5000)
    submitted = st.form_submit_button("Add to Dashboard")

if submitted and prop_name:
    save_data(prop_name, close_dt, comm_val)
    st.rerun()

# Display Dashboard
if not df.empty:
    # Calculations
    df['closing_date'] = pd.to_datetime(df['closing_date']).dt.date
    today = date.today()
    df['Days Left'] = df['closing_date'].apply(lambda x: (x - today).days)
    
    # Key Metrics at the top
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Deals", len(df))
    col2.metric("Total Pipeline", f"${df['commission'].sum():,.2f}")
    
    # Show count of urgent deals
    urgent_count = len(df[df['Days Left'] <= 7])
    col3.metric("Urgent (7 Days)", urgent_count)

    st.divider()
    st.subheader("Current Inventory")
    
    # Dynamic Table Rows
    for index, row in df.iterrows():
        cols = st.columns([3, 2, 2, 2, 1])
        cols[0].write(row['property'])
        cols[1].write(row['closing_date'])
        cols[2].write(f"${row['commission']:,.2f}")
        
        # Color logic for urgency
        days = row['Days Left']
        if days <= 7:
            cols[3].markdown(f":red[**{days} Days Left**]")
        else:
            cols[3].write(f"{days} Days Left")
        
        # Delete Button
        if cols[4].button("🗑️", key=f"del_{row['id']}"):
            delete_data(row['id'])
            st.rerun()
else:
    st.info("Your cloud database is currently empty. Add your first deal in the sidebar!")
