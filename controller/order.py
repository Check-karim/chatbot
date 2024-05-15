from flask import request,flash
from models.models import Order_tracking
from extensions import db

def update_order_function(id):
    if request.method == "POST":
        status = request.form['status']

        data = Order_tracking.get_by_id(id)
        data.status = status
        db.session.commit()
        return data

        