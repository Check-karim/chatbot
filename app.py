from flask import Flask, render_template, request, jsonify, redirect, url_for
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
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

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

        myData = USERS(email= email, password= password)
        db.session.add(myData)
        db.session.commit()
        return

    return render_template("signUp.html")

@app.route('/login')
def login():
    return  render_template('login.html')

@app.post('/predict')
def predict():
    text = request.get_json().get('message')
    # todo if response is valid
    response = get_response(text)
    message = {'answer': response}

    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
