# User Authentication Integration - Setup Guide

## Overview

Your chatbot now requires user authentication! The system has been updated to ensure that only logged-in users can add, remove, or track courses. The user's ID is automatically associated with all their course operations.

## Architecture

```
User (Browser)
    ↓
Dialogflow Messenger Widget
    ↓
Dialogflow (Google Cloud)
    ↓
Flask Webhook (/chat) → Validates user session → Injects user_id
    ↓
FastAPI Backend (backend/main.py) → Validates user_id → Processes request
    ↓
MySQL Database (user_id stored with courses)
```

## What Was Changed

### 1. Backend (FastAPI) - `backend/main.py`
- ✅ Extracts `user_id` from webhook payload
- ✅ Validates user is logged in before processing
- ✅ Uses actual `user_id` in database operations (no more hardcoded '2')
- ✅ All handler functions updated to accept and use `user_id`

### 2. Frontend (Flask) - `routes.py`
- ✅ Created Flask webhook proxy at `/chat`
- ✅ Validates Flask session for user authentication
- ✅ Injects `user_id` into Dialogflow payload
- ✅ Forwards requests to FastAPI backend

### 3. Frontend Template - `templates/index.html`
- ✅ Added authentication status monitoring
- ✅ Console logging for debugging

## Setup Instructions

### Step 1: Start Your Services

1. **Start FastAPI Backend** (Terminal 1):
   ```bash
   cd backend
   # Activate virtual environment if using one
   # venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   
   uvicorn main:app --reload --port 8000
   ```

2. **Start Flask Application** (Terminal 2):
   ```bash
   # From project root
   # Activate virtual environment if using one
   # venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   
   python app.py
   ```
   
   Your Flask app should be running on `http://localhost:5000`

### Step 2: Configure Dialogflow Webhook

