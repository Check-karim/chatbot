from flask import Blueprint,render_template,request,flash,session,redirect,jsonify,make_response
from controller.user import add_user_function,edit_user_function
import sys
from models.models import User
from helper import generic_helper,db_helper
# from controller import chat,order as order_function

main = Blueprint('main', __name__ ) #routename= main

@main.route('/chat', methods=['POST'])
def handle_request():
    """
    Dialogflow webhook endpoint - proxies to FastAPI backend with user authentication
    This endpoint receives webhooks from Dialogflow and forwards them to the FastAPI backend
    after injecting the user_id from the Flask session.
    """
    import requests
    
    # DEBUG: Log that webhook was called
    print("=" * 50, file=sys.stderr)
    print("WEBHOOK /chat CALLED", file=sys.stderr)
    
    payload = request.get_json(force=True)
    
    # Extract user_id from Dialogflow session ID
    # Session ID format: "user-{user_id}-{timestamp}" or default Dialogflow format
    user_id = None
    
    # Try to get session ID from payload
    if 'session' in payload:
        session_path = payload['session']
        print(f"Session path: {session_path}", file=sys.stderr)
        
        # Extract session ID from path (format: projects/.../sessions/SESSION_ID)
        if '/sessions/' in session_path:
            session_id = session_path.split('/sessions/')[-1]
            print(f"Session ID: {session_id}", file=sys.stderr)
            
            # Check if session ID contains user_id (format: user-123-timestamp)
            if session_id.startswith('user-'):
                parts = session_id.split('-')
                if len(parts) >= 2:
                    user_id = parts[1]  # Extract user_id
                    print(f"Extracted user_id from session: {user_id}", file=sys.stderr)
    
    # Fallback: Check Flask session as well
    if not user_id:
        user_id = session.get('user_id')
        if user_id:
            print(f"Got user_id from Flask session: {user_id}", file=sys.stderr)
    
    print(f"Final user_id: {user_id}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    if not user_id:
        # User not logged in - return auth error
        print("ERROR: No user_id found - returning auth error", file=sys.stderr)
        return jsonify({
            'fulfillmentText': 'Please log in to use the chatbot. You must be logged in to add, remove, or track courses.'
        })
    
    # Inject user_id into the payload
    if 'originalDetectIntentRequest' not in payload:
        payload['originalDetectIntentRequest'] = {}
    if 'payload' not in payload['originalDetectIntentRequest']:
        payload['originalDetectIntentRequest']['payload'] = {}
    
    payload['originalDetectIntentRequest']['payload']['user_id'] = str(user_id)
    
    # Forward to FastAPI backend
    try:
        # Update this URL to match your FastAPI backend location
        fastapi_url = 'http://localhost:8000/'  # Change port if different
        
        response = requests.post(
            fastapi_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return jsonify(response.json())
    
    except requests.exceptions.RequestException as e:
        print(f"Error forwarding to FastAPI backend: {e}", file=sys.stderr)
        return jsonify({
            'fulfillmentText': 'Sorry, there was an error processing your request. Please try again later.'
        }), 500

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