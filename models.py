from flask_login import UserMixin
from app import db
from datetime import datetime

# Create a user model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # create string
    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'

# Create product model
class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125), nullable=False)
    price = db.Column(db.Float)
    image = db.Column(db.String(125))


# Create shopping cart model
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Store id of user, make sure its an int, relate to id column in user 
    # - each cart item assoc with user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Store id of product that was added to cart, foreign key relation
    # with id of product  - each cart item assoc with specific product
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # Create relationship between Product and CartItem
    product = db.relationship('Products', backref='cart_items')
    # Create relationship between Users and Cart items
    user = db.relationship('Users', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.product.name} (x{self.quantity})>'


    
