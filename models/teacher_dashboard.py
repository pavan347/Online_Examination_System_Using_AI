import streamlit as st

from utils import create_new_user, get_data
from models import generate_questions, manage_exams, view_performance

import yaml
from yaml.loader import SafeLoader

with open('config.yaml', 'r', encoding='utf-8') as file:
    config  = yaml.load(file, Loader=SafeLoader)

def display(authenticator):
    user_name = st.session_state["name"]
    st.markdown(f"<h1>Welcome <span style='color:red;'>{user_name}</span> to the Teacher Dashboard</h1>", unsafe_allow_html=True)
    st.write("Here, you can create and manage exams, view student performance, and more.")

    menu = ["Create Exam", "Manage Exams", "Register New Student","View Students", "View Student Marks or Performance"]
    choice = st.selectbox("Menu", menu, label_visibility="hidden")
    if choice == "Create Exam":
        # st.write("Code for creating exams")
        generate_questions.display("teacher")
    elif choice == "Manage Exams":
        # st.write("Code for managing exams")
        manage_exams.manage_exams()
    elif choice == "Register New Student":
        st.write("Code for registering new students")
        create_new_user.create_new_user('student',authenticator)
    elif choice == "View Students":
        students_data = get_data.get_data('student')
        st.title("Students")
        st.write("List of students:")
        st.dataframe(students_data, use_container_width=True)
    elif choice == "View Student Marks or Performance":
        st.write("Code for viewing student marks or performance")
        view_performance.display()
    

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)