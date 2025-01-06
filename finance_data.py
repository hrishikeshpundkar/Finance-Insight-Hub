import plotly as py
import streamlit as st
from utils import add_transaction, view_transaction, summary,budget,portfolio
def moneymanager():
    st.markdown("---")
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Add Transaction", "View Transactions", "Summary", 
         "Budget","Portfolio","Add Bank Statement", "Help & support"]
    )
    if menu == "Add Transaction":
        add_transaction()
    elif menu == "View Transactions":
        st.markdown("<h3 style='color: white;'>Transaction History</h3>", unsafe_allow_html=True)
        view_transaction()
    elif menu == "Summary":
         summary()
    elif menu == "Budget":
        budget()
    elif menu == "Portfolio":
        portfolio()
    elif menu == "Add Bank Statement":
        addbankstatement()
    elif menu == "Help & support":
        st.markdown("Contact Us\nFashnear Technologies Private Limited,\nCIN: U74900KA2015PTC082263rd \nFloor, Wing-E, Helios Business Park,Kadubeesanahalli Village,\n Varthur Hobli, Outer Ring Road Bellandur,\n Bangalore, Bangalore South,\n Karnataka, India,\n 560103E-\nmail address: query@meesho.com© \n2015-2025 Meesho.com ")