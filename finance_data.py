import plotly as py
import streamlit as st
from utils import add_transaction, view_transaction
def moneymanager():
    # Main title
    st.markdown("<h2 style='text-align: center; color: white;'>Money Manager</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Track your expenses and income</h3>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Add Transaction", "View Transactions", "Summary", "Insights", 
         "Budget", "Goals", "Reports", "Portfolio"]
    )
    if menu == "Add Transaction":
        add_transaction()
    elif menu == "View Transactions":
        st.markdown("<h3 style='color: white;'>Transaction History</h3>", unsafe_allow_html=True)
        view_transaction()
    elif menu == "Summary":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Income", value="$0")
        with col2:
            st.metric(label="Total Expenses", value="$0")
        with col3:
            st.metric(label="Balance", value="$0")

    elif menu == "Portfolio":
        st.markdown("<h3 style='color: white;'>Investment Portfolio</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Holdings", "Performance"])
        with tab1:
            st.write("Your holdings here")
        with tab2:
            st.write("Performance metrics here")