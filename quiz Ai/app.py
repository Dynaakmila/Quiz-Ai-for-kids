from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import random, requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

questions = [
    {"question": "Apa kepanjangan dari AI?", "choices": ["Artificial Intelligence", "Automated Input", "Advanced Interface", "Algorithmic Integration"], "answer": "Artificial Intelligence"},
    {"question": "Library Python populer untuk AI adalah?", "choices": ["NumPy", "TensorFlow", "Flask", "BeautifulSoup"], "answer": "TensorFlow"},
    {"question": "Metode pembelajaran dalam AI disebut?", "choices": ["Supervised Learning", "Sorted Learning", "Synchronous Learning", "Single Learning"], "answer": "Supervised Learning"},
    {"question": "Model AI yang meniru kerja otak manusia disebut?", "choices": ["Neural Network", "Decision Tree", "Random Forest", "Clustering"], "answer": "Neural Network"}
]

@app.route('/')
def index():
    city = request.args.get('city')
    weather_data = None
    if city:
        api_url = 'https://api.open-meteo.com/v1/forecast?latitude=-6.9&longitude=107.6&daily=temperature_2m_max,temperature_2m_min&timezone=auto'
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                dates = data['daily']['time'][:3]
                temps_day = data['daily']['temperature_2m_max'][:3]
                temps_night = data['daily']['temperature_2m_min'][:3]
                weather_data = zip(dates, temps_day, temps_night)
        except:
            pass
    return render_template('index.html', weather_data=weather_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        if password != confirm:
            flash("Password tidak sama!")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username sudah dipakai!")
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registrasi berhasil! Silakan login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('quiz'))
        else:
            flash("Login gagal. Cek username atau password.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    question = random.choice(questions)
    if request.method == 'POST':
        selected = request.form.get('choice')
        if selected == request.form['answer']:
            current_user.score += 10
            db.session.commit()
            flash("Benar! Skor +10")
        else:
            flash("Salah! Coba lagi.")
        return redirect(url_for('quiz'))
    return render_template('quiz.html', question=question, score=current_user.score)

@app.route('/leaderboard')
def leaderboard():
    players = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', players=players)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
