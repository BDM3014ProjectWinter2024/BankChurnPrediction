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

# Display the Churn Rate Donut Chart

churn_rate = 15  # Assumption

# Draw and display the donut chart
donut_chart = draw_donut_chart(churn_rate)
st.pyplot(donut_chart)

# Display the List of Customers Likely to Churn

# Or for custom list layout
for index, row in customers_to_churn.iterrows():
    st.write(f"Customer ID: {row['customer_id']} - Predicted Churn: {row['churn_probability']}")

# Implement Navigation
if st.button('Back'):
    # Code to go back (usually this will be handled by your page control logic)
    pass

# For navigation links, you can also use st.sidebar for this
with st.sidebar:
    if st.button('Home'):
        # Navigate to Home
        pass
    if st.button('Reports'):
        # Navigate to Reports
        pass
    if st.button('Profile'):
        # Navigate to Profile
        pass
