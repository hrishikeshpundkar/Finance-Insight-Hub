import plotly as py
import streamlit as st
from utils import add_transaction, view_transaction, summary
def moneymanager():
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
         summary()

    elif menu == "Portfolio":
        st.markdown("<h3 style='color: white;'>Investment Portfolio</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Holdings", "Performance"])
        with tab1:
            st.write("Your holdings here")
        with tab2:
            st.write("Performance metrics here")