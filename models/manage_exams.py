import streamlit as st
import yaml
from yaml.loader import SafeLoader
from database import database

import json
import time

def manage_exams():
    """Admin/Teacher: Manage exams (delete)."""
    st.title("Manage Exams")
    conn = database.get_db_connection()
    cursor = conn.cursor()
    exams = cursor.execute("SELECT * FROM Exams").fetchall()
    if exams:
        for exam in exams:
            with st.expander(f"{exam[2]}"):
                st.write(f"Topic: {exam[3]}")

                if st.button(f"Show Questions (Exam {exam[0]})"):
                    st.json(json.loads(exam[4]))

                if st.button(f"Delete Exam {exam[0]}"):
                    try:
                        cursor.execute("DELETE FROM Exams WHERE exam_id = ?", (exam[0],))
                        conn.commit()
                        st.success(f"Exam {exam[2]} deleted!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred, Pls Refresh the page and Try Again: {e}")
    else:
        st.warning("No exams available.")
    conn.close()

    
