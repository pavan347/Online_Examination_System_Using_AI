import streamlit as st
from streamlit_webrtc import webrtc_streamer
import cv2
import time
import json
from database import database
import pandas as pd

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

        # Reset timer and session state when a new exam is selected
    if selected_exam_id and ("current_exam_id" not in st.session_state or st.session_state.current_exam_id != selected_exam_id):
        st.session_state.current_exam_id = selected_exam_id
        st.session_state.start_time = None  # Clear the timer
        st.session_state.exam_submitted = False  # Reset submitted flag

    # Display the selected exam details and questions on the main page
    if selected_exam_id:
        exam = next(exam for exam in exams if exam[0] == selected_exam_id)
        st.title(f"Exam: {exam[2]}")
        st.write(f"No of questions: {len(json.loads(exam[4]))}")
        st.write("Each question has multiple choice answers and each question carries 2 marks. Select the correct answer and submit the exam.")
        questions = json.loads(exam[4])
        is_answered = cursor.execute("SELECT Is_answered FROM results WHERE exam_id = ? AND student_id = ? AND exam_title = ?", (selected_exam_id, st.session_state["username"], exam[2])).fetchone()
        take_exam(selected_exam_id, exam[2], questions, is_answered)
    conn.close()

def take_exam(exam_id, exam_title, questions, is_answered=False):
    """Student: Take an exam with timer and monitoring."""
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

        # Display questions and collect answers
        selected_options = []
        correct_answers = []
        explanations = []
        for i, question in enumerate(questions):
            st.subheader(f"Q{i + 1}: {question['mcq']}")
            options = list(question["options"].values())
            selected_option = st.radio(f"Select an answer for Q{i + 1}:", options, key=f"q{i}",index=None)
            selected_options.append(selected_option)
            correct_answers.append(question["options"][question["correct"]])
            explanations.append(question["explanation"])

        # Timer setup: 1 minute per question
        time_limit = len(questions) * 1  # Total time in seconds

        if 'start_time' not in st.session_state or st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = time_limit - elapsed_time
        
        print(remaining_time)
        minutes, seconds = divmod(int(remaining_time), 60)
        print(minutes, seconds)
        # Display the timer
        if remaining_time > 0:
            minutes, seconds = divmod(int(remaining_time), 60)
            st.sidebar.markdown(f"### Time Remaining: {minutes}:{seconds:02}")
            time.sleep(1)  # Update the timer every second
            st.rerun()
        else:
            st.error("Time's up! Submitting your exam automatically.")
            # submit_exam(exam_id, exam_title, questions, selected_options, explanations, correct_answers)
            # return
        
        

        # # Camera Monitoring Setup
        # st.sidebar.subheader("Monitoring via Webcam")
        # unusual_activity = False

        # def process_video_frame(frame):
        #     """Detect if the user is present in the frame."""
        #     global unusual_activity
        #     img = frame.to_ndarray(format="bgr24")
        #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        #     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        #     if len(faces) == 0:  # No face detected
        #         unusual_activity = True
        #     return frame

        # webrtc_streamer(key="camera", video_frame_callback=process_video_frame)

        # if unusual_activity:
        #     st.error("Unusual activity detected! Your exam is being terminated.")
        #     return



         # Initialize session state for exam tracking
        if 'exam_submitted' not in st.session_state:
            st.session_state.exam_submitted = False

        if not st.session_state.exam_submitted:
            st.session_state.exam_submitted = st.button("Submit Exam")
        
        if st.session_state.exam_submitted:
            submit_exam(exam_id, exam_title, questions, selected_options, explanations, correct_answers)

def submit_exam(exam_id, exam_title, questions, selected_options, explanations, correct_answers):


    """Submit the exam and calculate results."""
    correct_count = sum(
        1 for i, question in enumerate(questions)
        if selected_options[i] == question["options"][question["correct"]]
    )
    total_questions = len(questions)


        # Display score in larger text
    st.markdown(f"<h2>Your score: {correct_count}/{total_questions}</h2>", unsafe_allow_html=True)

    # Create a DataFrame for visualization
    results_df = pd.DataFrame({
        'Result': ['Correct', 'Incorrect'],
        'Count': [correct_count, total_questions - correct_count]
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


    # Save results to the database
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        # Save results to the database
        cursor.execute('''
            INSERT INTO Results (exam_id, exam_title, student_id, score, total_questions, Is_answered, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            exam_id,
            exam_title,
            st.session_state["username"],
            correct_count,
            total_questions,
            True,
            time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()

        # Display results
        st.balloons()
        st.success(f"Exam submitted! Your score: {correct_count}/{total_questions}")
        st.session_state.exam_submitted = False
    except Exception as e:
        st.error(f"An error occurred while saving your results: {e}")
    
    if st.button("Done"):
        st.session_state.exam_submitted = False
        st.rerun()
