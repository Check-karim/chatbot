from helper import db_helper, generic_helper
from flask import jsonify
import requests

global id
inprogress_orders = {}
id="1"
# inprogress_orders = {}
# id = request.cookies.get("user_id")
# print(id)

url = 'https://example.com'
response = requests.get(url)
cookies = response.cookies
for cookie in cookies:
    print(cookie.name, cookie.value)

def save_to_db(order: dict):
    if id is None:
        return {
            "fulfillmentText": "Please Login or SignUp First"
        }
    else:
        next_order_id = db_helper.get_next_order_id()
        # Insert individual items along with quantity in orders table
        for food_item, quantity in order.items():
            rcode = db_helper.insert_order_item(
                food_item,
                quantity,
                next_order_id,
                user_id = id
            )

            if rcode == -1:
                return -1

        # Now insert order tracking status
        db_helper.insert_order_tracking(next_order_id, "in progress", id)

        print('order_id',next_order_id)

        return next_order_id

def remove_from_order(parameters: dict, session_id: str):
    if id is None:
        return {
            "fulfillmentText": "Please Login or SignUp First"
        }
    else:
        if session_id not in inprogress_orders:
            return {
                "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
            }

        food_items = parameters["food-item"]
        current_order = inprogress_orders[session_id]

        removed_items = []
        no_such_items = []

        for item in food_items:
            if item not in current_order:
                no_such_items.append(item)
            else:
                removed_items.append(item)
                del current_order[item]

        if len(removed_items) > 0:
            fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

        if len(no_such_items) > 0:
            fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

        if len(current_order.keys()) == 0:
            fulfillment_text += " Your order is empty!"
        else:
            order_str = generic_helper.get_str_from_food_dict(current_order)
            fulfillment_text += f" Here is what is left in your order: {order_str} , Anything else"

        return {
            "fulfillmentText": fulfillment_text
        }

def complete_order(parameters: dict, session_id: str):
    if id is None:
        return {
            "fulfillmentText": "Please Login or SignUp First"
        }
    else:
        if session_id not in inprogress_orders:
            fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        else:
            order = inprogress_orders[session_id]
            order_id = save_to_db(order)
            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                                "Please place a new order again"
            else:
                order_total = int(db_helper.get_total_order_price(order_id))

                fulfillment_text = f"Awesome. We have placed your order. " \
                            f"Here is your order id # {order_id}. " \
                            f"Your order total is {order_total} RWF which you can pay at the time of delivery!"

            del inprogress_orders[session_id]

        return {
            "fulfillmentText": fulfillment_text
        }

def add_to_order(parameters: dict, session_id: str):
    if id is None:
        return {
            "fulfillmentText": "Please Login or SignUp First"
        }
    else:
        food_items = parameters["food-item"]
        quantities = parameters["number"]

        if len(food_items) != len(quantities):
            fulfillmentText = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
        else:
            new_food_dict = dict(zip(food_items, quantities))

            if session_id in inprogress_orders:
                current_food_dict = inprogress_orders[session_id]
                current_food_dict.update(new_food_dict)
                inprogress_orders[session_id] = current_food_dict
            else:
                inprogress_orders[session_id] = new_food_dict

            order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
            fulfillmentText = f"So far you have: {order_str}. Do you need anything else?"

        return {
            "fulfillmentText": fulfillmentText
        }

def track_order(parameters: dict, session_id: str):
    if id is None:
        return {
            "fulfillmentText": "Please Login or SignUp First"
        }
    else:
        order_id = int(parameters['order_id'])
        order_status = db_helper.get_order_status(order_id, id)
        if order_status:
            fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
        else:
            fulfillment_text = f"No order found with order id: {order_id}"

        print('track',fulfillment_text)

        return {
            "fulfillmentText": fulfillment_text
        }