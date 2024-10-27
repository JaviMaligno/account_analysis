import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bidict import bidict

#TODO add options to each individual plot to show/hide data and date granularity (should be possible to clear all filters and reset to global options)
#TODO add more plots and data about expenses
#TODO Grab data from database. Upload the csv to the database. 
periods = bidict({'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly', 'Q': 'Quarterly', 'Y': 'Yearly'})
period_names = bidict({'D': 'Day', 'W': 'Week', 'M': 'Month', 'Q': 'Quarter', 'Y': 'Year'})

# Function to load and process the uploaded CSV files
def load_data(uploaded_files):
    combined_data = pd.concat([pd.read_csv(file) for file in uploaded_files], ignore_index=True)
    combined_data['Date'] = pd.to_datetime(combined_data['Date'], format='%d-%m-%Y')
    combined_data = combined_data.sort_values(by='Date')
    # Ensure Currency column exists, default to 'GBP' if missing
    if 'Currency' not in combined_data.columns:
        combined_data['Currency'] = 'GBP'
    return combined_data

# New utility functions
def reindex_to_match(data_to_adjust, reference_data, fill_value=0):
    return data_to_adjust.reindex(reference_data.index, fill_value=fill_value)

def adjust_data(base_data, adjustments, adjustment_column=None):
    adjusted_data = base_data.copy()
    adjustments = reindex_to_match(adjustments, adjusted_data)
    
    if adjustment_column:
        adjusted_data[adjustment_column] += adjustments
    else:
        adjusted_data += adjustments
    
    return adjusted_data

# Modified filter_and_adjust_data function
def filter_and_adjust_data(combined_data, period='M'):
    filtered_data = combined_data[~combined_data['Description'].str.contains("GBP to", na=False)]
    filtered_periodic_balance = filtered_data.groupby(filtered_data['Date'].dt.to_period(period)).last()['Running Balance']

    removed_rows = combined_data[combined_data['Description'].str.contains("GBP to", na=False)]
    removed_rows['Adjusted Amount'] = -removed_rows['Amount']
    periodic_adjustments = removed_rows.groupby(removed_rows['Date'].dt.to_period(period))['Adjusted Amount'].sum()

    adjusted_periodic_balance = adjust_data(filtered_periodic_balance, periodic_adjustments)
    
    return filtered_periodic_balance, adjusted_periodic_balance

# Modified adjust_income_expenses function
def adjust_income_expenses(periodic_data, adjustments):
    return adjust_data(periodic_data, abs(adjustments), adjustment_column='Income')

# Function to calculate net changes
def calculate_net_changes(periodic_balance):
    return periodic_balance.diff()

#Function to calculate cumulative net changes
def calculate_cumulative_net_changes(periodic_balance):
    return periodic_balance.cumsum()

# Function to calculate percentage changes
def calculate_percentage_changes(periodic_balance):
    return periodic_balance.pct_change() * 100

# Function to calculate periodic income and expenses
def calculate_periodic_income_expenses(combined_data, period='M'):
    # Convert Date to period for monthly grouping
    combined_data['Period'] = combined_data['Date'].dt.to_period(period)
    
    # Calculate periodic income and expenses
    periodic_data = combined_data.groupby('Period').agg({
        'Amount': lambda x: (x[x > 0].sum(), x[x < 0].sum())
    })
    
    periodic_data['Income'] = periodic_data['Amount'].apply(lambda x: x[0])
    periodic_data['Expenses'] = periodic_data['Amount'].apply(lambda x: abs(x[1]))
    
    return periodic_data[['Income', 'Expenses']]

def calculate_cumulative_percentage_change(data):
    first_value = data.iloc[0]
    last_value = data.iloc[-1]
    cumulative_change = last_value - first_value
    cumulative_percentage_change = (cumulative_change / first_value) * 100
    return cumulative_percentage_change

