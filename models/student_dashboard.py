import streamlit as st
from utils import get_data

from models import take_exams_original

def display():
    user_name = st.session_state["name"]
    st.markdown(f"<h1>Welcome <span style='color:red;'>{user_name}</span> to the Student Dashboard</h1>", unsafe_allow_html=True)
    st.write("Here, you can access all the functionalities available to students.")

    # Displaying the student-specific functionalities
    menu = ["View Exams", "View Profile"]
    choice = st.selectbox("Select an option", menu, label_visibility="hidden")

    if choice == "View Exams":
        st.write("Open the sidebar to view the exams.")
        take_exams_original.view_exams()
    elif choice == "View Profile":
        student_data = get_data.get_student_data(st.session_state["username"])
        st.write("Your profile information:")

        with st.container(): 
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**First Name:** {student_data['First Name']}")
                st.write(f"**Username:** {student_data['Username']}")

            with col2:
                st.write(f"**Last Name:** {student_data['Last Name']}")
                st.write(f"**Email:** {student_data['Email']}")