1. **Open Dialogflow Console**:
   - Go to [https://dialogflow.cloud.google.com/](https://dialogflow.cloud.google.com/)
   - Select your agent (PAUL - agent-id: b192fd09-52e5-49e1-aeac-bc6239516896)

2. **Configure Webhook URL**:
   - Click on "Fulfillment" in the left sidebar
   - Enable "Webhook"
   - Set the Webhook URL to: `https://your-domain.com/chat`
   
   **For Local Development:**
   - You'll need to expose your local Flask server using **ngrok** or similar tool:
     ```bash
     # Download ngrok from https://ngrok.com/
     # Or use the ngrok.exe in your project directory
     ngrok http 5000
     ```
   - Copy the HTTPS URL provided by ngrok (e.g., `https://abc123.ngrok.io`)
   - Set webhook URL to: `https://abc123.ngrok.io/chat`

3. **Enable Webhook for Intents**:
   - Go to each of these intents and enable "Enable webhook call for this intent":
     - `course.add - context: ongoing-add-course`
     - `course.add.complete : context - ongoing-add-course`
     - `track.course - context: ongoing-tracking-course`
     - `course.remove - context-ongoing-remove-course`
     - `course.remove.complete : context-ongoing-remove-course`

4. **Save** your changes

### Step 3: Verify Configuration

Check that:
- ✅ Flask is running on port 5000
- ✅ FastAPI is running on port 8000
- ✅ Dialogflow webhook URL is set to Flask `/chat` endpoint
- ✅ All course-related intents have webhook enabled
- ✅ If using ngrok, the tunnel is active

## Testing the Integration

### Test 1: Without Login (Should Fail)

1. Open your website: `http://localhost:5000`
2. **Do NOT log in**
3. Click on the chatbot icon
4. Try to add a course: "I want to add CSC 101"
5. **Expected Response**: "Please log in to use the chatbot. You must be logged in to add, remove, or track courses."

### Test 2: With Login (Should Work)

1. Log in to your website
2. Verify you can see your user ID in the browser console
3. Open the chatbot
4. Try to add a course: "I want to add CSC 101"
5. **Expected Response**: "So far you have: ['CSC 101']. Do you need anything else?"
6. Complete the order: "No, that's all"
7. **Expected Response**: "Your courses has been added successfully. Your course tracking id is: X. please use this id to track your course status."

### Test 3: Database Verification

1. Check your MySQL database:
   ```sql
   SELECT * FROM course_items WHERE course_user_id = 'YOUR_USER_ID';
   SELECT * FROM course_tracking WHERE user_id = 'YOUR_USER_ID';
   ```

2. Verify that:
   - ✅ Records exist with your actual user ID
   - ✅ No more records with hardcoded '2' for new entries

## Configuration Options

### Change FastAPI Backend URL

If your FastAPI backend runs on a different port or server, update `routes.py`:

```python
# Line 41 in routes.py
fastapi_url = 'http://localhost:8000/'  # Change this to your backend URL
```

### Change Flask Port

If you need to run Flask on a different port, update `app.py`:

```python
# Line 25 in app.py
app.run('127.0.0.1', 5000)  # Change 5000 to your desired port
```

### Session Security

For production, update cookie security in `routes.py`:

```python
# Line 64 in routes.py
response.set_cookie("user_id", str(id), secure=True, httponly=False, samesite='Strict')
```

## Troubleshooting

### Issue 1: "Please log in" message even when logged in

**Possible Causes:**
- Flask session not persisting
- Cookie not being set
- User logged out

**Solutions:**
1. Check browser cookies:
   - Open DevTools → Application → Cookies
   - Verify `session` cookie exists
   - Verify `user_id` cookie exists (optional)

2. Check Flask session:
   ```python
   # Add this to your Flask route for debugging
   print(f"User ID in session: {session.get('user_id')}")
   ```

3. Clear browser cookies and log in again

### Issue 2: Webhook not receiving requests

**Possible Causes:**
- Dialogflow webhook not configured
- ngrok tunnel expired
- Flask server not running
- Firewall blocking requests

**Solutions:**
1. Verify Dialogflow webhook URL is correct and HTTPS
2. Test webhook manually:
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/chat \
     -H "Content-Type: application/json" \
     -d '{"queryResult": {"intent": {"displayName": "test"}}}'
   ```
3. Check Flask logs for incoming requests
4. Restart ngrok if tunnel expired

### Issue 3: "Error forwarding to FastAPI backend"

**Possible Causes:**
- FastAPI server not running
- Wrong FastAPI URL in routes.py
- Port conflict

**Solutions:**
1. Verify FastAPI is running:
   ```bash
   curl http://localhost:8000/
   ```
2. Check FastAPI logs for errors
3. Verify port 8000 is not in use by another application
4. Update `fastapi_url` in `routes.py` if needed

### Issue 4: Database still showing user_id as '2'

**Possible Causes:**
- Old FastAPI code still running
- Database not updated
- Caching issue

**Solutions:**
1. Stop and restart FastAPI server
2. Clear Python cache:
   ```bash
   rm -rf backend/__pycache__
   ```
3. Verify `backend/main.py` has the updated code
4. Check FastAPI logs to see what user_id is being used

### Issue 5: Chatbot not responding at all

**Possible Causes:**
- Dialogflow agent not configured
- Intent names don't match
- Webhook disabled for intents

**Solutions:**
1. Verify intent names in Dialogflow match those in `backend/main.py`:
   - `course.add - context: ongoing-add-course`
   - `course.add.complete : context - ongoing-add-course`
   - `track.course - context: ongoing-tracking-course`
   - `course.remove - context-ongoing-remove-course`
   - `course.remove.complete : context-ongoing-remove-course`

2. Ensure webhook is enabled for all these intents
3. Test intents in Dialogflow console first

## Debugging Tips

### Enable Debug Logging

1. **Flask Debugging** - Add to `routes.py`:
   ```python
   @main.route('/chat', methods=['POST'])
   def handle_request():
       import json
       payload = request.get_json(force=True)
       print("=" * 50)
       print("WEBHOOK RECEIVED")
       print(f"User ID: {session.get('user_id')}")
       print(f"Payload: {json.dumps(payload, indent=2)}")
       print("=" * 50)
       # ... rest of the function
   ```

2. **FastAPI Debugging** - Add to `backend/main.py`:
   ```python
   @app.post('/')
   async def handle_request(request: Request):
       import json
       payload = await request.json()
       print("=" * 50)
       print("FASTAPI RECEIVED")
       print(f"Payload: {json.dumps(payload, indent=2)}")
       print("=" * 50)
       # ... rest of the function
   ```

3. **Browser Console**:
   - Open DevTools → Console
   - Look for authentication status messages
   - Check for any JavaScript errors

### Test Webhook Manually

```bash
# Test Flask webhook (with session cookie)
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "queryResult": {
      "intent": {"displayName": "course.add - context: ongoing-add-course"},
      "parameters": {"course_code": ["CSC 101"]},
      "outputContexts": [{
        "name": "projects/PROJECT_ID/agent/sessions/SESSION_ID/contexts/context-name"
      }]
    }
  }'