# Function to plot histogram of income and expenses
def plot_histogram(periodic_balance, adjusted_periodic_balance, period='M', adjusted=False, expenses=False, income=False):
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(periodic_balance.index))
    width = 0.25  # width of each bar
    
    if adjusted:
        plt.bar(x - width, adjusted_periodic_balance['Income'], 
                width, label='Adjusted Income', color='green', alpha=0.7)
    
    if income:
        plt.bar(x, periodic_balance['Income'], 
                width, label='Income', color='blue', alpha=0.8)
    
    if expenses:
        plt.bar(x + width, periodic_balance['Expenses'], 
                width, label='Expenses', color='red', alpha=0.6)
    
    plt.title(f"{periods[period]} Income and Expenses")
    plt.xlabel(periods[period])
    plt.ylabel('Amount (GBP)')
    plt.legend()
    plt.grid(True, axis='y')
    plt.xticks(x, periodic_balance.index.astype(str), rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

# Modify the plot_data_with_option function
def plot_data(filtered, adjusted, title, ylabel, income_lable = 'Balance', adjusted_lable = 'Adjusted Balance', show_income=True, show_adjusted=True):
    plt.figure(figsize=(10, 6))
    
    if show_income:
        plt.plot(filtered.index.astype(str), filtered.values, marker='o', label=income_lable, color='blue')
    
    if show_adjusted:
        plt.plot(adjusted.index.astype(str), adjusted.values, marker='o', label=adjusted_lable, color='lightgreen')
    
    plt.title(title)
    plt.xlabel('Month')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Streamlit UI
st.title("Bank Statement Analysis")

# Upload CSV files
uploaded_files = st.file_uploader("Upload CSV", type="csv", accept_multiple_files=True)

# Add checkboxes for data display options
st.sidebar.header('Display Options')
show_adjusted = False
#show_adjusted = st.sidebar.checkbox("Show Adjusted Data", value=False)
show_income = st.sidebar.checkbox("Show Income", value=True)
show_expenses = st.sidebar.checkbox("Show Expenses", value=True)
show_data_tables = st.sidebar.checkbox("Show Data Tables", value=False)

# If both files are uploaded
if uploaded_files:
    combined_data = load_data(uploaded_files)
    

    # Sidebar for user inputs
    st.sidebar.header('Filter Options')
    period_name = st.sidebar.selectbox("Period", list(periods.values()), index=2)
    period = periods.inverse[period_name]
    # Date range selection
    start_date = st.sidebar.date_input('Start Date', combined_data['Date'].min())
    end_date = st.sidebar.date_input('End Date', combined_data['Date'].max())
    # Filter data based on user inputs
    date_mask = (
        (combined_data['Date'] >= pd.to_datetime(start_date)) &
        (combined_data['Date'] <= pd.to_datetime(end_date)) # & other filters
    )
     # Get available currencies and add currency selector
    available_currencies = combined_data['Currency'].unique()
    selected_currency = st.sidebar.selectbox("Select Currency", available_currencies)
    
    # Filter data for selected currency
    currency_mask = combined_data['Currency'] == selected_currency
    filtered_df = combined_data.loc[date_mask & currency_mask]

    # Ensure start_date is before end_date
    if start_date > end_date:
        st.sidebar.error('Error: Start date must be before end date.')

    if filtered_df is not None:
        filtered_periodic_balance, adjusted_periodic_balance = filter_and_adjust_data(filtered_df, period=period)

        # Calculate monthly income and expenses
        periodic_income_expenses = calculate_periodic_income_expenses(filtered_df, period=period)
        
        # Calculate adjustments
        removed_rows = filtered_df[filtered_df['Description'].str.contains("GBP to", na=False)]
        periodic_adjustments = -removed_rows.groupby(removed_rows['Date'].dt.to_period(period))['Amount'].sum()
        
        # Calculate adjusted income and expenses
        adjusted_income_expenses = adjust_income_expenses(periodic_income_expenses, periodic_adjustments)

        # Calculate net changes
        filtered_net_change = calculate_net_changes(filtered_periodic_balance)
        adjusted_net_change = calculate_net_changes(adjusted_periodic_balance)

        # Calculate cumulative net changes
        filtered_cumulative_net_changes = calculate_cumulative_net_changes(filtered_net_change)
        adjusted_cumulative_net_changes = calculate_cumulative_net_changes(adjusted_net_change)

        # Calculate percentage changes
        filtered_percentage_change = calculate_percentage_changes(filtered_periodic_balance)
        adjusted_percentage_change = calculate_percentage_changes(adjusted_periodic_balance)

        # Plot end-of-period balances
        st.subheader(f"End-of-{period_names[period]} Balance Evolution")
        plot_data(filtered_periodic_balance, adjusted_periodic_balance, 
                 f"End-of-{period_names[period]} Balance", 
                 f"Balance ({selected_currency})", 
                 show_income=show_income, 
                 show_adjusted=show_adjusted)

        # Plot net changes
        st.subheader("Net Change")
        plot_data(filtered_net_change, adjusted_net_change, 
                 "Net Change in Balance", 
                 f"Net Change ({selected_currency})", 
                 income_lable='Net Change', 
                 adjusted_lable='Adjusted Net Change', 
                 show_income=show_income, 
                 show_adjusted=show_adjusted)

        # Plot cumulative net changes
        st.subheader("Cumulative Net Change")
        plot_data(filtered_cumulative_net_changes, adjusted_cumulative_net_changes, f"Cumulative Net Change in {period_names[period]}", f"Cumulative Net Change ({period_names[period]})", show_income=show_income, show_adjusted=show_adjusted)

        # Plot percentage changes
        st.subheader("Percentage Change")
        plot_data(filtered_percentage_change, adjusted_percentage_change, "Month-over-Month Percentage Change", "Percentage Change (%)", income_lable='Percentage Change', adjusted_lable='Adjusted Percentage Change', show_income=show_income, show_adjusted=show_adjusted)

        # Plot histogram of income and expenses
        st.subheader(f"{period_name} Income and Expenses")
        plot_histogram(periodic_income_expenses, adjusted_income_expenses, period=period,
                       adjusted=show_adjusted, expenses=show_expenses, income=show_income)

        # Display averages
        st.subheader("Averages")
        st.write(f"Average Net Change: {filtered_net_change.mean():.2f} {selected_currency}")
        if show_adjusted:
            st.write(f"Average Adjusted Net Change: {adjusted_net_change.mean():.2f} {selected_currency}")
        st.write(f"Average Income: {periodic_income_expenses['Income'].mean():.2f} GBP")
        if show_adjusted:
            st.write(f"Average Adjusted Income: {adjusted_income_expenses['Income'].mean():.2f} GBP")
        st.write(f"Average Expenses: {periodic_income_expenses['Expenses'].mean():.2f} GBP")
        if show_adjusted:
            st.write(f"Average Adjusted Expenses: {adjusted_income_expenses['Expenses'].mean():.2f} GBP")

        st.subheader("Cumulative Percentage Change")
        cumulative_pct_change = calculate_cumulative_percentage_change(periodic_income_expenses['Income'])
        st.write(f"Cumulative Percentage Change in Income: {cumulative_pct_change:.2f}%")
        if show_adjusted:
            adjusted_cumulative_pct_change = calculate_cumulative_percentage_change(adjusted_income_expenses['Income'])
            st.write(f"Adjusted Cumulative Percentage Change in Income: {adjusted_cumulative_pct_change:.2f}%")

        if show_data_tables:
            st.header("Data tables")
            # Display data
            st.subheader("Data")
            st.write(filtered_df)

            # Display monthly adjustments
            if show_adjusted:
                st.subheader("Periodic Adjustments")
                st.write(periodic_adjustments)

            # Display filtered monthly balance
            st.subheader("Filtered Periodic Balance")
            st.write(filtered_periodic_balance)

            # Display adjusted monthly balance
            if show_adjusted:
                st.subheader("Adjusted Periodic Balance")
                st.write(adjusted_periodic_balance)

            # Display monthly income and expenses
            st.subheader("Periodic Income and Expenses")
            st.write(periodic_income_expenses)

            # Display adjusted income and expenses
            if show_adjusted:
                st.subheader("Adjusted Income and Expenses")
                st.write(adjusted_income_expenses)

            # Display filtered net change
            st.subheader("Filtered Net Change")
            st.write(filtered_net_change)

            # Display adjusted net change
            if show_adjusted:
                st.subheader("Adjusted Net Change")
                st.write(adjusted_net_change)

            # Display filtered cumulative net changes
            st.subheader("Filtered Cumulative Net Changes")
            st.write(filtered_cumulative_net_changes)

            # Display adjusted cumulative net changes
            if show_adjusted:
                st.subheader("Adjusted Cumulative Net Changes")
                st.write(adjusted_cumulative_net_changes)

            # Display filtered percentage changes
            st.subheader("Filtered Percentage Changes")
            st.write(filtered_percentage_change)

            # Display adjusted percentage changes
            if show_adjusted:
                st.subheader("Adjusted Percentage Changes")
                st.write(adjusted_percentage_change)

            # Display filtered periodic balance
            st.subheader("Filtered Periodic Balance")
            st.write(filtered_periodic_balance)

            # Display adjusted monthly balance
            if show_adjusted:
                st.subheader("Adjusted Periodic Balance")
                st.write(adjusted_periodic_balance)

            # Display periodic income and expenses
            st.subheader("Periodic Income and Expenses")
            st.write(periodic_income_expenses)

            # Display adjusted income and expenses
            if show_adjusted:
                st.subheader("Adjusted Income and Expenses")
                st.write(adjusted_income_expenses)

            # Display filtered net change
            st.subheader("Filtered Net Change")
            st.write(filtered_net_change)

            # Display adjusted net change
            if show_adjusted:
                st.subheader("Adjusted Net Change")
                st.write(adjusted_net_change)

            # Display filtered cumulative net changes
            st.subheader("Filtered Cumulative Net Changes")
            st.write(filtered_cumulative_net_changes)

            # Display adjusted cumulative net changes
            if show_adjusted:
                st.subheader("Adjusted Cumulative Net Changes")
                st.write(adjusted_cumulative_net_changes)

            # Display filtered percentage changes
            st.subheader("Filtered Percentage Changes")
            st.write(filtered_percentage_change)

            # Display adjusted percentage changes
            if show_adjusted:
                st.subheader("Adjusted Percentage Changes")
                st.write(adjusted_percentage_change)
