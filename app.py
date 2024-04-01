from flask import Flask, render_template, request, jsonify, redirect, url_for,session
from flask_cors import CORS
from chat import get_response
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
# CORS(app)
app.secret_key = "secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/chatbot"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class USERS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, email,password):
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

@app.route('/')
def index_get():
    return render_template("index.html")

@app.route('/signUp', methods= ['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['Email_signUp']
        password = request.form['Passowrd_signUp']
        mydata = USERS(email= email, password= password)
        db.session.add(mydata)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("signUp.html")

@app.route('/login', methods= ['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form['Email_login']
        password = request.form['Password_login']

        user = USERS.query.filter_by(email=email).first()

        if user and user.check_password(password=password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid Users")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if session.get('email') is not None:
        user = USERS.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect('/login')

@app.route('/logout')
def logout():
    if session.get('email') is not None:
        session.pop('email', None)
        return redirect('/')
    else:
        return redirect('/dashboard')

@app.post('/predict')
def predict():
    text = request.get_json().get('message')
    # todo if response is valid
    response = get_response(text)
    message = {'answer': response}

    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
