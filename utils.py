import streamlit as st
import csv
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import plotly.express as px
def add_transaction():
    try:
        try:
            tag_mapping_df = pd.read_csv("tag_mapping.csv")
            tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        except Exception as e:
            st.error("Failed to load tag mapping from CSV.")
            return

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='color: white;'>Add Transaction</h3>", unsafe_allow_html=True)
            amount = st.number_input("Amount", min_value=0.0)
            category = st.selectbox("Category", ["Income", "Expense"])
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Bank Transfer"])
        with col2:
            st.markdown("<h3 style='color: white;'>Transaction Details</h3>", unsafe_allow_html=True)
            date = st.date_input("Date")
            description = st.text_input("Description")
            tags = st.text_input("Tags (comma separated)")
        type = 'Uncategorized' if not pd.notna(tags) or tags.strip() == '' else tag_mapping.get(str(tags).strip().lower(), 'Uncategorized')
        user_file = st.session_state.user_file
        if st.button("Submit"):
            try:
                with open(user_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        date, 
                        description,
                        amount,
                        category,  
                        type, 
                        payment_method,
                        tags
                    ])
                st.success("Transaction added")
            except Exception as e:
                st.error(f"Error saving transaction to {user_file}: {str(e)}")
    except Exception as e:
        st.error(f"Error adding transaction: {str(e)}")
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
        
        try:
            df = pd.read_csv(user_file)
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            years = sorted(df['year'].unique())
            selected_year = st.selectbox("Select Year", years, index=len(years)-1)
        except Exception as e:
            st.error("Failed to load transactions from CSV.")
            return

        if st.button("View Transactions"):
            try:
                df = df[df['year'] == selected_year]
                if selected_month != "All":
                    month_number = month_mapping[selected_month]
                    df = df[df["date"].dt.month == month_number]

                if not df.empty:
                    df["date"] = df["date"].dt.date

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
                                    title=f"Transaction Amounts by Category - {selected_month} {selected_year}")
                        fig1.update_layout(
                            width=1100, height=700,
                            font=dict(size=18),
                            title_font_size=18,
                            legend_font_size=14
                        )
                        st.plotly_chart(fig1)
                    else:
                        st.info("No categories found for the selected month and year")

                    df = df.rename(columns={'amount': 'amount (INR)'})
                    df['amount (INR)'] = pd.to_numeric(df['amount (INR)'], errors='coerce').fillna(0).astype(int)
                    st.table(df)
                    excel_buffer = BytesIO()
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        label="Download as Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"transactions_{selected_month}_{selected_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(190, 10, f"Transaction Report - {selected_month} {selected_year}", ln=True, align='C')
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
                        file_name=f"transactions_{selected_month}_{selected_year}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("No transactions found for the selected month and year!")
            except FileNotFoundError:
                st.warning("No transactions found!")

    except Exception as e:
        st.error(f"Error viewing transactions: {str(e)}")


def format_amount(amount):
    """Formats the amount in Indian numbering style."""
    return '₹{:,.0f}'.format(amount).replace(',', 'X').replace('X', ',', 1) 

import streamlit as st
import pandas as pd
import plotly.express as px

def summary():
    st.markdown("<h3 style='color: white;'>Summary</h3>", unsafe_allow_html=True)
    user_file = st.session_state.get('user_file')
    
    if not user_file:
        st.warning("No file uploaded.")
        return
    
    try:
        df = pd.read_csv(user_file)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.strftime('%B')
        df['year'] = df['date'].dt.year
        years = sorted(df['year'].unique())
        if not years:
            st.warning("No data available")
            return
        selected_year = st.selectbox("Select Year", years, index=len(years)-1)
        yearly_df = df[df['year'] == selected_year]
        monthly_totals = yearly_df.groupby('month')['amount'].sum().reindex([
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]).fillna(0)
        formatted_amounts = monthly_totals.apply(format_amount)
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
        try:
            tag_mapping_df = pd.read_csv("tag_mapping.csv")
            tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        except Exception as e:
            st.error("Failed to load tag mapping from CSV.")
            return
        try: 
    
            st.subheader("Spending by Tags")
            tags_df = yearly_df.assign(tags=yearly_df['tags'].str.split(',')).explode('tags')
            tags_df['tags'] = tags_df['tags'].str.strip().str.lower()
            
            # Map tags to categories using tag_mapping
            tags_df['category'] = tags_df['tags'].map(tag_mapping).fillna('Uncategorized')
            
            # Group by category instead of tags
            category_totals = tags_df.groupby('category')['amount'].sum()
            
            tag_df = pd.DataFrame({
                'Category': category_totals.index,
                'Amount (₹)': category_totals.values
            })
            tag_df['Amount (₹)'] = tag_df['Amount (₹)'].apply(lambda x: f"₹{x:,.2f}")
            st.table(tag_df)
            
            total_amount = yearly_df['amount'].sum()
            st.write(f"Total amount spent in {selected_year}: ₹{total_amount:,.2f}")
        except Exception as e:
            st.error(f"Error processing tags: {str(e)}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
def budget():
    st.markdown("<h3 style='color: white;'>Budget</h3>", unsafe_allow_html=True)
    user_file = st.session_state.get('user_file')
    
    if not user_file:
        st.warning("No file uploaded.")
        return
    
    try:
        # Generate budget file name based on user file
        budget_file = user_file.replace('.csv', '_budget.csv')
        df = pd.read_csv(user_file)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.strftime('%B')
        df['year'] = df['date'].dt.year
        df['tags'] = df['tags'].str.split(',')
        
        tag_mapping_df = pd.read_csv("tag_mapping.csv")
        tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        
        current_month = pd.to_datetime('today').strftime('%B')
        current_year = pd.to_datetime('today').year
        
        # Load existing budget if available
        try:
            budget_df = pd.read_csv(budget_file)
            existing_budgets = dict(zip(budget_df['Category'], budget_df['Budget']))
        except FileNotFoundError:
            existing_budgets = {}
            
        # Filter for current month and year
        current_df = df[(df['month'] == current_month) & (df['year'] == current_year)]
        current_df = current_df.explode('tags')
        current_df['tags'] = current_df['tags'].str.strip().str.lower()
        current_df['category'] = current_df['tags'].map(tag_mapping).fillna('Uncategorized')
        
        # Budget settings
        st.write("### Set Budget")
        budget_settings = {}
        for category in current_df['category'].unique():
            default_value = existing_budgets.get(category, 0.0)
            budget_settings[category] = st.number_input(
                f"Budget for {category}",
                min_value=0.0,
                value=float(default_value),
                step=100.0
            )
            
        if st.button("Save Budget"):
            budget_data = pd.DataFrame({
                'Category': list(budget_settings.keys()),
                'Budget': list(budget_settings.values())
            })
            budget_data.to_csv(budget_file, index=False)
            st.success("Budget saved successfully!")
            
        st.write("### Budget Overview")
        category_totals = current_df.groupby('category')['amount'].sum()
        budget_overview = pd.DataFrame({
            'Category': category_totals.index,
            'Spent': category_totals.values,
            'Budget': [budget_settings[category] for category in category_totals.index],
        })
        budget_overview['Remaining'] = budget_overview['Budget'] - budget_overview['Spent']
        
        # Display budget table
        st.table(budget_overview.round(2))
        
        # Create columns for pie charts (2 columns, showing up to 10 categories)
        categories = list(budget_overview.index)
        num_categories = len(categories)
        charts_per_row = 2
        # Get all tags for each category
        tag_by_category = {}
        for category in categories:
            category_tags = current_df[current_df['category'] == category]['tags'].unique()
            tag_by_category[category] = ', '.join(filter(None, category_tags))

        for i in range(0, min(10, num_categories), charts_per_row):
            cols = st.columns(charts_per_row)
            for j in range(charts_per_row):
                    if i + j < min(10, num_categories):
                        category = categories[i + j]
                        with cols[j]:
                            # Create pie chart for each category
                            data = pd.DataFrame({
                                'Type': ['Spent', 'Remaining'],
                                'Amount': [
                                    budget_overview.loc[category, 'Spent'],
                                    max(0, budget_overview.loc[category, 'Remaining'])
                                ]
                            })
                            fig = px.pie(
                                data,
                                values='Amount',
                                names='Type',
                                title=f"{category} Budget Usage<br><sub>Tags: {tag_by_category[category]}</sub>"
                            )
                            fig.update_layout(
                                width=400,
                                height=400,
                                showlegend=True,
                                title_font_size=14
                            )
                            st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"Error processing budget: {str(e)}")