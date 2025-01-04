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
import pandas as pd
import plotly.express as px
import pandas as pd
import plotly.express as px
import csv
from io import BytesIO
import streamlit as st
from fpdf import FPDF

import pandas as pd
import plotly.express as px
import csv
from io import BytesIO
import streamlit as st
from fpdf import FPDF

def view_transaction():
    try:
        st.markdown("<h3 style='color: white;'>View Transactions</h3>", unsafe_allow_html=True)
        user_file = st.session_state.get("user_file", "user_transactions.csv")

        # Tag mapping to group similar tags into broader categories, including slight spelling variations
        tag_mapping = {
    "monthly salary": "Income",
    "rental income": "Income",
    "interest income": "Income",
    "dividend income": "Income",
    "bonus": "Income",
    "refund": "Income",
    "award": "Income",
    "gift": "Income",
    "investment": "Investment",
    "savings": "Investment",
    "stocks": "Investment",
    "bonds": "Investment",
    "mutual funds": "Investment",
    "crypto": "Investment",
    "cashback": "Income",
    "groceries": "Food & Dining",
    
    "streaming": "Entertainment",
    "netflix subscription": "Streaming",
    "amazon order": "Shopping",
    "movie tickets": "Entertainment",
    "fitness": "Health",
    "yoga classes": "Health",
    "food": "Food & Dining",
    "groceries purchase": "Food",
    "cinema": "Entertainment",
    "fuel": "Bills",
    "supermarket": "Shopping",
    "friends": "Transfer",
    "snacks and beverages": "Food",
    "petrol": "Bills",
    "car emi": "Loans",
    "electricity bill": "Bills",
    "home rent": "Housing",
    "stock dividends": "Investment",
    "interest from fd": "Investment",
    "freelance project": "Income",
    "salary": "Income",
    "gift from friend": "Income",
    "charity donation": "Charity",
    "book purchase": "Education",
    "mobile recharge": "Bills",
    "app development payment": "Income",
    "dinner at restaurant": "Food",
    "tea break": "Food",
    "study": "Education",
    
    # Indian-specific additional tags
    "diwali shopping": "Shopping",  # Specific to the Diwali shopping spree
    "wedding expenses": "Expenses",  # Common for weddings in India
    "hdfc bank": "Banking",  # Common Indian bank
    "icici bank": "Banking",  # Common Indian bank
    "savings deposit": "Investment",  # Related to savings in Indian banks
    "mutual fund investment": "Investment",  # Common in India for long-term savings
    "gold purchase": "Shopping",  # Popular in India for investment and gifting
    "insurance premium": "Bills",  # Insurance-related payments
    "school fees": "Education",  # Common expense for children in India
    "medicine purchase": "Health",  # Common in healthcare expenses
    "mobile data recharge": "Bills",  # Mobile data recharge is a common expense
    "pension contribution": "Investment",  # Pension schemes in India
    "tax payment": "Bills",  # Indian tax payments
    "travel": "Travel",  # For expenses related to trips (could be domestic or international)
    "hotel stay": "Travel",  # Accommodation expenses for domestic or international travel
    "train tickets": "Travel",  # Travel-related expenses in India
    "flight tickets": "Travel",  # Flight bookings for travel
    "local transport": "Transport",  # Expenses for public or private transport (e.g., Ola, Uber)
    "auto rickshaw": "Transport",  # Specific to transportation in India
    "cab fare": "Transport",  # Uber, Ola, or other cab fares in India
    "gift": "Gift",  # Gifts for various occasions (could be for festivals or birthdays)
    "pukka meal": "Food & Dining",  # A term used for meals from popular restaurants or dhabas
    "temple donation": "Charity",  # Donations for religious purposes
    "pooja expenses": "Charity",  # Common expenses for religious rituals
    "aadhar card": "Documents",  # For Aadhar card-related services and updates
    "passport fees": "Documents",  # Passport-related services
    "domestic help": "Housing",  # Payments for maids, cooks, or other domestic help
    "rent": "Housing",  # Rent for accommodation in India
    "landline bill": "Bills",  # Landline telephone bills, though decreasing in use
    "internet bill": "Bills",  # For broadband internet bills
    "grocery shopping": "Food & Dining",  # Regular grocery purchases
    "vegetable purchase": "Food & Dining",  # Specific to buying vegetables in India
    "fruits purchase": "Food & Dining",  # Specific to buying fruits in India
    "construction materials": "Housing",  # For home improvement or construction
    "repair costs": "Housing",  # For home repairs and maintenance
    "furniture purchase": "Shopping",  # Furniture-related expenses for the home
    "mobile phone purchase": "Shopping",  # For buying phones in India
}


        # Month mapping to convert month names to month numbers
        month_mapping = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12
        }

        # Layout with two columns
        col1, col2 = st.columns([1, 2])

        with col1:
            selected_month = st.selectbox("Select Month", options=["All"] + list(month_mapping.keys()), key="month_select", label_visibility="collapsed")
            
            # Read the CSV data for pie chart
            try:
                user_file = st.session_state.user_file

                with open(user_file, mode='r', encoding='utf-8') as file:
                    df = pd.read_csv(file)
                    if not df.empty:
                        # Split tags and explode them into separate rows
                        df['tags'] = df['tags'].fillna('')
                        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                        tags_df = df.assign(tags=df['tags'].str.split(',')).explode('tags')
                        tags_df['tags'] = tags_df['tags'].str.strip().str.lower()  # Convert to lowercase

                        # Map the tags to broader categories, matching with predefined tag_mapping
                        tags_df['category'] = tags_df['tags'].apply(lambda tag: tag_mapping.get(tag, tag))

                        # Group by the new categories and sum the amounts
                        category_amounts = tags_df.groupby('category')['amount'].sum()

                        # Display the pie chart for transaction amounts by category
                        if not category_amounts.empty:
                            st.write("Transaction Amounts by Category")
                            fig1 = px.pie(category_amounts, values=category_amounts.values, names=category_amounts.index, title="Transaction Amounts by Category")
                            fig1.update_layout(width=800, height=900)  # Increased dimensions
                            st.plotly_chart(fig1)
                        else:
                            st.info("No categories found in transactions")

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

