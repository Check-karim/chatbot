from flask import Blueprint,render_template,request,flash,session,redirect
from controller.user import add_user_function,edit_user_function
import sys
from models.models import User

main = Blueprint('main', __name__ ) #routename= main

@main.route('/', methods = ['GET'])
def home():
    data = User.get_all()
    print(data)
    return render_template("index.html")

@main.route('/signUp', methods= ['GET','POST'])
def signup():
    if session.get('user_id') is not None:
        return redirect('/dashboard')
    data = add_user_function()
    print(data, file= sys.stderr)
    return render_template("signUp.html", data=data)

@main.route('/login/', methods= ['GET','POST'])
def login():
    if session.get('user_id') is not None:
        return redirect('/dashboard')
    if request.method == 'POST':
        email = request.form['Email_login']
        password = request.form['Password_login']

        user = User.get_by_email_password(email,password)
        if user:
            session['user_id'] = user.id
            flash("Logged in Successfully ")
            return redirect('/dashboard')
        else :
            flash("incorrect password or email")
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        return render_template('dashboard.html', user=user)
    return redirect('/login')

@main.route('/logout')
def logout():
    if session.get('user_id') is not None:
        session.pop('user_id', None)
        return redirect('/')
    else:
        return redirect('/dashboard')
    
@main.route('/settings')
def settings():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        return render_template('settings.html', user=user)
    return redirect('/login')

@main.route('/edit-user', methods= ['GET','POST'])
def edit_user():
    if session.get('user_id') is not None:
        id = session['user_id']
        user = User.get_by_id(id)
        data = edit_user_function(user)
        print(data)
        return redirect('/settings')