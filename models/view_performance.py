import sqlite3
import pandas as pd
import streamlit as st

from database import database

def display():
    # Connect to the SQLite database
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Query to fetch data from the results table
    query = "SELECT * FROM results"
    results_df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    # Display the results table using Streamlit
    st.title('Results Table')
    st.dataframe(results_df)