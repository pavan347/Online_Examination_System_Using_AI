import streamlit as st
import json
import os
import google.generativeai as palm
from dotenv import load_dotenv
import pandas as pd
from fpdf import FPDF

from utils import fetch_questions
from database import database
import time

def display(role):
    st.write("Generate questions and take exams from your text content.")

    #Input for the exam title
    exam_title = st.text_input("Enter the exam title:")

    # Input for text content
    text_content = st.text_area("Paste the text content here:")
    
    # Dropdown for difficulty level selection
    exam_level = st.selectbox("Select exam level:", ["Easy", "Medium", "Hard"])
    exam_level_lower = exam_level.lower()

    # Slider for number of questions
    no_of_questions = st.slider("Select number of questions:", 1, 10, 3)

    # Initialize session state for exam tracking
    if 'exam_generated' not in st.session_state:
        st.session_state.exam_generated = False

    # Track if Generate exam button is clicked
    if not st.session_state.exam_generated:
        st.session_state.exam_generated = st.button("Generate Questions")
    if st.session_state.exam_generated:
        if text_content == "":
            st.warning("Please paste some content to generate questions.")
            return
        elif exam_title == "":
            st.warning("Please enter the exam title.")
            return
        elif len(text_content) < 100:
            st.warning("The content should be greater than 100 characters to generate questions.")
            return
        elif len(text_content) > 5000:
            st.warning("The content should be less than 5000 characters to generate questions.")
            return

        questions = fetch_questions.fetch_questions(text_content=text_content, exam_level=exam_level_lower, no_of_questions=no_of_questions)

        if not questions:
            st.error("No questions were generated. Please try again.")
            return

        # Display questions and collect user answers
        selected_options = []
        correct_answers = []
        explanations = []
        correct_count = 0
        for i, question in enumerate(questions):
            st.subheader(f"Q{i + 1}: {question['mcq']}")
            options = list(question["options"].values())
            selected_option = st.radio(f"Select an answer for Q{i + 1}:", options, key=f"q{i}",index=None)
            selected_options.append(selected_option)
            correct_answers.append(question["options"][question["correct"]])
            explanations.append(question["explanation"])

            correct_answer = question["options"][question["correct"]]

            # Check if the selected answer is correct
            if selected_option == correct_answer:
                correct_count += 1

        # Submit button to evaluate answers
        if st.button("Submit"):

            total_questions = len(questions)
            incorrect_count = total_questions - correct_count

            # Display score in larger text
            st.markdown(f"<h2>Your score: {correct_count}/{total_questions}</h2>", unsafe_allow_html=True)

            # Create a DataFrame for visualization
            results_df = pd.DataFrame({
                'Result': ['Correct', 'Incorrect'],
                'Count': [correct_count, incorrect_count]
            })

            # Display a bar chart
            st.bar_chart(results_df.set_index('Result'))

            # marks = 0
            st.header("Questions Explanation:")
            for i, question in enumerate(questions):
                selected_option = selected_options[i]
                correct_option = correct_answers[i]
                explanation = explanations[i]
                st.subheader(f"{question['mcq']}")
                st.write(f"Your answer: {selected_option}")
                st.write(f"Correct answer: {correct_option}")
                st.write(f"Explanation: {explanation}")

                if selected_option == correct_option:
                    st.success("Correct!")
                    # marks += 1
                else:
                    st.error("Incorrect.")

        if st.button("Clear Questions"):
            st.session_state.exam_generated = False
            st.rerun()

        if st.session_state.exam_generated:
            if st.button("Save Exam"):
                # Save the exam to the database
                exam_saved = save_exam(exam_title, text_content, questions,role)
                if exam_saved:
                    st.balloons()
                    st.sidebar.success("Exam saved successfully!", icon="✅")
                    st.session_state.exam_generated = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Failed to save exam.")

                    

def save_exam(exam_title, text_content, questions, role):
    # Save the exam to the database
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exams (created_by, title, description, questions)
            VALUES (?, ?, ?, ?)
        ''', (st.session_state["username"]+ "({role})", exam_title, text_content, json.dumps(questions)))
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        return False
    
