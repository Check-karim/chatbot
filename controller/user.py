from flask import request,flash
from models.models import User
from extensions import db
from sqlalchemy.exc import IntegrityError

def add_user_function():
    if request.method == "POST":
        email = request.form['Email_signUp']
        password = request.form['Passowrd_signUp']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered. Please use a different email or login instead.', 'warning')
            return None

        user = User(
            email = email,
            password = password
        )

        try:
            user.save()
            data = {
                'id': user.id,
                'email': user.email,
                'password': user.password
            }
            flash(user.email+' Successfully created your account', 'success')
            return data
        except IntegrityError:
            db.session.rollback()
            flash('This email is already registered. Please use a different email or login instead.', 'error')
            return None
    
def edit_user_function(data):
    if request.method == "POST":
        if request.form['email_update']:
            data.email = request.form['email_update']
        if request.form['passowrd_update']:
            data.password = request.form['passowrd_update']

        db.session.commit()
        return data