from flask import request,flash
from models.models import User
from extensions import db

def add_user_function():
    if request.method == "POST":
        email = request.form['Email_signUp']
        password = request.form['Passowrd_signUp']

        user = User(
            email = email,
            password = password
        )

        user.save()
        data = {
            'id': user.id,
            'email': user.email,
            'password': user.password
        }
        flash(user.email+' Successfully created your account')
        return data
    
def edit_user_function(data):
    if request.method == "POST":
        if request.form['email_update']:
            data.email = request.form['email_update']
        if request.form['passowrd_update']:
            data.password = request.form['passowrd_update']

        db.session.commit()
        return data