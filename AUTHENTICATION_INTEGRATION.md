# Authentication Integration Guide

## Overview
This guide explains how to integrate user authentication from your Flask website with the FastAPI chatbot backend. The system now requires users to be logged in before they can use the chatbot to add, remove, or track courses.

## What Changed in `backend/main.py`

### 1. User ID Extraction
The webhook handler now extracts the `user_id` from the Dialogflow webhook payload:

```python
# Extract user_id from the payload (sent from Flask website)
user_id = None
if 'queryResult' in payload and 'queryParams' in payload['queryResult']:
    if 'payload' in payload['queryResult']['queryParams']:
        user_id = payload['queryResult']['queryParams']['payload'].get('user_id')

# Also check in originalDetectIntentRequest for user_id
if not user_id and 'originalDetectIntentRequest' in payload:
    if 'payload' in payload['originalDetectIntentRequest']:
        user_id = payload['originalDetectIntentRequest']['payload'].get('user_id')
```

### 2. Authentication Check
If no `user_id` is found, the chatbot will reject the request:

```python
# Validate that user is logged in
if not user_id:
    return JSONResponse(content={
        'fulfillmentText': "Please log in to use the chatbot. You must be logged in to add, remove, or track courses."
    })
```

### 3. Database Operations
All database operations now use the actual `user_id` instead of the hardcoded `'2'`:
- `save_to_db()` - Uses `user_id` for course enrollment
- `remove_to_db()` - Uses `user_id` for course removal
- All handler functions receive and pass `user_id`

## How to Integrate with Dialogflow

### Option 1: Using Dialogflow CX (Recommended)

If you're using Dialogflow CX, you can send user data through the webhook:

1. **In your Flask website, when initializing the Dialogflow chat:**

```javascript
// Get user_id from cookie or Flask session
function getUserId() {
    // Method 1: From cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'user_id') {
            return value;
        }
    }
    return null;
}

// When sending detect intent request to Dialogflow
const request = {
    session: sessionPath,
    queryInput: {
        text: {
            text: userMessage,
            languageCode: 'en-US',
        },
    },
    queryParams: {
        payload: {
            user_id: getUserId()
        }
    }
};
```

### Option 2: Using Dialogflow ES with Custom Payload

For Dialogflow ES (Essentials), modify your chat integration:

1. **Add user_id to the Dialogflow Web Integration:**

```javascript
<script>
window.addEventListener('dfMessengerLoaded', function (event) {
    const dfMessenger = document.querySelector('df-messenger');
    
    // Get user_id from cookie
    const userId = getUserId();
    
    // Set custom parameters
    dfMessenger.addEventListener('df-request-sent', function(event) {
        event.detail.queryParams = {
            payload: {
                user_id: userId
            }
        };
    });
});

function getUserId() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'user_id') {
            return value;
        }
    }
    return null;
}
</script>
```

### Option 3: Using Dialogflow Messenger Custom Payload

If you're using the Dialogflow Messenger widget:

```html
<df-messenger
  chat-title="Course Assistant"
  agent-id="YOUR_AGENT_ID"
  language-code="en"
  chat-icon="YOUR_ICON_URL">
  <df-messenger-user-input placeholder="Type your message..."></df-messenger-user-input>
</df-messenger>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const messenger = document.querySelector('df-messenger');
    
    // Get user_id from cookie (set by Flask)
    function getUserId() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'user_id') {
                return value;
            }
        }
        return null;
    }
    
    // Add user_id to every request
    messenger.addEventListener('df-request-sent', function(event) {
        const userId = getUserId();
        if (event.detail.requestPayload) {
            event.detail.requestPayload.queryParams = {
                payload: {
                    user_id: userId
                }
            };
        }
    });
});
</script>
```

### Option 4: Server-Side Integration (Most Secure)

If you're handling Dialogflow requests server-side through Flask:

1. **Create a Flask route to proxy Dialogflow requests:**

