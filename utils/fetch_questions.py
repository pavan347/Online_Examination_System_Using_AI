import streamlit as st
import json
import os
import google.generativeai as palm
from dotenv import load_dotenv
import pandas as pd
from fpdf import FPDF

load_dotenv()  # Load any other environment variables you might need

# Set the Google API Key (either through an environment variable or directly)
palm.configure(api_key=os.environ["API_KEY"])

model = palm.GenerativeModel("gemini-1.5-flash")

@st.cache_data
def fetch_questions(text_content, exam_level, no_of_questions):

    # Define a template for your prompt
    PROMPT_TEMPLATE = f"""
    Given the following content:
    "{text_content}"

    You are an expert quiz generator. Create {no_of_questions} unique multiple-choice questions (MCQs) based on the provided content, with the difficulty level set to {exam_level}. Ensure that the MCQs are diverse and correctly reflect the content.

    Format your response in JSON as shown below:
    {{
      "mcqs": [
        {{
          "mcq": "Question 1?",
          "options": {{
            "a": "Option 1",
            "b": "Option 2",
            "c": "Option 3",
            "d": "Option 4"
          }},
          "correct": "c",
          "explanation": "Explanation for the correct answer."
        }},
        ...
      ]
    }}
    """
    

    try:
        response = model.generate_content(PROMPT_TEMPLATE)
        # extracted_response = response.text
        # print(extracted_response)
        # return json.loads(extracted_response).get("mcqs", [])

        cleaned_response = response.text.strip()

        # Remove any wrapping triple backticks
        if cleaned_response.startswith("```json") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[7:-3].strip()
        
        print(cleaned_response)

        questions = json.loads(cleaned_response)
        return questions.get("mcqs", [])

    except Exception as e:
        print(f"Error generating questions: {e}")
        st.error(f"Failed to generate questions. {e}")
        return []  # Return empty list on error
