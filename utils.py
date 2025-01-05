import streamlit as st
import csv
import pandas as pd
import time
from fpdf import FPDF
from io import BytesIO
import plotly.express as px
import csv
import os
import pandas as pd
import streamlit as st
import os
import pandas as pd
import streamlit as st

def check_and_initialize_user_data():
    """Ensure the user's data directory and file exist."""
    username = st.session_state.get("login_username", "")
    if not username:
        st.error("User not logged in!")
        return False

    user_directory = os.path.join("data", username)
    user_file = os.path.join(user_directory, f"{username}_data.csv")

    # Create user directory if it doesn't exist
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    # Create user data file if it doesn't exist
    if not os.path.exists(user_file):
        with open(user_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write headers for the transaction data
            writer.writerow(['date', 'description', 'amount', 'category', 'transaction_type', 'payment_method', 'tags'])
        st.info(f"Data file created for {username}. Start by adding your first transaction.")
    
    return user_file


def add_transaction():
    try:
        # Load tag mapping file
        try:
            tag_mapping_df = pd.read_csv("data/tag_mapping.csv")
            tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        except Exception as e:
            st.error("Failed to load tag mapping from CSV.")
            return
        user_file = check_and_initialize_user_data()
        username = st.session_state.get("login_username", "")
        if not username:
            st.error("User not logged in!")
            return
        if not os.path.exists(user_file):
            st.error(f"User data file not found: {user_file}. Please ensure the file exists.")
            return

        # Input fields for transaction details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='color: white;'>Add Transaction</h3>", unsafe_allow_html=True)
            amount_str = st.text_input("Amount")
            category = st.selectbox("Category", ["Income", "Expense"])
            payment_method = st.selectbox("Payment Method", ["Cash","UPI","Credit Card", "Debit Card", "Bank Transfer"])
        with col2:
            st.markdown("<h3 style='color: white;'>Transaction Details</h3>", unsafe_allow_html=True)
            date = st.date_input("Date")
            description = st.text_input("Description")
            tag_options = ["Type your own tag"] + list(tag_mapping_df['tag'].unique())
            tag_selection = st.selectbox("Select or Type Tag", tag_options)
            if tag_selection == "Type your own tag":
                tags = st.text_input("Enter custom tag") 
            else:
                tags = tag_selection
        try:
            amount = int(amount_str) if amount_str     else None
        except ValueError:
            st.error("Amount must be a valid Number")
            amount = None
        transaction_type = (
            'Uncategorized'
            if not pd.notna(tags) or tags.strip() == ''
            else tag_mapping.get(tags.strip().lower(), 'Uncategorized')
        )
        if st.button("Submit"):
            if not all([amount, date, description, category, payment_method]):
                st.error("Please fill in all fields")
            else:
                try:
                    # Append the transaction to the user's file
                    with open(user_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([
                            date, 
                            description,
                            amount,
                            category,
                            transaction_type,
                            payment_method,
                            tags
                        ])
                    st.success("Transaction added successfully!")
                except Exception as e:
                 st.error(f"Error saving transaction to {user_file}: {str(e)}")
    except Exception as e:
        st.error(f"Error adding transaction: {str(e)}")

def view_transaction():
    try:
        st.markdown("<h3 style='color: white;'>View Transactions</h3>", unsafe_allow_html=True)
        username = st.session_state.get("login_username", "")
        if not username:
            st.error("User not logged in!")
            return
        user_file = os.path.join("data", username, f"{username}_data.csv")
        tag_mapping_file = os.path.join("data", "tag_mapping.csv")
        try:
            tag_mapping_df = pd.read_csv(tag_mapping_file)
            tag_mapping = pd.Series(
                tag_mapping_df['category'].values,
                index=tag_mapping_df['tag'].str.lower()
            ).to_dict()
        except FileNotFoundError:
            st.error(f"Tag mapping file '{tag_mapping_file}' not found!")
            return
        except Exception as e:
            st.error(f"Error loading tag mapping: {str(e)}")
            return
        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        selected_month = st.selectbox("Select Month", options=["All"] + list(month_mapping.keys()))
        try:
            df = pd.read_csv(user_file)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['year'] = df['date'].dt.year
        except FileNotFoundError:
            st.error(f"User transaction file '{user_file}' not found!")
            return
        except Exception as e:
            st.error(f"Error loading transactions: {str(e)}")
            return
        years = sorted(df['year'].dropna().unique())
        selected_year = st.selectbox("Select Year", years, index=len(years) - 1)
        if st.button("View Transactions"):
            try:
                filtered_df = df[df['year'] == selected_year]
                if selected_month != "All":
                    month_number = month_mapping[selected_month]
                    filtered_df = filtered_df[filtered_df["date"].dt.month == month_number]
                if not filtered_df.empty:
                    filtered_df["date"] = filtered_df["date"].dt.date
                    filtered_df['tags'] = filtered_df['tags'].fillna('')
                    filtered_df['amount'] = pd.to_numeric(filtered_df['amount'], errors='coerce')              
                    tags_df = filtered_df.assign(tags=filtered_df['tags'].str.split(',')).explode('tags')
                    tags_df['tags'] = tags_df['tags'].str.strip()
                    tags_df['category'] = tags_df['tags'].apply(
                        lambda tag: tag_mapping.get(tag.lower(), 'Uncategorized') if pd.notna(tag) else 'Uncategorized'
                    )                  
                    category_amounts = tags_df.groupby('category')['amount'].sum()
                    if not category_amounts.empty:
                        fig1 = px.pie(
                            category_amounts,
                            values=category_amounts.values,
                            names=category_amounts.index,
                            title=f"Transaction Amounts by Category - {selected_month} {selected_year}"
                        )
                        fig1.update_layout(
                            width=1100, height=700,
                            font=dict(size=18),
                            title_font_size=18,
                            legend_font_size=14
                        )
                        st.plotly_chart(fig1)
                    else:
                        st.info("No categories found for the selected period.")
                    filtered_df.rename(columns={'amount': 'amount (INR)'}, inplace=True)
                    del filtered_df["year"]
                    st.table(filtered_df)
                    excel_buffer = BytesIO()
                    filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
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
                    cols = ['Date', 'Description', 'amount (INR)', 'Category', 'Payment Method']
                    col_widths = [25, 60, 35, 35, 35]
                    for col, width in zip(cols, col_widths):
                        pdf.cell(width, 10, col, 1, 0, 'C')
                    pdf.ln()

                    pdf.set_font("Arial", "", 10)
                    for _, row in filtered_df.iterrows():
                        pdf.cell(col_widths[0], 10, str(row['date']), 1, 0, 'C')
                        pdf.cell(col_widths[1], 10, str(row['description'])[:55], 1, 0, 'L')
                        pdf.cell(col_widths[2], 10, f"{row['amount (INR)']:.2f}", 1, 0, 'R')
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
            except Exception as e:
                st.error(f"Error processing transactions: {str(e)}")
    except Exception as e:
        st.error(f"Error viewing transactions: {str(e)}")
def format_amount(amount):
    """Formats the amount in Indian numbering style."""
    return '₹{:,.0f}'.format(amount).replace(',', 'X').replace('X', ',', 1) 
def summary():
    st.markdown("<h3 style='color: white;'>Summary</h3>", unsafe_allow_html=True)
    username = st.session_state.get("login_username", "")
    if not username:
        st.error("User not logged in!")
        return    
    user_file = check_and_initialize_user_data()
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
            tag_mapping_df = pd.read_csv("data/tag_mapping.csv")
            tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()
        except Exception as e:
            st.error("Failed to load tag mapping from CSV.")
            return
        try: 
    
            st.subheader("Spending by Tags")
            tags_df = yearly_df.assign(tags=yearly_df['tags'].str.split(',')).explode('tags')
            tags_df['tags'] = tags_df['tags'].str.strip().str.lower()
            tags_df['category'] = tags_df['tags'].map(tag_mapping).fillna('Uncategorized')
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
    username = st.session_state.get("login_username", "")
    if not username:
        st.error("User not logged in!")
        return
    user_file = check_and_initialize_user_data()
    if not os.path.exists(user_file):
        st.error(f"User data file not found: {user_file}. Please upload your data file.")
        return
    tag_mapping_file = "data/tag_mapping.csv"
    if not os.path.exists(tag_mapping_file):
        st.error(f"Tag mapping file not found: {tag_mapping_file}. Please ensure the file exists.")
        return

    try:
        df = pd.read_csv(user_file)
        if df.empty:
            st.warning("No transactions available for this user. Please add transactions to view the budget.")
            return

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.strftime('%B')
        df['year'] = df['date'].dt.year
        df['tags'] = df['tags'].str.split(',')

        tag_mapping_df = pd.read_csv(tag_mapping_file)
        tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()

        unique_years = sorted(df['year'].unique(), reverse=True)
        unique_months = df['month'].unique()

        selected_year = st.selectbox("Select Year", unique_years, index=0)
        selected_month = st.selectbox("Select Month", unique_months, index=0)

        current_month = pd.to_datetime('today').strftime('%B')
        current_year = pd.to_datetime('today').year
        is_current_period = (selected_month == current_month and selected_year == current_year)
        is_previous_period = (selected_year < current_year) or (selected_year == current_year and unique_months.tolist().index(selected_month) < unique_months.tolist().index(current_month))

        current_df = df[(df['month'] == selected_month) & (df['year'] == selected_year)]
        current_df = current_df.explode('tags')
        current_df['tags'] = current_df['tags'].str.strip().str.lower()
        current_df['category'] = current_df['tags'].map(tag_mapping).fillna('Uncategorized')

        current_df = current_df[current_df['category'] != 'Income']

        budget_file = f"data/{username}/{selected_year}_{selected_month}_budget.csv"

        try:
            budget_df = pd.read_csv(budget_file)
            existing_budgets = dict(zip(budget_df['Category'], budget_df['Budget']))
        except FileNotFoundError:
            existing_budgets = {}

        category_totals = current_df.groupby('category')['amount'].sum()

        budget_overview = pd.DataFrame({
            'Category': category_totals.index,
            'Spent': category_totals.values.astype(int),
            'Budget': [existing_budgets.get(category, 0.0) for category in category_totals.index],
        })
        budget_overview['Budget'] = budget_overview['Budget'].apply(
            lambda x: "Budget is not set" if x == 0 else f"{int(x)}"
        )
        budget_overview['Remaining'] = budget_overview['Budget'].apply(
            lambda x: 0 if x == "Budget is not set" else float(x)
        ) - budget_overview['Spent']
        budget_overview['Status'] = budget_overview['Remaining'].apply(
            lambda x: 'Within Budget' if x >= 0 else 'Exceeding Budget'
        )
        budget_overview['Remaining'] = budget_overview['Remaining'].astype(int)
        st.write(f"### Budget Overview for {selected_month} {selected_year}")
        st.table(budget_overview.round(2))
        st.write("### Budget Usage")
        budget_overview['Color'] = budget_overview['Status'].map({'Within Budget': 'green', 'Exceeding Budget': 'red'})
        charts_per_row = 2
        categories = budget_overview['Category'].unique()
        for i in range(0, len(categories), charts_per_row):
          cols = st.columns(charts_per_row)
          for j in range(charts_per_row):
              if i + j < len(categories):
                  category = categories[i + j]
                  row = budget_overview[budget_overview['Category'] == category].iloc[0]
                  fig = px.pie(
                names=['Spent', 'Remaining'],
                values=[row['Spent'], max(0, row['Remaining'])],
                color=['Spent', 'Remaining'],
                color_discrete_map={'Spent': row['Color'], 'Remaining': 'gray'},
                hole=0.5,
                title=f"{row['Category']} Budget Usage<br><sub>Status: {row['Status']}</sub>"
            )

                  fig.update_traces(
                hovertemplate='%{label}: %{value}<extra></extra>'
            )
                  fig.update_layout(
                annotations=[
                    dict(
                        text=f"<b>{row['Category']}</b>",
                        x=0.5,
                        y=0.5,
                        font_size=14,
                        showarrow=False
                    )
                ],
                showlegend=False,
                width=350,
                height=350
            )
                  cols[j].plotly_chart(fig)
        if is_current_period:
            st.write("### Set Budget")
            budget_settings = {}
            for category in current_df['category'].unique():
                default_value = existing_budgets.get(category, 0.0)
                try:
                    input_value = st.text_input(
                        f"Budget for {category}",
                        value=str(default_value)
                    )
                    # Check if input is a valid float
                    if input_value and input_value.replace(".", "").isdigit():
                        budget_settings[category] = float(input_value)
                    else:
                        st.error(f"Please enter a valid number for {category}")
                        budget_settings[category] = default_value
                except ValueError:
                    st.error(f"Invalid input for {category}. Using default value.")
                    budget_settings[category] = default_value
            if st.button("Save Budget"):
                budget_data = pd.DataFrame({
                    'Category': list(budget_settings.keys()),
                    'Budget': list(budget_settings.values())
                })
                budget_data.to_csv(budget_file, index=False)
                st.success("Budget saved successfully!")
                time.sleep(2)
                st.rerun()
        elif is_previous_period:
            st.warning("Budget settings for previous months are locked. You can only view the overview.")

    except Exception as e:
        st.error(f"Error processing budget: {str(e)}")
def portfolio():
    st.markdown("<h3 style='color: white;'>Portfolio Overview</h3>", unsafe_allow_html=True)
    username = st.session_state.get("login_username", "")
    if not username:
        st.error("User not logged in!")
        return

    user_file = check_and_initialize_user_data()
    if not os.path.exists(user_file):
        st.error(f"User data file not found: {user_file}. Please upload your data file.")
        return

    tag_mapping_file = "data/tag_mapping.csv"
    if not os.path.exists(tag_mapping_file):
        st.error(f"Tag mapping file not found: {tag_mapping_file}. Please ensure the file exists.")
        return

    try:
        # Load data and preprocess
        df = pd.read_csv(user_file)

        # Check if the file is empty
        if df.empty:
            st.warning("No transactions available for this user. Please add transactions to view the portfolio.")
            return

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.strftime('%B')
        df['year'] = df['date'].dt.year
        df['tags'] = df['tags'].str.split(',')

        tag_mapping_df = pd.read_csv(tag_mapping_file)
        tag_mapping = pd.Series(tag_mapping_df['category'].values, index=tag_mapping_df['tag'].str.lower()).to_dict()

        # Tag mapping and categorization
        df = df.explode('tags')
        df['tags'] = df['tags'].str.strip().str.lower()
        df['category'] = df['tags'].map(tag_mapping).fillna('Uncategorized')

        # Summary metrics
        total_spent = df[df['category'] != 'Income']['amount'].sum()
        total_income = df[df['category'] == 'Income']['amount'].sum()
        savings = total_income - total_spent

        # Display summary
        st.write("### Summary")
        st.metric("Total Income", f"₹{total_income:,.2f}")
        st.metric("Total Spent", f"₹{total_spent:,.2f}")
        st.metric("Savings", f"₹{savings:,.2f}")

        # Spending distribution by category
        st.write("### Spending Distribution by Category")
        category_totals = df[df['category'] != 'Income'].groupby('category')['amount'].sum().reset_index()
        fig = px.pie(
            category_totals,
            names='category',
            values='amount',
            title="Spending Distribution",
            hole=0.5
        )
        fig.update_traces(hovertemplate='%{label}: ₹%{value:,.2f}<extra></extra>')
        st.plotly_chart(fig)

        # Spending trends over time
        st.write("### Spending Trends")
        df['month_year'] = df['date'].dt.to_period('M').dt.to_timestamp()
        spending_trends = df[df['category'] != 'Income'].groupby('month_year')['amount'].sum().reset_index()
        fig = px.line(
            spending_trends,
            x='month_year',
            y='amount',
            title="Monthly Spending Trends",
            labels={'amount': 'Spent (₹)', 'month_year': 'Month'},
            markers=True
        )
        fig.update_layout(xaxis=dict(title="Month"), yaxis=dict(title="Amount Spent (₹)"))
        st.plotly_chart(fig)

        # Savings trends over time
        st.write("### Savings Trends")
        savings_trends = (
            df.groupby('month_year')
            .apply(lambda x: x[x['category'] == 'Income']['amount'].sum() - x[x['category'] != 'Income']['amount'].sum())
            .reset_index(name='savings')
        )
        fig = px.bar(
            savings_trends,
            x='month_year',
            y='savings',
            title="Monthly Savings Trends",
            labels={'savings': 'Savings (₹)', 'month_year': 'Month'},
            color='savings',
            color_continuous_scale=['red', 'green'],
        )
        fig.update_layout(xaxis=dict(title="Month"), yaxis=dict(title="Savings (₹)"))
        st.plotly_chart(fig)

        # Spending breakdown by individual categories
        st.write("### Detailed Spending Breakdown")
        category_breakdown = df[df['category'] != 'Income'].groupby(['category', 'month_year'])['amount'].sum().reset_index()
        fig = px.bar(
            category_breakdown,
            x='month_year',
            y='amount',
            color='category',
            title="Spending Breakdown by Category",
            labels={'amount': 'Spent (₹)', 'month_year': 'Month'},
        )
        fig.update_layout(xaxis=dict(title="Month"), yaxis=dict(title="Amount Spent (₹)"))
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error processing portfolio: {str(e)}")
