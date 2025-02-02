import streamlit as st
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
import yaml
from yaml.loader import SafeLoader


with open('config.yaml', 'r', encoding='utf-8') as file:
    config  = yaml.load(file, Loader=SafeLoader)

def create_new_user(role,authenticator):
    try:
        (email_of_registered_user,
        username_of_registered_user,
        name_of_registered_user,) = authenticator.register_user(
            roles=[role],
            fields= {'Form name':f'Register {role.capitalize()}',
                        'Email':'Email',
                        'Username':'Username',
                        'Password':'Password',
                        'Repeat password':'Repeat password',
                        'Password hint':'Password hint',
                        'Captcha':"Verify you're not a robot",
                        'Register':f'Create new {role.capitalize()} Account',
                    },
            clear_on_submit = True
            )
        if email_of_registered_user:
            st.success('User registered successfully')
    except RegisterError as e:
        st.error(e)

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)