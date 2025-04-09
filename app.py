from flask import Flask, render_template, request, redirect, url_for, session
import os
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from audio import audio_to_spectrogram, predict_spectrogram
from sentence import process_sentence_audio

app = Flask(__name__)
app.secret_key = '67345$@345!'

# MySQL Configuration
DB_HOST = 'localhost'
DB_USER = 'root'  # Change to your MySQL username
DB_PASSWORD = 'qwerty_123'  # Change to your MySQL password
DB_NAME = 'vericall'  # Database name

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to establish DB connection
def get_db_connection():
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

# Ensure database table exists
def setup_database():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    db.commit()
    cursor.close()
    db.close()

setup_database()  # Run once on startup

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "<h1>Invalid Credentials. Try again.</h1>"

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
        except MySQLdb.IntegrityError:
            cursor.close()
            db.close()
            return "<h1>Username already exists. Try a different one.</h1>"

        cursor.close()
        db.close()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/test_call', methods=['GET'])
def test_call():
    return render_template('test_call.html')

    # return redirect(url_for('login'))
@app.route('/learn_app')
def learn_app():
    return render_template('Learn_App.html')


@app.route('/audio_level_testing', methods=['GET', 'POST'])
def audio_level_testing():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        if "audio" not in request.files:
            return "No file uploaded", 400

        file = request.files["audio"]
        if file.filename == "":
            return "No selected file", 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        spectrogram_path = audio_to_spectrogram(file_path, UPLOAD_FOLDER)
        prediction = predict_spectrogram(spectrogram_path)

        return render_template("audio_test.html", prediction=prediction, spectrogram=spectrogram_path)

    return render_template("audio_test.html", prediction=None, spectrogram=None)

@app.route('/sentence_level_testing', methods=['GET', 'POST'])
def sentence_level_testing():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        if "audio" not in request.files:
            return "No file uploaded", 400

        file = request.files["audio"]
        if file.filename == "":
            return "No selected file", 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        transcription, classification = process_sentence_audio(file_path)

        if transcription is None:
            return render_template("sentence_test.html", transcription="Could not transcribe", classification="Error")

        return render_template("sentence_test.html", transcription=transcription, classification=classification)

    return render_template("sentence_test.html", transcription=None, classification=None)

if __name__ == '__main__':
    app.run(debug=True)



