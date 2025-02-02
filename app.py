import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

from models import admin_dashboard, student_dashboard, teacher_dashboard
from database import database

def main():
    database.init_db()
    ## Code for the sidebar Toggle by programatically changing the sidebar state
    # # Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
    # if 'sidebar_state' not in st.session_state:
    #     st.session_state.sidebar_state = 'expanded'

    # # Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
    # st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

    # Loading config file
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)

  

    # Creating the authenticator object
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # authenticator = stauth.Authenticate(
    #     '../config.yaml'
    # )

    if st.session_state["authentication_status"] is None:
        st.title("Welcome to the Online Examination System")

        st.write("This platform is designed to facilitate efficient online examinations. Whether you're a student, teacher, or administrator, you'll find a range of tools to streamline your academic journey.")




    # if st.button('Click to toggle sidebar state'):
    #     st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'

    # Creating a login widget
    try:
        authenticator.login()
    except LoginError as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        authenticator.logout(location='sidebar')
        
        if st.session_state["roles"]:
            user_role = st.session_state["roles"][0]
        else:
            user_role = None

        if user_role == "admin":
            # Admin dashboard
            admin_dashboard.display(authenticator)
            # ... admin-specific content and functionalities
        elif user_role == "teacher":
            # Teacher dashboard
            teacher_dashboard.display(authenticator)
            # ... teacher-specific content and functionalities
        elif user_role == "student":
            # Student dashboard
            student_dashboard.display()
            # ... student-specific content and functionalities

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')


    # # Creating a new user registration widget
    # try:
    #     (email_of_registered_user,
    #      username_of_registered_user,
    #      name_of_registered_user,) = authenticator.register_user()
    #     if email_of_registered_user:
    #         st.success('User registered successfully')
    # except RegisterError as e:
    #     st.error(e)


    # Saving config file
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)

if __name__ == "__main__":
    main()