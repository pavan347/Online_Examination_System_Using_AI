import sqlite3

# Database connection
def init_db():
    conn = sqlite3.connect('exam_app.db')
    cursor = conn.cursor()
    # Create exams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_by TEXT,
            title TEXT,
            description TEXT,
            questions TEXT
        )
    ''')
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            exam_title TEXT,
            student_id TEXT,
            score INTEGER,
            total_questions INTEGER,
            Is_answered BOOLEAN,
            date TEXT,
            FOREIGN KEY(exam_id) REFERENCES Exams(exam_id)
        )
    ''')
    conn.commit()
    return conn

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect('exam_app.db')