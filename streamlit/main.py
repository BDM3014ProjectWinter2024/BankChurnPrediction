import time
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import pickle


# MongoDB libraries
from dotenv import load_dotenv, find_dotenv #Used for import the function to load .env file
import os
from pymongo import MongoClient #Used to create the connection
load_dotenv(find_dotenv()) #Shorcut to load the enviroment file



#'''Streamlit settings------------------------------------------------------------------------------------------------------------- '''

# Page title
st.set_page_config(page_title='Bank Churn App', 
                   page_icon='🤖', layout="wide", 
                   initial_sidebar_state="expanded")


#'''Connect to the DB------------------------------------------------------------------------------------------------------------- '''

@st.cache_resource

# def connect_db():
#     password = os.environ.get("MONGODB_PWD") #This is to grab the password from the .env file
#     connection_string = f"mongodb+srv://carlosmebratt:{password}@bdm1003.tnmvwtl.mongodb.net/?retryWrites=true&w=majority"
#     client = MongoClient(connection_string)
#     db=client["bankchurnapp"]    
#     return db

def connect_db():
    # Replace the connection string with the appropriate one for your local MongoDB instance
    connection_string = "mongodb://localhost:27017/"
    client = MongoClient(connection_string)
    db = client["bankchurnapp"]
    return db

#'''Login App Function------------------------------------------------------------------------------------------------------------- '''

def select_signup():
    st.session_state.form = 'signup_form'

def user_update(name, succesful_login):
    st.session_state.username = name
    st.session_state.succesful_login=succesful_login
    
def update_succesful_login(succesful_login):
    st.session_state.succesful_login=succesful_login

def login_app():
    db = connect_db()
    credentials_db=db["credentials"]

    
    # Initialize Session States.
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'form' not in st.session_state:
        st.session_state.form = ''

    if 'succesful_login' not in st.session_state:
        st.session_state.succesful_login = False    
            
    if st.session_state.username != '':
        st.sidebar.markdown(''':blue[You are logged in]''')
        
        logout = st.sidebar.button(label='Log Out')
        if logout:
            # Handle Logout Click
            st.session_state.username = ''  # Set username to empty string
            st.session_state.succesful_login = False  # Set successful_login to False
            st.session_state.form = ''  # Reset form state
            st.sidebar.success("You have successfully logged out!")
            st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar

    

    # Initialize Sing In or Sign Up forms
    if st.session_state.form == 'signup_form' and st.session_state.username == '':

    
        signup_form = st.sidebar.form(key='signup_form', clear_on_submit=True)
        new_username = signup_form.text_input(label='Enter Username*')
        new_user_email = signup_form.text_input(label='Enter Email Address*')
        new_user_pas = signup_form.text_input(label='Enter Password*', type='password')
        user_pas_conf = signup_form.text_input(label='Confirm Password*', type='password')
        note = signup_form.markdown('**required fields*')
        signup = signup_form.form_submit_button(label='Sign Up')
        
        if signup:
            if '' in [new_username, new_user_email, new_user_pas]:
                st.sidebar.error('Some fields are missing')
            else:
                if credentials_db.find_one({'username' : new_username}):
                    st.sidebar.error('This username already exists')
                if credentials_db.find_one({'email' : new_user_email}):
                    st.sidebar.error('This e-mail is already registered')
                else:
                    if new_user_pas != user_pas_conf:
                        st.sidebar.error('Passwords do not match')
                    else:
                        user_update(new_username,True)
                        credentials_db.insert_one({'username' : new_username, 
                                                'email' : new_user_email, 
                                                'password' : new_user_pas,
                                                "creation_time":datetime.now()})
                        

                        # Handle Logout Click
                        st.session_state.username = ''  # Set username to empty string
                        st.session_state.succesful_login = False  # Set successful_login to False
                        st.session_state.form = ''  # Reset form state
                        st.sidebar.success('You have successfully registered!')
                        st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar
                 
    
    
    elif st.session_state.username == '':
        login_form = st.sidebar.form(key='signin_form', clear_on_submit=True)
        username = login_form.text_input(label='Enter Username')
        password = login_form.text_input(label='Enter Password', type='password')        
        

        if credentials_db.find_one({'username' : username, 'password' : password}):
            login = login_form.form_submit_button(label='Sign In', on_click=user_update(username,True))
            if login:
                st.sidebar.success(f"You are logged in as {username.upper()}")  
                st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar
                del password
        else:
            login = login_form.form_submit_button(label='Sign In')
            if login:
                st.sidebar.error("Username or Password is incorrect. Please try again or create an account.")
        

    # 'Create Account' button
    if st.session_state.username == "" and st.session_state.form != 'signup_form':
        signup_request = st.sidebar.button('Create Account', on_click=select_signup)  
    
    return st.session_state.username, st.session_state.succesful_login



