import webbrowser
import threading
import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Secret key for session management
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fee-agent-fallback-secret-key-39182")

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'students.db')
PDF_FILENAME = "fee_structure.pdf"
PDF_TEXT = ""

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            semester TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scholarship_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            semester TEXT NOT NULL,
            family_income REAL NOT NULL,
            community TEXT NOT NULL,
            first_graduate TEXT NOT NULL,
            cgpa REAL NOT NULL,
            eligible_scholarships TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize SQLite database
init_db()

def extract_text_from_pdf():
    global PDF_TEXT
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PDF_FILENAME)
    if not os.path.exists(pdf_path):
        print(f"Warning: {PDF_FILENAME} not found. Please place it in the project root.")
        PDF_TEXT = ""
        return
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        PDF_TEXT = "\n".join(text_parts).strip()
        print(f"Successfully loaded and extracted text from {PDF_FILENAME} ({len(PDF_TEXT)} chars).")
    except Exception as e:
        print(f"Error reading {PDF_FILENAME}: {e}")
        PDF_TEXT = ""

# Load PDF content on startup
extract_text_from_pdf()

# Get api key from environment
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Gemini client at startup: {e}")

@app.route('/')
def index():
    # Route protection - redirect to login if user not authenticated
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    pdf_loaded = len(PDF_TEXT) > 0
    api_key_set = (os.environ.get("GEMINI_API_KEY") is not None)
    return render_template('index.html', 
                           pdf_loaded=pdf_loaded, 
                           api_key_set=api_key_set,
                           student_name=session.get('name'),
                           student_dept=session.get('department'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'student_id' in session:
        return redirect(url_for('index'))
        
    error = None
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        semester = request.form.get('semester', '').strip()
        password = request.form.get('password', '')

        if not (student_id and name and department and year and semester and password):
            error = "All fields are required."
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student_id,))
            if cursor.fetchone():
                error = f"Student ID {student_id} is already registered."
                conn.close()
            else:
                pw_hash = generate_password_hash(password)
                try:
                    cursor.execute(
                        'INSERT INTO students (student_id, name, department, year, semester, password_hash) VALUES (?, ?, ?, ?, ?, ?)',
                        (student_id, name, department, year, semester, pw_hash)
                    )
                    conn.commit()
                    conn.close()
                    return redirect(url_for('login', registered=True))
                except Exception as e:
                    error = f"Registration failed: {str(e)}"
                    conn.close()

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'student_id' in session:
        return redirect(url_for('index'))
        
    error = None
    registered = request.args.get('registered')
    success_msg = "Registration successful! Please login." if registered else None

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '')

        if not (student_id and password):
            error = "Both Student ID and Password are required."
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
            student = cursor.fetchone()
            conn.close()

            if student and check_password_hash(student['password_hash'], password):
                session['student_id'] = student['student_id']
                session['name'] = student['name']
                session['department'] = student['department']
                session['year'] = student['year']
                session['semester'] = student['semester']
                return redirect(url_for('index'))
            else:
                error = "Invalid Student ID or Password."

    return render_template('login.html', error=error, success_msg=success_msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/status', methods=['GET'])
def status():
    if 'student_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    pdf_loaded = len(PDF_TEXT) > 0
    if not pdf_loaded:
        extract_text_from_pdf()
        pdf_loaded = len(PDF_TEXT) > 0
        
    api_key_set = (os.environ.get("GEMINI_API_KEY") is not None)
    return jsonify({
        "pdf_loaded": pdf_loaded,
        "pdf_characters": len(PDF_TEXT),
        "api_key_set": api_key_set
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    # Protection - redirect to login if session not found
    if 'student_id' not in session:
        return jsonify({"error": "Unauthorized. Please login first."}), 401
        
    global client
    
    current_api_key = os.environ.get("GEMINI_API_KEY")
    if not current_api_key:
        return jsonify({"error": "GEMINI_API_KEY is not set. Please set it in your environment or .env file."}), 500
        
    # Re-initialize client if key wasn't present at startup or changed
    if not client:
        try:
            client = genai.Client(api_key=current_api_key)
        except Exception as e:
            return jsonify({"error": f"Failed to initialize Gemini client: {str(e)}"}), 500

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    history = data.get('history', [])

    if not message:
        return jsonify({"error": "Message is empty"}), 400

    # Ensure PDF text is loaded
    global PDF_TEXT
    if not PDF_TEXT:
        extract_text_from_pdf()

    # Strict prompt instruction
    system_instruction = (
        "You are a Fee Inquiry Agent for V.S.B. Engineering College, Karur.\n"
        "Your task is to answer user queries about fees strictly using the provided fee structure text below.\n\n"
        "RULES:\n"
        "1. Rely ONLY on the information in the Fee Structure PDF text provided below.\n"
        "2. If the user's question cannot be answered using the provided text, respond politely stating that the information is unavailable.\n"
        "3. Do NOT make up information or use any external knowledge. If a course, fee, service, or rule is not explicitly mentioned in the text, you must say that the information is unavailable.\n"
        "4. Keep answers clear, accurate, and concise. Be professional and helpful.\n"
        "5. CRITICAL SCHOLARSHIP RULE: If the student asks 'What scholarships are available?' or has questions about scholarship availability, you MUST answer EXACTLY as follows:\n"
        "The following scholarships are available:\n"
        "• First Graduate Scholarship\n"
        "• Merit Scholarship\n"
        "• BC/MBC Scholarship\n"
        "• SC/ST Scholarship\n\n"
        "To know which scholarships you are eligible for, please use the Scholarship Eligibility Checker available on your dashboard.\n\n"
        f"FEE STRUCTURE TEXT:\n{PDF_TEXT if PDF_TEXT else 'No fee structure is currently loaded or available.'}"
    )

    try:
        # Format conversation history for Gemini API
        formatted_contents = []
        for turn in history:
            role = turn.get('role')
            text = turn.get('content')
            if role in ['user', 'model'] and text:
                formatted_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    )
                )

        # Add current user message
        formatted_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            )
        )

        # Call Gemini API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
        )

        reply = response.text if response.text else "The information is unavailable."
        return jsonify({"reply": reply})

    except APIError as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"error": f"Gemini API Error: {e.message}"}), 500
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/scholarship-checker', methods=['GET', 'POST'])
def scholarship_checker():
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    error = None
    result = None
    
    if request.method == 'POST':
        family_income_raw = request.form.get('family_income', '').strip()
        community = request.form.get('community', '').strip()
        first_graduate = request.form.get('first_graduate', '').strip()
        cgpa_raw = request.form.get('cgpa', '').strip()
        
        if not (family_income_raw and community and first_graduate and cgpa_raw):
            error = "Please fill in all the form fields."
        else:
            try:
                family_income = float(family_income_raw)
                cgpa = float(cgpa_raw)
                
                if cgpa < 0.0 or cgpa > 10.0:
                    error = "CGPA must be between 0.0 and 10.0."
                elif family_income < 0:
                    error = "Annual Family Income cannot be negative."
                else:
                    # Apply Rules
                    eligible = []
                    not_eligible = []
                    
                    # Rule 1: First Graduate
                    if first_graduate == 'Yes':
                        eligible.append('First Graduate Scholarship')
                    else:
                        not_eligible.append('First Graduate Scholarship')
                        
                    # Rule 2: Merit Scholarship
                    if cgpa >= 8.5:
                        eligible.append('Merit Scholarship')
                    else:
                        not_eligible.append('Merit Scholarship')
                        
                    # Rule 3: BC/MBC Scholarship
                    if community in ['BC', 'MBC']:
                        eligible.append('BC/MBC Scholarship')
                    else:
                        not_eligible.append('BC/MBC Scholarship')
                        
                    # Rule 4: SC/ST Scholarship
                    if community in ['SC', 'ST']:
                        eligible.append('SC/ST Scholarship')
                    else:
                        not_eligible.append('SC/ST Scholarship')
                        
                    eligible_str = ", ".join(eligible)
                    
                    # Save results to database
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO scholarship_results 
                        (student_id, name, department, year, semester, family_income, community, first_graduate, cgpa, eligible_scholarships)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session['student_id'],
                        session['name'],
                        session['department'],
                        session['year'],
                        session['semester'],
                        family_income,
                        community,
                        first_graduate,
                        cgpa,
                        eligible_str
                    ))
                    conn.commit()
                    conn.close()
                    
                    # Format results to pass to template
                    result = {
                        "name": session['name'],
                        "student_id": session['student_id'],
                        "department": session['department'],
                        "year": session['year'],
                        "semester": session['semester'],
                        "eligible": eligible,
                        "not_eligible": not_eligible,
                        "eligible_count": len(eligible)
                    }
            except ValueError:
                error = "Please enter valid numeric values for Income and CGPA."
                
    return render_template('scholarship_checker.html',
                           student_name=session.get('name'),
                           student_id=session.get('student_id'),
                           student_dept=session.get('department'),
                           student_year=session.get('year'),
                           student_sem=session.get('semester'),
                           error=error,
                           result=result)

@app.route('/previous-scholarships')
def previous_scholarships():
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM scholarship_results 
        WHERE student_id = ? 
        ORDER BY timestamp DESC
    ''', (session['student_id'],))
    results = cursor.fetchall()
    conn.close()
    
    return render_template('previous_scholarships.html', 
                           student_name=session.get('name'),
                           student_dept=session.get('department'),
                           results=results)
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")
if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.5, open_browser).start()

    app.run(host='127.0.0.1', port=5000, debug=True)