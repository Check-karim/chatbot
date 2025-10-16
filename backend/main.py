from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_courses = {}
inprogress_remove_course = {}

@app.post('/')
async def handle_request(request: Request):
    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
    
    # Extract user_id from the payload (sent from Flask website)
    user_id = None
    
    # Method 1: Check if user_id is in the payload (from Flask proxy)
    if 'queryResult' in payload and 'queryParams' in payload['queryResult']:
        if 'payload' in payload['queryResult']['queryParams']:
            user_id = payload['queryResult']['queryParams']['payload'].get('user_id')
    
    # Method 2: Check in originalDetectIntentRequest for user_id
    if not user_id and 'originalDetectIntentRequest' in payload:
        if 'payload' in payload['originalDetectIntentRequest']:
            user_id = payload['originalDetectIntentRequest']['payload'].get('user_id')
    
    # Method 3: Extract from Dialogflow session ID (format: user-{user_id}-{timestamp})
    if not user_id and session_id:
        print(f"Attempting to extract user_id from session_id: {session_id}")
        if session_id.startswith('user-'):
            parts = session_id.split('-')
            if len(parts) >= 2:
                user_id = parts[1]
                print(f"Extracted user_id from session_id: {user_id}")
    
    # Validate that user is logged in
    if not user_id:
        print(f"ERROR: No user_id found. Session ID: {session_id}")
        return JSONResponse(content={
            'fulfillmentText': "Please log in to use the chatbot. You must be logged in to add, remove, or track courses."
        })
    
    print(f"Processing request for user_id: {user_id}")

    intent_handler_dict = {
        'course.add - context: ongoing-add-course': add_course,
        'course.add.complete : context - ongoing-add-course': complete_add_course,
        'track.course - context: ongoing-tracking-course': track_course,
        'course.remove - context-ongoing-remove-course': remove_course,
        'course.remove.complete : context-ongoing-remove-course': complete_remove_course,
    }

    return intent_handler_dict[intent](parameters, session_id, user_id)


def save_to_db(course_items: dict, user_id: str):
    next_course_tracking_id = db_helper.get_next_course_tracking_id()
    
    for course_code in course_items:
        rcode = db_helper.insert_course_item(next_course_tracking_id, course_code, 'IN PROGRESS', user_id)
            
        if rcode == -1:
            return -1

    db_helper.insert_course_tracking(next_course_tracking_id, "in progress", user_id)
    return next_course_tracking_id

def remove_to_db(course_items: dict, user_id: str):
    for course_code in course_items:
        rcode = db_helper.remove_course_item(course_code, user_id)
            
        if rcode == -1:
            return -1
    return 1

def add_course(parameters: dict, session_id: str, user_id: str):
    new_course = parameters['course_code']

    # If the session already has some courses, merge them
    if session_id in inprogress_courses:
        existing_courses = inprogress_courses[session_id]
        # Merge and remove duplicates
        inprogress_courses[session_id] = list(set(existing_courses + new_course))
    else:
        # New session, just assign
        inprogress_courses[session_id] = new_course

    course_items = inprogress_courses[session_id]

    fulfillementText = f"So far you have: {course_items}. Do you need anything else?"

    return JSONResponse( content={
        'fulfillmentText': fulfillementText
    })

def remove_course(parameters: dict, session_id: str, user_id: str):
    new_course = parameters['course_code']

    # If the session already has some courses, merge them
    if session_id in inprogress_remove_course:
        existing_courses = inprogress_remove_course[session_id]
        # Merge and remove duplicates
        inprogress_remove_course[session_id] = list(set(existing_courses + new_course))
    else:
        # New session, just assign
        inprogress_remove_course[session_id] = new_course

    course_items = inprogress_remove_course[session_id]

    fulfillementText = f"So far you have: {course_items}. You want to remove. Do you need anything else?"

    return JSONResponse( content={
        'fulfillmentText': fulfillementText
    })

def complete_add_course(parameters: dict, session_id: str, user_id: str):
    if session_id not in inprogress_courses:
        fulfillmentText = "I'm having a trouble finding your course. Sorry! Can you add a course again please?"
    else:
        course_items = inprogress_courses[session_id]
        course_tracking_id = save_to_db(course_items, user_id)

        if course_tracking_id == -1:
            fulfillmentText = "I'm having a trouble saving your course. Sorry! Can you add a course again please?"
        else:
            fulfillmentText = f"Your courses has been added successfully. "\
            f" Your course tracking id is: {course_tracking_id} ."\
                f" please use this id to track your course status."

    return JSONResponse( content={
        'fulfillmentText': fulfillmentText
    })

def complete_remove_course(parameters: dict, session_id: str, user_id: str):
    if session_id not in inprogress_remove_course:
        fulfillmentText = "I'm having a trouble finding your course. Sorry! Can you remove course again please?"
    else:
        course_items = inprogress_remove_course[session_id]
        course_tracking_id = remove_to_db(course_items, user_id)

        if course_tracking_id == -1:
            fulfillmentText = "I'm having a trouble removing your course. Sorry! Can you remove course again please?"
        else:
            fulfillmentText = f"Your courses has been removed successfully. "

    return JSONResponse( content={
        'fulfillmentText': fulfillmentText
    })


def track_course(parameters: dict, session_id: str, user_id: str):
    course_tracking_id = int(parameters['number'])
    course_status = db_helper.get_course_tracking_status(course_tracking_id)

    if course_status:
        fulfillmentText = f"The course status for course tracking id: {course_tracking_id} is: {course_status}"
    else:
        fulfillmentText = f"No course found with course tracking id: {course_tracking_id}"

    return JSONResponse( content={
            'fulfillmentText': fulfillmentText
        })