#'''Funcionality------------------------------------------------------------------------------------------------------------- '''
def form_content(username):
    
    st.header('Input data')
    st.markdown("**1. Load the clients' data**")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=False)      

    
    # Initiate the model building process
    if uploaded_file:  
        st.subheader('Processing the data')
        st.write('Processing in progress...')

        # Placeholder for model building process
        with st.spinner('Wait for it...'):
            time.sleep(2)

        #st.write('Customer predictions are now complete!')
        st.markdown(''':blue[Customer data has been loaded!]''')

        st.dataframe(data=df, use_container_width=True)


    #'''--------------------------------------------------------------------------------------
    
    st.markdown('**2. Load the saved model**')
    # Load the saved model
    uploaded_pkl = st.file_uploader("Upload .pkl file", type=["pkl"])

    # Check if a file is uploaded
    if uploaded_pkl is not None:
        st.write("File uploaded successfully!")

        try:
            # Load the model from the file
            loaded_model = pd.read_pickle(uploaded_pkl)
            st.success("Model loaded successfully!")

            
        except Exception as e:
            st.error(f"Error loading .pkl file: {e}")

    else:
        st.info("Please upload a .pkl file.")

    

    #'''--------------------------------------------------------------------------------------
    st.markdown('**3. Predict churn clients**')
    # Load the saved model
    if st.button('Predict'):
        # # Convert input data to numpy array
        input_data_np = np.array(df)  # Adjust input data format as needed

        # Perform inference using the loaded model
        prediction = loaded_model.predict(input_data_np)
        df['predictions'] = prediction
        # Display prediction
        st.dataframe(data=prediction, use_container_width=True)




#'''Main Function------------------------------------------------------------------------------------------------------------- '''
    

def main():
    # Initialize Session States.
    succesful_login=False
    username, succesful_login=login_app()

    st.title('Machine Learning App for Bank Churn Prediction')
    

    if succesful_login == False:        
        st.subheader("Please use the sidebar on the left to log in or create an account.")
        st.image('image1.png')

    else:
        with st.sidebar:             
            st.header(f"Welcome {username} !")
        
        form_content(username)


#'''Sidebar------------------------------------------------------------------------------------------------------------- '''

    
    with st.sidebar:

        with st.expander('About this app / Instructions'):
                    st.markdown('**What can this app do?**')
                    st.info('This app allow users to load a bank .csv file and use it to build a machine learning model to predict churn. The app also recomends actions to reduce churn.')

                    st.markdown('**How to use the app?**')
                    st.warning('To engage with the app, please login or create an account and then 1. Select a data set and 2. Click on "Run the model". As a result, this would initiate the ML model and data processing.')

                    st.markdown('**Under the hood**')
                    st.markdown('Data sets:')
                    st.code('''- You can upload your own data set or use the example data set provided in the app.
                    ''', language='markdown')
                    
                    st.markdown('Libraries used:')
                    st.code('''
                            * Pandas for data wrangling  
                            * Scikit-learn
                            * XGBoost for machine learning
                            * Streamlit for user interface
                    ''', language='markdown')

# Call the main function
if __name__ == '__main__':
    main()