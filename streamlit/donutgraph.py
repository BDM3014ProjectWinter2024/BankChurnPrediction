import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Define a function to load data from a CSV file
@st.cache_data
def load_data():
    data = pd.read_csv('dummy_customers_to_churn.csv')
    return data

# Load data into dummy_customers_to_churn
dummy_customers_to_churn = load_data()

# Create a Function to Draw the Donut Chart
def draw_donut_chart(churn_rate):
    fig, ax = plt.subplots()
    size = 0.3
    vals = [churn_rate, 100 - churn_rate]

    ax.pie(vals, radius=1, wedgeprops=dict(width=size, edgecolor='w'))

    ax.set(aspect="equal")
    plt.text(-0.05, 0, f'{churn_rate}%', ha='center', va='center', fontsize=12)
    return fig

# Initialize session state variables
if 'navigation' not in st.session_state:
    st.session_state['navigation'] = 'home'
if 'selected_customer_id' not in st.session_state:
    st.session_state['selected_customer_id'] = None

# Define a function to handle customer ID click
def handle_customer_click(customer_id):
    st.session_state['selected_customer_id'] = customer_id
    st.session_state['navigation'] = 'customer_detail'

# Sidebar navigation
with st.sidebar:
    if st.button('Home'):
        st.session_state['navigation'] = 'home'
    if st.button('Reports'):
        st.session_state['navigation'] = 'reports'
    if st.button('Profile'):
        st.session_state['navigation'] = 'profile'

# Main page content based on navigation state
#if st.session_state['navigation'] == 'home':
    st.title("Churn Rate Dashboard")
    churn_rate = 15  # Assumption
    donut_chart = draw_donut_chart(churn_rate)
    st.pyplot(donut_chart)

    st.subheader("Customers Likely to Churn")
    for index, row in dummy_customers_to_churn.iterrows():
        if st.button(f"Customer ID: {row['customer_id']} - Predicted Churn: {row['churn_probability']}"):
            handle_customer_click(row['customer_id'])

#elif st.session_state['navigation'] == 'customer_detail':
    st.write(f"Details for customer ID: {st.session_state['selected_customer_id']}")

#elif st.session_state['navigation'] == 'reports':
#    st.write("Reports Page Content")

#elif st.session_state['navigation'] == 'profile':
#    st.write("Profile Page Content")
