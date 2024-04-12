import streamlit as st
import matplotlib.pyplot as plt

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

# Display the Churn Rate Donut Chart
churn_rate = 15  # Assumption
donut_chart = draw_donut_chart(churn_rate)
st.pyplot(donut_chart)

# Define a function to handle customer ID click
def handle_customer_click(customer_id):
    # Here you would define what happens when a customer ID is clicked
    # For demonstration purposes, we'll just write the ID to the page
    st.session_state['navigation'] = 'customer_detail'
    st.session_state['selected_customer_id'] = customer_id

# Check if we are on the 'customer_detail' page
if st.session_state['navigation'] == 'customer_detail':
    st.write(f"Details for customer ID: {st.session_state['selected_customer_id']}")

# Display the List of Customers Likely to Churn
# This assumes `customers_to_churn` is a DataFrame with customer data.
for index, row in dummy_customers_to_churn.iterrows():
    if st.button(f"Customer ID: {row['customer_id']}"):
        handle_customer_click(row['customer_id'])

# Sidebar navigation
with st.sidebar:
    if st.button('Home'):
        st.session_state['navigation'] = '

