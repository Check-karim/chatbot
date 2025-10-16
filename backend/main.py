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

    intent_handler_dict = {
        'course.add - context: ongoing-add-course': add_course,
        'course.add.complete : context - ongoing-add-course': complete_add_course,
        'track.course - context: ongoing-tracking-course': track_course,
        'course.remove - context-ongoing-remove-course': remove_course,
        'course.remove.complete : context-ongoing-remove-course': complete_remove_course,
    }

    return intent_handler_dict[intent](parameters, session_id)


def save_to_db(course_items: dict):
    next_course_tracking_id = db_helper.get_next_course_tracking_id()
    
    for course_code in course_items:
        rcode = db_helper.insert_course_item(next_course_tracking_id,course_code,'IN PROGRESS','2')
            
        if rcode == -1:
            return -1

    db_helper.insert_course_tracking(next_course_tracking_id, "in progress","2")
    return next_course_tracking_id

def remove_to_db(course_items: dict):
    for course_code in course_items:
        rcode = db_helper.remove_course_item(course_code,'2')
            
        if rcode == -1:
            return -1
    return 1

def add_course(parameters: dict, session_id: str):
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

def remove_course(parameters: dict, session_id: str):
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

def complete_add_course(parameters: dict, session_id: str):
    if session_id not in inprogress_courses:
        fulfillmentText = "I'm having a trouble finding your course. Sorry! Can you add a course again please?"
    else:
        course_items = inprogress_courses[session_id]
        course_tracking_id = save_to_db(course_items)

        if course_tracking_id == -1:
            fulfillmentText = "I'm having a trouble saving your course. Sorry! Can you add a course again please?"
        else:
            fulfillmentText = f"Your courses has been added successfully. "\
            f" Your course tracking id is: {course_tracking_id} ."\
                f" please use this id to track your course status."

    return JSONResponse( content={
        'fulfillmentText': fulfillmentText
    })

def complete_remove_course(parameters: dict, session_id: str):
    if session_id not in inprogress_remove_course:
        fulfillmentText = "I'm having a trouble finding your course. Sorry! Can you remove course again please?"
    else:
        course_items = inprogress_remove_course[session_id]
        course_tracking_id = remove_to_db(course_items)

        if course_tracking_id == -1:
            fulfillmentText = "I'm having a trouble removing your course. Sorry! Can you remove course again please?"
        else:
            fulfillmentText = f"Your courses has been removed successfully. "

    return JSONResponse( content={
        'fulfillmentText': fulfillmentText
    })


def track_course(parameters: dict, session_id: str):
    course_tracking_id = int(parameters['number'])
    course_status = db_helper.get_course_tracking_status(course_tracking_id)

    if course_status:
        fulfillmentText = f"The course status for course tracking id: {course_tracking_id} is: {course_status}"
    else:
        fulfillmentText = f"No course found with course tracking id: {course_tracking_id}"

    return JSONResponse( content={
            'fulfillmentText': fulfillmentText
        })