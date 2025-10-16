# Quick Start - User Authentication Integration

## ⚡ Get Started in 5 Minutes

### 1️⃣ Start Your Services

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Flask App:**
```bash
python app.py
```

**Terminal 3 - ngrok (for Dialogflow webhook):**
```bash
ngrok http 5000
```

### 2️⃣ Configure Dialogflow

1. Go to [Dialogflow Console](https://dialogflow.cloud.google.com/)
2. Select your agent
3. Click **Fulfillment** → Enable Webhook
4. Set Webhook URL: `https://YOUR-NGROK-URL.ngrok.io/chat`
5. Save

### 3️⃣ Enable Webhook for Intents

Enable webhook for these 5 intents:
- `course.add - context: ongoing-add-course`
- `course.add.complete : context - ongoing-add-course`
- `track.course - context: ongoing-tracking-course`
- `course.remove - context-ongoing-remove-course`
- `course.remove.complete : context-ongoing-remove-course`

### 4️⃣ Test

1. Open http://localhost:5000
2. **Without login** → Try chatbot → Should say "Please log in..."
3. **Login** → Try chatbot → Should work!

---

## 🎯 What Changed?

| Before | After |
|--------|-------|
| Anyone can use chatbot | Only logged-in users |
| All courses saved with user_id = '2' | Uses actual user IDs |
| No authentication | Double validation (Flask + FastAPI) |

---

## 🔧 Quick Fixes

### Chatbot says "Please log in" but I'm logged in?
```python
# Check routes.py line 41 - make sure FastAPI URL is correct
fastapi_url = 'http://localhost:8000/'
```

### Webhook not working?
```bash
# Make sure all 3 services are running:
# 1. FastAPI on port 8000
# 2. Flask on port 5000  
# 3. ngrok tunnel active

# Test webhook:
curl https://YOUR-NGROK-URL.ngrok.io/chat
```

### Database still showing user_id = '2'?
```bash
# Restart FastAPI
cd backend
# Stop current server (Ctrl+C)
uvicorn main:app --reload --port 8000
```

---

## 📚 Full Documentation

- **SETUP_GUIDE.md** - Complete setup with troubleshooting
- **AUTHENTICATION_INTEGRATION.md** - Technical details
- **CHANGES_SUMMARY.md** - What was changed and why

---

## ✅ Verify It's Working

### Check 1: Flask Logs
Should see:
```
Webhook received
User ID: 123
Forwarding to FastAPI...
```

### Check 2: FastAPI Logs
Should see:
```
INFO: POST request received
User ID extracted: 123
Processing intent...
```

### Check 3: Database
```sql
SELECT * FROM course_items ORDER BY course_item_id DESC LIMIT 5;
-- course_user_id should be YOUR user ID, not '2'
```

### Check 4: Browser Console
Should see:
```
Chatbot active for user ID: 123
```

---

## 🚀 Production Deployment

When ready for production:

1. **Remove ngrok** - Use actual domain
2. **Update webhook URL** - https://yourdomain.com/chat
3. **Enable HTTPS** - Required for Dialogflow
4. **Secure cookies** - Update routes.py line 64
5. **Set environment variables** - Don't hardcode URLs

See SETUP_GUIDE.md for full production checklist.

---

## 🆘 Still Having Issues?

1. Check **SETUP_GUIDE.md** troubleshooting section
2. Enable debug logging (see SETUP_GUIDE.md)
3. Verify all 3 services are running
4. Check Dialogflow History for webhook errors
5. Look at Flask/FastAPI console for errors

---

**🎉 You're all set! Your chatbot now requires authentication!**