```python
from flask import request, jsonify
import requests

@main.route('/dialogflow', methods=['POST'])
def dialogflow_proxy():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({
            'fulfillmentText': 'Please log in to use the chatbot.'
        }), 401
    
    user_id = session['user_id']
    user_message = request.json.get('message')
    
    # Send to Dialogflow with user_id
    dialogflow_request = {
        'queryInput': {
            'text': {
                'text': user_message,
                'languageCode': 'en-US'
            }
        },
        'queryParams': {
            'payload': {
                'user_id': str(user_id)
            }
        }
    }
    
    # Make request to Dialogflow
    # ... (implement Dialogflow API call here)
    
    return jsonify(response)
```

2. **Update your frontend to call the Flask proxy instead of Dialogflow directly:**

```javascript
async function sendMessageToChatbot(message) {
    const response = await fetch('/dialogflow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    });
    
    const data = await response.json();
    return data;
}
```

## Testing the Integration

### 1. Test Without Login
1. Log out from your Flask website
2. Try to interact with the chatbot
3. You should receive: "Please log in to use the chatbot. You must be logged in to add, remove, or track courses."

### 2. Test With Login
1. Log in to your Flask website
2. The `user_id` cookie should be set (you can verify in browser DevTools > Application > Cookies)
3. Interact with the chatbot to add/remove/track courses
4. The operations should work and use your actual user ID in the database

### 3. Verify Database Records
Check your database tables:
- `course_items` should have records with your actual `user_id` (not '2')
- `course_tracking` should have records with your actual `user_id`

## Troubleshooting

### Issue: Still seeing "Please log in" message even when logged in

**Solutions:**
1. Check if the `user_id` cookie is being set correctly in `routes.py` (line 64)
2. Verify the cookie is accessible by JavaScript (not httpOnly)
3. Check browser console for any JavaScript errors
4. Verify the Dialogflow integration is correctly reading and sending the cookie value

### Issue: Database still showing user_id as '2' or NULL

**Solutions:**
1. Ensure the `user_id` is being passed in the Dialogflow webhook payload
2. Check the FastAPI logs to see if `user_id` is being extracted correctly
3. Verify the Dialogflow webhook is configured correctly

### Issue: Chatbot not responding at all

**Solutions:**
1. Check if the FastAPI backend is running
2. Verify the webhook URL in Dialogflow is correct
3. Check FastAPI logs for any errors
4. Ensure all intent names in the `intent_handler_dict` match your Dialogflow intents

## Security Considerations

1. **Cookie Security**: Consider making the cookie secure and httpOnly for production:
   ```python
   response.set_cookie("user_id", str(id), secure=True, httponly=False, samesite='Strict')
   ```

2. **User ID Validation**: Consider adding user validation in the FastAPI backend:
   ```python
   # Verify user_id exists in database
   if not User.exists(user_id):
       return JSONResponse(content={
           'fulfillmentText': "Invalid user session. Please log in again."
       })
   ```

3. **Rate Limiting**: Implement rate limiting to prevent abuse

4. **HTTPS**: Always use HTTPS in production to protect cookie transmission

## Additional Features to Consider

1. **Session Timeout**: Add session timeout checking
2. **User Verification**: Verify user exists in database before processing
3. **Audit Logging**: Log all chatbot operations with user_id and timestamp
4. **Error Handling**: Add more robust error handling for edge cases
5. **User Permissions**: Implement role-based access control if needed

## Summary

The authentication integration is now complete in the backend. You need to:
1. Choose one of the integration methods above (Option 4 is recommended for security)
2. Implement the frontend changes to send `user_id` with Dialogflow requests
3. Test the integration thoroughly
4. Monitor logs to ensure everything works correctly

The backend will now:
- ✅ Reject requests without a valid `user_id`
- ✅ Use the actual `user_id` for all database operations
- ✅ Associate courses with the correct user
- ✅ Track operations per user

All database operations in `backend/main.py` have been updated to use the authenticated user's ID instead of hardcoded values.

