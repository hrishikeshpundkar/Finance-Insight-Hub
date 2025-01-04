import streamlit as st
import csv
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def add_transaction():
    try:
        # Define column layout
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='color: white;'>Add Transaction</h3>", unsafe_allow_html=True)
            amount = st.number_input("Amount", min_value=0.0)
            category = st.selectbox("Category", ["Income", "Expense"])
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Bank Transfer"])
            recurring = st.checkbox("Recurring Transaction")
        with col2:
            st.markdown("<h3 style='color: white;'>Transaction Details</h3>", unsafe_allow_html=True)
            date = st.date_input("Date")
            description = st.text_input("Description")
            notes = st.text_area("Notes")
            tags = st.text_input("Tags (comma separated)")

        # Get the user file from session state
        user_file = st.session_state.user_file
        st.write(f"User file before Submit: {user_file}")

        # Submit button logic
        if st.button("Submit"):
            st.write(f"User file at Submit: {user_file}")
            try:
                with open(user_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        date, 
                        description,
                        amount,
                        category,  
                        "Recurring" if recurring else "One-time", 
                        payment_method,
                        tags
                    ])
                st.success(f"Transaction added successfully to {user_file}!")
                # Display current CSV data
                with open(user_file, mode='r', encoding='utf-8') as file:
                    csv_data = list(csv.reader(file))
                    st.write("Current CSV Data:")
                    st.table(csv_data)
            except Exception as e:
                st.error(f"Error saving transaction to {user_file}: {str(e)}")
    except Exception as e:
        st.error(f"Error adding transaction: {str(e)}")

import streamlit as st
import pandas as pd
import csv
from io import BytesIO
from fpdf import FPDF
import plotly.express as px

def view_transaction():
    try:
        st.markdown("<h3 style='color: white;'>View Transactions</h3>", unsafe_allow_html=True)
        user_file = st.session_state.get("user_file", "user_transactions.csv")

        # Month mapping for the selectbox
        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4, 
            "May": 5, "June": 6, "July": 7, "August": 8, 
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        # Layout with two columns
        col1, col2 = st.columns([1, 2])

        with col1:
            selected_month = st.selectbox("Select Month", options=["All"] + list(month_mapping.keys()), key="month_select", label_visibility="collapsed")
            if st.button("View Transactions"):
                
            try:
                user_file = st.session_state.user_file
                with open(user_file, mode='r', encoding='utf-8') as file:
                    df = pd.read_csv(file)
                    if not df.empty:
                        # Split tags and explode them into separate rows
                        df['tags'] = df['tags'].fillna('')
                        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                        tags_df = df.assign(tags=df['tags'].str.split(',')).explode('tags')
                        tags_df['tags'] = tags_df['tags'].str.strip()

                        # Group by tags and sum the amounts
                        tag_amounts = tags_df.groupby('tags')['amount'].sum()
                        tag_amounts = tag_amounts[tag_amounts.index != '']
                        
                        # Display only the first pie chart (Transaction Amounts by Tags)
                        if not tag_amounts.empty:
                            st.write("Transaction Amounts by Tags")
                            fig1 = px.pie(tag_amounts, values=tag_amounts.values, names=tag_amounts.index, title="Transaction Amounts by Tags")
                            fig1.update_layout(width=800, height=900)  # Increased dimensions
                            st.plotly_chart(fig1)
                        else:
                            st.info("No tags found in transactions")

            except Exception as e:
                st.warning("No transaction data available for pie chart")
        with col2:
            if st.button("View Transactions"):
                try:
                    with open(user_file, mode='r', encoding='utf-8') as file:
                        csv_data = list(csv.reader(file))
                        if len(csv_data) <= 1:
                            st.warning("No transactions found!")
                            return

                        header = ["date", "description", "amount", "category", "type", "payment_method", "tags"]
                        data = csv_data[1:]

                        df = pd.DataFrame(data, columns=header)
                        df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.date

                        if selected_month != "All":
                            month_number = month_mapping[selected_month]
                            df = df[df["date"].apply(lambda x: x.month) == month_number]

                        st.table(df)

                        # Excel download (unchanged)
                        excel_buffer = BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        excel_buffer.seek(0)
                        st.download_button(
                            label="Download as Excel",
                            data=excel_buffer.getvalue(),
                            file_name=f"transactions_{selected_month}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Improved PDF formatting
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(190, 10, f"Transaction Report - {selected_month}", ln=True, align='C')
                        pdf.ln(10)

                        # Table header
                        pdf.set_font("Arial", "B", 10)
                        cols = ['Date', 'Description', 'Amount', 'Category', 'Payment Method']
                        # Create header row in PDF with thick borders
                        pdf.set_line_width(0.5)  # Set border thickness
                        col_widths = [25, 60, 35, 35, 35]  # Adjusted widths for remaining columns
                        for i, col in enumerate(cols):
                            pdf.cell(col_widths[i], 10, col, 1, 0, 'C')
                        pdf.ln()

                        # Table data
                        pdf.set_font("Arial", "", 10)
                        for _, row in df.iterrows():
                            pdf.cell(col_widths[0], 10, str(row['date']), 1, 0, 'C')
                            pdf.cell(col_widths[1], 10, str(row['description'])[:55], 1, 0, 'L')  # Increased description length
                            pdf.cell(col_widths[2], 10, str(row['amount']), 1, 0, 'R')  # Right-align amounts
                            pdf.cell(col_widths[3], 10, str(row['category']), 1, 0, 'C')
                            pdf.cell(col_widths[4], 10, str(row['payment_method']), 1, 1, 'C')
                        
                        pdf_buffer = BytesIO()
                        pdf_buffer.write(pdf.output(dest='S').encode('latin-1'))
                        pdf_buffer.seek(0)
                        st.download_button(
                            label="Download as PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"transactions_{selected_month}.pdf",
                            mime="application/pdf"
                        )

                except FileNotFoundError:
                    st.warning("No transactions found!")

    except Exception as e:
        st.error(f"Error viewing transactions: {str(e)}")
