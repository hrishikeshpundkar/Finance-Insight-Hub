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

import pandas as pd
import csv
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import streamlit as st
import pandas as pd
import csv
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import streamlit as st

# Function to view transactions
def view_transaction():
    try:
        st.markdown("<h3 style='color: white;'>View Transactions</h3>", unsafe_allow_html=True)
        user_file = st.session_state.get("user_file", "user_transactions.csv")

        try:
            tag_mapping_df = pd.read_csv("tag_mapping.csv")
            tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        except Exception as e:
            st.error("Failed to load tag mapping from CSV.")
            return

        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        selected_month = st.selectbox("Select Month", options=["All"] + list(month_mapping.keys()))
        
        if st.button("View Transactions"):
            try:
                with open(user_file, mode='r', encoding='utf-8') as file:
                    df = pd.read_csv(file)
                    if not df.empty:
                        # Convert date column and filter by month first
                        df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.date
                        if selected_month != "All":
                            month_number = month_mapping[selected_month]
                            df = df[df["date"].apply(lambda x: x.month) == month_number]

                        # Process tags for pie chart
                        df['tags'] = df['tags'].fillna('')
                        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                        tags_df = df.assign(tags=df['tags'].str.split(',')).explode('tags')
                        tags_df['tags'] = tags_df['tags'].str.strip()

                        case_insensitive_mapping = {k.lower(): v for k, v in tag_mapping.items()}
                        tags_df['category'] = tags_df['tags'].apply(lambda tag: 
                            case_insensitive_mapping.get(str(tag).strip().lower(), 'Uncategorized') 
                            if pd.notna(tag) and tag.strip() != '' else 'Uncategorized')

                        category_amounts = tags_df.groupby('category')['amount'].sum()

                        if not category_amounts.empty:
                            fig1 = px.pie(category_amounts, values=category_amounts.values, 
                                        names=category_amounts.index, 
                                        title=f"Transaction Amounts by Category - {selected_month}")
                            fig1.update_layout(
                                width=1200, height=800,
                                font=dict(size=18),
                                title_font_size=18,
                                legend_font_size=14
                            )
                            st.plotly_chart(fig1)
                        else:
                            st.info("No categories found for the selected month")

                        df = df.rename(columns={'amount': 'amount (INR)'})
                        df['amount (INR)'] = pd.to_numeric(df['amount (INR)'], errors='coerce').fillna(0).astype(int)
                        st.table(df)
                        excel_buffer = BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        excel_buffer.seek(0)
                        st.download_button(
                            label="Download as Excel",
                            data=excel_buffer.getvalue(),
                            file_name=f"transactions_{selected_month}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(190, 10, f"Transaction Report - {selected_month}", ln=True, align='C')
                        pdf.ln(10)

                        pdf.set_font("Arial", "B", 10)
                        cols = ['Date', 'Description','amount (INR)', 'Category', 'Payment Method']
                        pdf.set_line_width(0.5)
                        col_widths = [25, 60, 35, 35, 35]
                        for i, col in enumerate(cols):
                            pdf.cell(col_widths[i], 10, col, 1, 0, 'C')
                        pdf.ln()

                        pdf.set_font("Arial", "", 10)
                        for _, row in df.iterrows():
                            pdf.cell(col_widths[0], 10, str(row['date']), 1, 0, 'C')
                            pdf.cell(col_widths[1], 10, str(row['description'])[:55], 1, 0, 'L')
                            pdf.cell(col_widths[2], 10, str(row['amount (INR)']), 1, 0, 'R')
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

import pandas as pd
import plotly.express as px
import streamlit as st

def format_amount(amount):
    """Formats the amount in Indian numbering style."""
    return '₹{:,.0f}'.format(amount).replace(',', 'X').replace('X', ',', 1)  # Adds commas for Indian numbering
def summary():
        st.markdown("<h3 style='color: white;'>Summary</h3>", unsafe_allow_html=True)
        user_file = st.session_state.user_file 
        
        try:
            df = pd.read_csv(user_file)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.strftime('%B')
            df['year'] = df['date'].dt.year
            
            # Get unique years for selection
            years = sorted(df['year'].unique())
            if not years:
                st.warning("No data available")
                return
                
            # Add year selection widget
            selected_year = st.selectbox("Select Year", years, index=len(years)-1)
            
            # Filter data for selected year
            yearly_df = df[df['year'] == selected_year]
            
            # Calculate monthly totals for selected year
            monthly_totals = yearly_df.groupby('month')['amount'].sum().reindex([
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]).fillna(0)

            # Format the amounts in Indian style
            formatted_amounts = monthly_totals.apply(format_amount)

            # Create a bar chart
            plot_df = pd.DataFrame({
                'Month': monthly_totals.index,
                'Amount': monthly_totals.values
            })
            fig = px.bar(
                plot_df,
                x='Month',
                y='Amount',
                title=f'Monthly Transactions - {selected_year}',
                labels={'Month': 'Month', 'Amount': 'Total Amount'}
            )
            
            # Add line trace for distribution
            fig.add_scatter(
                x=plot_df['Month'],
                y=plot_df['Amount'],
                mode='lines',
                name='Trend',
                line=dict(color='rgb(255, 165, 0)', width=3),
                hovertemplate='%{y:,.0f}<extra></extra>'
            )
            
            # Enhance the bar chart appearance
            fig.update_traces(
                selector=dict(type='bar'),
                marker_color='rgb(158,202,225)',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5,
                opacity=0.8,
                width=0.8,
                hovertemplate='<span style="font-size: 20px">%{x}: %{customdata[0]}</span><extra></extra>',
                customdata=[[formatted_amounts[i]] for i in range(len(formatted_amounts))]
            )
            
            fig.update_layout(
                width=1200,
                height=600,
                font=dict(size=18),
                title_font_size=32,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    showline=True,
                    linecolor='rgb(204, 204, 204)',
                    linewidth=1.5,
                    tickfont=dict(size=20)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgb(204, 204, 204)',
                    showline=True,
                    linecolor='rgb(204, 204, 204)',
                    linewidth=1.5,
                    tickfont=dict(size=20)
                )
            )
            
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
