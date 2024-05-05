from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255),nullable=False,unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())
    orders = db.relationship('Orders', backref='user')

    @property
    def data(self):
        return{
            'id':self.id,
            'email':self.email,
            'password':self.password
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        r = cls.query.all()
        result = []

        for i in r:
            result.append(i.data)
        return result
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_by_email_password(cls, email,password):
        return cls.query.filter(cls.email == email, cls.password == password).first()


#  order_tracking table
class Order_tracking(db.Model):
    __tablename__ = 'order_tracking'

    order_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(255),nullable=False)
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())
    orders = db.relationship('Orders', backref='order_trackings')

    def __init__(self,order_id,status):
        self.order_id = order_id
        self.status = status
    
    def __repr__(self):
         return{
            'order_id':self.order_id,
            'status':self.status
        }
    

# food_items table
class Food_items(db.Model):
    __tablename__ = 'food_items'

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False,unique=True)
    price = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())
    orders = db.relationship('Orders', backref='food_item')

    def __init__(self,item_id,name,price):
        self.item_id = item_id
        self.name = name
        self.price = price
    
    def __repr__(self):
         return{
            'item_id':self.item_id,
            'name':self.name,
            'price':self.price
        }
    


# orders tables
class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_tracking.order_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('food_items.item_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.String(255),nullable=False)
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())

    def __init__(self,order_id,item_id,user_id,quantity,total_price):
        self.order_id = order_id
        self.item_id = item_id
        self.user_id = user_id
        self.quantity = quantity
        self.total_price = total_price
    
    def __repr__(self):
         return{
            'order_id':self.order_id,
            'item_id':self.item_id,
            'user_id':self.user_id,
            'quantity':self.quantity,
            'total_price':self.total_price,
        }