
import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="college-inquiry"
)


# Function to fetch the order status from the order_tracking table
def get_course_tracking_status(course_tracking_id):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM course_tracking WHERE course_tracking_id = {course_tracking_id}"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the course tracking status
    if result:
        return result[0]
    else:
        return None

# Function to get the next available course_tracking_id
def get_next_course_tracking_id():
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id
    query = "SELECT MAX(course_tracking_id) FROM course_tracking"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1

def insert_course_item(course_tracking_id, course_code, course_status, course_user_id):
    try:
        cursor = cnx.cursor()

        # Inserting the record into the course_items table
        insert_query = "INSERT INTO course_items (course_tracking_id, course_code, course_status, course_user_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (course_tracking_id, course_code, course_status, course_user_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        cnx.rollback()

        return -1

def remove_course_item(course_code,course_user_id):
    try:
        cursor = cnx.cursor()

        # Inserting the record into the course_items table
        insert_query = "DELETE FROM course_items  WHERE course_code = %s AND course_user_id = %s "
        cursor.execute(insert_query, (course_code,course_user_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        cnx.rollback()

        return -1

# Function to insert a record into the order_tracking table
def insert_course_tracking(course_tracking_id, tracking_status, course_user_id):
    cursor = cnx.cursor()

    # Inserting the record into the course_tracking table
    insert_query = "INSERT INTO course_tracking (course_tracking_id, status, user_id) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (course_tracking_id, tracking_status, course_user_id))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()
