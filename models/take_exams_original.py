import streamlit as st
import json
from database import database
import pandas as pd
import time

def view_exams():
    st.sidebar.title("Available Exams")
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Fetch all exams and list them in the sidebar
    exams = cursor.execute("SELECT * FROM Exams").fetchall()
    if exams:
        exam_titles = {exam[0]: exam[2] for exam in exams}  # Map exam_id to title
        selected_exam_id = st.sidebar.selectbox("Select an Exam", options=list(exam_titles.keys()), format_func=lambda x: exam_titles[x])
    else:
        st.sidebar.warning("No exams available.")
        selected_exam_id = None
    
    # Display the selected exam details and questions on the main page
    if selected_exam_id:
        exam = next(exam for exam in exams if exam[0] == selected_exam_id)
        st.title(f"Exam: {exam[2]}")
        st.write(f"No of questions: {len(json.loads(exam[4]))}")
        st.write("Each question has multiple choice answers and each question carries 2 marks. Select the correct answer and submit the exam.")
        questions = json.loads(exam[4])
        is_answered = cursor.execute("SELECT Is_answered FROM results WHERE exam_id = ? AND student_id = ? AND exam_title = ?", (selected_exam_id, st.session_state["username"], exam[2])).fetchone()
        print(is_answered)
        take_exam(selected_exam_id, exam[2], questions, is_answered)
    conn.close()

def take_exam(exam_id,exam_title, questions,is_answered=False):
    """Student: Take an exam."""
    st.title("Take Exam")
    st.subheader(f"Exam ID: {exam_id}")

    # Check if the exam has already been answered
    if is_answered:
        st.warning("You have already answered this exam.")
        conn = database.get_db_connection()
        cursor = conn.cursor()

        score = cursor.execute("SELECT score FROM Results WHERE exam_id = ? AND student_id = ? AND exam_title = ?", (exam_id, st.session_state["username"], exam_title)).fetchone()
        st.write(f"Your score: {score[0]}")
        return
    else:
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

        # Initialize session state for exam tracking
        if 'exam_submitted' not in st.session_state:
            st.session_state.exam_submitted = False

        if not st.session_state.exam_submitted:
            st.session_state.exam_submitted = st.button("Submit Exam")
        
        if st.session_state.exam_submitted:

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
            # Save results into the database
            try:
                conn = database.get_db_connection()
                cursor = conn.cursor()

                # Insert the result into the Results table
                cursor.execute('''
                    INSERT INTO Results (exam_id, exam_title, student_id, score, total_questions, Is_answered, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    exam_id,  # Exam ID
                    exam_title,  # Exam title
                    st.session_state["username"],  # Current student's username
                    correct_count,  # Total correct answers (score)
                    total_questions,  # Total number of questions
                    True,  # Exam has been answered
                    time.strftime('%Y-%m-%d %H:%M:%S')  # Current date and time
                ))

                conn.commit()
                conn.close()
                st.balloons()
                st.success("Your results have been successfully saved!")
                st.session_state.exam_submitted = False
            except Exception as e:
                st.error(f"An error occurred while saving your results: {e}")

            if st.button("Done"):
                st.session_state.exam_submitted = False
                st.rerun()