# Test FastAPI backend directly
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "queryResult": {
      "intent": {"displayName": "course.add - context: ongoing-add-course"},
      "parameters": {"course_code": ["CSC 101"]},
      "outputContexts": [{
        "name": "projects/PROJECT_ID/agent/sessions/SESSION_ID/contexts/context-name"
      }]
    },
    "originalDetectIntentRequest": {
      "payload": {"user_id": "2"}
    }
  }'
```

## Security Best Practices

### For Production Deployment:

1. **Use HTTPS everywhere**
   - Flask app must be behind HTTPS
   - FastAPI backend should be HTTPS
   - Never use ngrok in production

2. **Secure Cookies**
   ```python
   response.set_cookie(
       "user_id", 
       str(id), 
       secure=True,      # Only send over HTTPS
       httponly=True,    # Not accessible via JavaScript (more secure but prevents client-side reading)
       samesite='Strict' # Prevent CSRF attacks
   )
   ```

3. **Environment Variables**
   - Store FastAPI URL in environment variables
   - Don't hardcode URLs or secrets

4. **Rate Limiting**
   - Add rate limiting to webhook endpoint
   - Prevent abuse

5. **User Validation**
   - Verify user exists in database
   - Check user permissions

6. **Input Validation**
   - Validate all inputs in FastAPI backend
   - Sanitize course codes
   - Prevent SQL injection (use parameterized queries - already done in db_helper.py)

## Production Deployment Checklist

- [ ] Flask app deployed with HTTPS
- [ ] FastAPI backend deployed with HTTPS
- [ ] Environment variables configured
- [ ] Dialogflow webhook URL updated to production URL
- [ ] Database connection secured
- [ ] Cookies set to secure and httpOnly
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Error monitoring set up (e.g., Sentry)
- [ ] Backup strategy in place
- [ ] Load balancing configured (if needed)

## Support

If you encounter issues not covered in this guide:

1. Check Flask logs: Look for errors in your Flask console
2. Check FastAPI logs: Look for errors in your FastAPI console
3. Check Dialogflow logs: In Dialogflow console → History
4. Check browser console: For JavaScript errors
5. Check database: Verify data is being stored correctly

## Summary

✅ **Backend Updated**: FastAPI now validates user authentication and uses real user IDs

✅ **Middleware Added**: Flask proxy injects user ID securely server-side

✅ **Frontend Updated**: Template includes authentication monitoring

✅ **Security Enhanced**: User must be logged in to use chatbot features

✅ **Database Fixed**: All operations use actual user IDs instead of hardcoded values

Your chatbot is now fully integrated with your authentication system! 🎉

