
import streamlit as st
import pandas as pd
from datetime import datetime
import os

FILE_PATH = "orders.csv"
STATUS_OPTIONS = ["Pending", "Order Placed", "Sent for Fitting", "Ready", "Delivered"]
SALESPERSONS = ["Sukrit", "Tanya", "Ajit", "Param", "Parveen", "Sonu"]

# Initialize CSV if not exists
if not os.path.exists(FILE_PATH):
    df = pd.DataFrame(columns=["Mobile", "Name", "Date", "Details", "Status", "Salesperson"])
    df.to_csv(FILE_PATH, index=False)

# Load data
def load_data():
    return pd.read_csv(FILE_PATH)

# Save data
def save_data(df):
    df.to_csv(FILE_PATH, index=False)

# Main Navigation
st.title("Beauty Optics - Order Management System")

menu = st.sidebar.radio("Menu", [" Home", " New Order", " Search Order", " Pending Orders"," Mark Ready"," Ready Orders"])

# Home
if menu == " Home":
    st.subheader("Welcome to Beauty Optics Order System")
    st.write("Use the menu on the left to navigate:")
    st.markdown("""
    -  **New Order** to add a customer order  
    -  **Search Order** to find/update an order  
    -  **Pending Orders** to view all pending items  
    """)

# New Order
elif menu == " New Order":
    st.subheader("Enter New Order Details")

    with st.form("order_form"):
        mobile = st.text_input("Mobile Number")
        name = st.text_input("Customer Name")
        date = st.date_input("Date", value=datetime.today())
        details = st.text_area("Order Details")
        status = st.selectbox("Status", STATUS_OPTIONS)
        salesperson = st.selectbox("Salesperson", SALESPERSONS)
        submitted = st.form_submit_button("Submit Order")

        if submitted:
            if not mobile or not name or not details:
                st.error("Please fill all required fields.")
            else:
                new_row = {
                    "Mobile": mobile,
                    "Name": name,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Details": details,
                    "Status": status,
                    "Salesperson": salesperson
                }
                df = load_data()
                df = df._append(new_row, ignore_index=True)
                save_data(df)
                st.success("Order added successfully!")

# Search Order
# ----------------- Search Order -----------------
elif menu == " Search Order":
    st.subheader("Search and Update Order Status")
    df = load_data()

    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    search_by = st.radio("Search by", ["Customer Name", "Mobile Number", "Date"])

    # Search value depending on type
    if search_by in ["Customer Name", "Mobile Number"]:
        search_value = st.text_input(f"Enter {search_by}")

    if search_by == "Date":
        search_date = st.date_input("Select Date")

    if st.button("Search"):
        if search_by == "Customer Name":
            results = df[df['Name'].str.contains(search_value, case=False, na=False)]
        elif search_by == "Mobile Number":
            results = df[df['Mobile'].astype(str).str.contains(search_value, na=False)]
        elif search_by == "Date":
            search_date_str = search_date.strftime("%Y-%m-%d")
            results = df[df['Date'] == search_date_str]
        else:
            results = pd.DataFrame()  # fallback empty

        if results.empty:
            st.warning("No matching orders found.")
            st.session_state.search_results = None
        else:
            st.session_state.search_results = results

    if st.session_state.search_results is not None:
        results = st.session_state.search_results
        for i in results.index:
            row = df.loc[i]
            st.markdown("---")
            st.write(f"**Name**: {row['Name']}")
            st.write(f"**Mobile**: {row['Mobile']}")
            st.write(f"**Date**: {row['Date']}")
            st.write(f"**Details**: {row['Details']}")
            st.write(f"**Current Status**: {row['Status']}")

            # track dropdown status in session_state
            dropdown_key = f"dropdown_status_{i}"
            if dropdown_key not in st.session_state:
                st.session_state[dropdown_key] = row['Status']

            st.selectbox(
                "Update Status",
                STATUS_OPTIONS,
                key=dropdown_key
            )

            if st.button(f"Update Order #{i}", key=f"update_button_{i}"):
                selected_status = st.session_state[dropdown_key]
                df.at[i, "Status"] = selected_status
                save_data(df)
                st.success(f"Order #{i} updated to '{selected_status}' ")
                # refresh session search results
                st.session_state.search_results = df[df.index.isin(results.index)]



                    

# Pending Orders
elif menu == " Pending Orders":
    st.subheader("All Pending Orders")
    df = load_data()
    pending_df = df[df["Status"] == "Pending"]

    if pending_df.empty:
        st.info("No pending orders.")
    else:
        for i in pending_df.index:
            row = df.loc[i]
            st.markdown("---")
            st.write(f"**Name**: {row['Name']} | **Mobile**: {row['Mobile']}")
            st.write(f"**Date**: {row['Date']} | **Salesperson**: {row['Salesperson']}")
            st.write(f"**Details**: {row['Details']}")
            st.write(f"**Current Status**: {row['Status']}")

            # Add button to update status to 'Order Placed'
            if st.button(f"Mark as Order Placed", key=f"place_button_{i}"):
                df.at[i, "Status"] = "Order Placed"
                save_data(df)
                st.success(f"Status for {row['Name']} updated to 'Order Placed'")




# ----------------- Mark Ready -----------------
elif menu == " Mark Ready":
    st.subheader("Mark Orders as Ready")
    df = load_data()
    ready_df = df[df["Status"].isin(["Order Placed", "Sent for Fitting"])]

    if ready_df.empty:
        st.info("No orders in 'Order Placed' or 'Sent for Fitting' status.")
    else:
        for i in ready_df.index:
            row = df.loc[i]
            st.markdown("---")
            st.write(f"**Name**: {row['Name']} | **Mobile**: {row['Mobile']}")
            st.write(f"**Date**: {row['Date']} | **Salesperson**: {row['Salesperson']}")
            st.write(f"**Details**: {row['Details']}")
            st.write(f"**Current Status**: {row['Status']}")

            # Button to mark as Ready
            if st.button("Mark as Ready", key=f"ready_button_{i}"):
                df.at[i, "Status"] = "Ready"
                save_data(df)
                st.success(f"Status for {row['Name']} updated to 'Ready'")




# ----------------- Ready Orders -----------------
elif menu == " Ready Orders":
    st.subheader("Ready Orders - Mark as Delivered")
    df = load_data()
    ready_df = df[df["Status"] == "Ready"]

    if ready_df.empty:
        st.info("No orders marked as 'Ready'.")
    else:
        for i in ready_df.index:
            row = df.loc[i]
            st.markdown("---")
            st.write(f"**Name**: {row['Name']} | **Mobile**: {row['Mobile']}")
            st.write(f"**Date**: {row['Date']} | **Salesperson**: {row['Salesperson']}")
            st.write(f"**Details**: {row['Details']}")
            st.write(f"**Current Status**: {row['Status']}")

            if st.button("Mark as Delivered", key=f"deliver_button_{i}"):
                df.at[i, "Status"] = "Delivered"
                save_data(df)
                st.success(f"Status for {row['Name']} updated to 'Delivered'")


