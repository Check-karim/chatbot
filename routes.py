from flask import Blueprint,render_template,request,flash,session,redirect,jsonify,make_response
from controller.user import add_user_function,edit_user_function
import sys
from models.models import User
from helper import generic_helper,db_helper
# from controller import chat,order as order_function

main = Blueprint('main', __name__ ) #routename= main

@main.route('/chat', methods=['POST'])
async def handle_request():
    payload = request.get_json(force=True)
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        'order.add - context: ongoing-order': chat.add_to_order,
        'order.remove - context: ongoing-order': chat.remove_from_order,
        'order.complete - context: ongoing-order': chat.complete_order,
        'track.order - context: ongoing-tracking': chat.track_order
    }

    return intent_handler_dict[intent](parameters, session_id)

@main.route('/', methods = ['GET'])
def home():
    if session.get('user_id') is None:
        return render_template("index.html")
    else:
        user = User.get_by_id(session['user_id'])
        print(user)
        return render_template("index.html", user=user)
    
@main.route('/about', methods = ['GET'])
def about():
    if session.get('user_id') is None:
        return render_template("about.html")
    else:
        user = User.get_by_id(session['user_id'])
        return render_template("about.html", user=user)

@main.route('/signUp', methods= ['GET','POST'])
def signup():
    if session.get('user_id') is not None:
        return redirect('/dashboard')
    data = add_user_function()
    print(data, file= sys.stderr)
    return render_template("signUp.html", data=data)

@main.route('/login', methods= ['GET','POST'])
def login():
    if session.get('user_id') is not None:
        return redirect('/dashboard')
    if request.method == 'POST':
        email = request.form['Email_login']
        password = request.form['Password_login']
        user = User.get_by_email_password(email,password)
        if user:
            id = user.id
            session['user_id'] = id
            response = make_response(redirect('/dashboard'))
            response.set_cookie("user_id", str(id))
            flash("Logged in Successfully", 'success')
            return response
        else :
            flash("Incorrect password or email. Please try again.", 'error')
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        if user.email == 'admin@admin.com':
            return redirect('/dashboard_admin')
        else:
            # orders = db_helper.get_client_order(user.id)
            courses = db_helper.get_all_courses()
            return render_template('dashboard.html', user=user, courses=courses)
    return redirect('/login')

@main.route('/dashboard_admin')
def dashboard_admin():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        if user.email == 'admin@admin.com':
            orders = db_helper.get_orders()
            courses = db_helper.get_all_courses()
            return render_template('dashboard_admin.html', user=user, orders=orders, courses=courses)
        else:
            return redirect('/dashboard')
    return redirect('/login')

@main.route('/update-order/<int:id>', methods=['POST'])
def update(id):
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        if user.email == 'admin@admin.com':
            data = order_function.update_order_function(id)
            flash("Order ID "+str(data.order_id)+" has been updated to "+str(data.status), 'success')
            return redirect('/dashboard')
        else:
            return redirect('/dashboard')
    return redirect('/login')

@main.route('/logout')
def logout():
    if session.get('user_id') is not None:
        response = make_response(redirect('/login'))
        response.delete_cookie('user_id')
        session.pop('user_id', None)
        return response
    else:
        return redirect('/dashboard')
    
@main.route('/settings')
def settings():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        courses = db_helper.get_all_courses()
        return render_template('settings.html', user=user, courses=courses)
    return redirect('/login')

@main.route('/edit-user', methods= ['GET','POST'])
def edit_user():
    if session.get('user_id') is not None:
        id = session['user_id']
        user = User.get_by_id(id)
        data = edit_user_function(user)
        print(data)
        return redirect('/settings')

@main.route('/items')
def items():
    if session.get('user_id') is not None:
        user = User.get_by_id(session['user_id'])
        # Get all unique courses for navigation
        all_courses = db_helper.get_all_courses()
        # Get all course enrollments for the main table
        all_enrollments = db_helper.get_all_enrollments()
        return render_template('items.html', user=user, courses=all_courses, enrollments=all_enrollments)
    return redirect('/login')