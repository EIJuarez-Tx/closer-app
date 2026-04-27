import streamlit as st
import pandas as pd
import os
from datetime import date

DATA_FILE = "deals.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Ensure date column is actual dates
        df['Closing Date'] = pd.to_datetime(df['Closing Date']).dt.date
        return df
    return pd.DataFrame(columns=["Property", "Closing Date", "Commission"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="The Closer's Command Center", layout="wide")
st.title("🏠 The Closer's Command Center")

df = load_data()

# --- Sidebar: Add New Deal ---
st.sidebar.header("Add New Transaction")
with st.sidebar.form("input_form", clear_on_submit=True):
    prop_name = st.text_input("Property Address")
    close_date = st.date_input("Closing Date", value=date.today())
    comm_val = st.number_input("Commission ($)", min_value=0, value=5000)
    submitted = st.form_submit_button("Add to Dashboard")

if submitted and prop_name:
    new_entry = pd.DataFrame([[prop_name, close_date, comm_val]], columns=["Property", "Closing Date", "Commission"])
    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)
    st.rerun()

# --- Dashboard Logic ---
if not df.empty:
    today = date.today()
    df['Days to Close'] = df['Closing Date'].apply(lambda x: (x - today).days)
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Deals", len(df))
    col2.metric("Total Pipeline", f"${df['Commission'].sum():,.2f}")
    
    # Urgent Deals count
    urgent = len(df[df['Days to Close'] <= 7])
    col3.metric("Urgent (7 Days)", urgent, delta_color="inverse")

    st.subheader("Current Inventory")
    
    # Add a Delete column
    for index, row in df.iterrows():
        cols = st.columns([3, 2, 2, 2, 1])
        cols[0].write(row['Property'])
        cols[1].write(row['Closing Date'])
        cols[2].write(f"${row['Commission']:,.2f}")
        
        # Color coding the countdown
        days = row['Days to Close']
        if days <= 7:
            cols[3].markdown(f":red[**{days} Days Left**]")
        else:
            cols[3].write(f"{days} Days Left")
            
        if cols[4].button("🗑️", key=f"del_{index}"):
            df = df.drop(index)
            save_data(df)
            st.rerun()

    st.markdown("---")
    # Export capability
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export to Excel (CSV)", data=csv, file_name="my_deals.csv", mime='text/csv')

else:
    st.info("Dashboard empty. Add a property in the sidebar to begin.")

st.markdown("---")
st.subheader("🤖 AI Document Assistant")
contract_text = st.text_area("Paste contract text here...", height=150)
if st.button("Generate AI Analysis Prompt"):
    st.code(f"Analyze this real estate contract. List the top 3 red flags, all critical repair deadlines, and any hidden fees:\n\n{contract_text}")