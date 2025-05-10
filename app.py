from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    resume = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    about = db.Column(db.Text)
    projects = db.Column(db.Text)
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            error_message = "Invalid login credentials, please try again."
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            filename = f"{uuid.uuid4()}_{user.email}_resume.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.resume = filename
            db.session.commit()
    return render_template('dashboard.html', user=user)

@app.route('/edit_portfolio', methods=['GET', 'POST'])
def edit_portfolio():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.skills = request.form['skills']
        user.about = request.form['about']
        user.projects = request.form['projects']
        user.linkedin = request.form['linkedin']
        user.github = request.form['github']
        db.session.commit()
        return redirect('/portfolio')
    return render_template('edit_portfolio.html', user=user)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    print(f"Message from {name} ({email}): {message}")

    return redirect(url_for('thank_you'))


@app.route('/portfolio')
def portfolio():
    user = User.query.get(session['user_id'])
    return render_template('portfolio.html', user=user)

@app.route('/download_resume/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/thank_you', methods=['GET'])
def thank_you():
    return render_template('thank_you.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
