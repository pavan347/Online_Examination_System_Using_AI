import streamlit as st
import yaml
from yaml.loader import SafeLoader

from utils import create_new_user, get_data

from models import generate_questions, manage_exams, view_performance

with open('config.yaml', 'r', encoding='utf-8') as file:
    config  = yaml.load(file, Loader=SafeLoader)

def display(authenticator):
    user_name = st.session_state["name"]
    st.markdown(f"<h1>Welcome <span style='color:red;'>{user_name}</span> to the Admin Dashboard</h1>", unsafe_allow_html=True)

    menu = ["Register New Teacher", "Register New Student", "View Teachers", "View Students", "Create Exam", "Manage Exams", "view performance"]
    choice = st.selectbox("Menu", menu, label_visibility="hidden")
    if choice == "Register New Teacher":
        create_new_user.create_new_user('teacher',authenticator)
    elif choice == "Register New Student":
        create_new_user.create_new_user('student',authenticator)
    elif choice == "View Teachers":
        teachers_data = get_data.get_data('teacher')
        st.title("Teachers")
        st.write("List of teachers:")
        st.dataframe(teachers_data, use_container_width=True)
    elif choice == "View Students":
        students_data = get_data.get_data('student')
        st.title("Students")
        st.write("List of students:")
        st.dataframe(students_data, use_container_width=True)
    elif choice == "Create Exam":
        # st.write("Code for creating exams")
        generate_questions.display("admin")
    elif choice == "Manage Exams":
        # st.write("Code for managing exams")
        manage_exams.manage_exams()
    elif choice == "view performance":
        st.write("Code for viewing student marks or performance")
        view_performance.display()


# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)