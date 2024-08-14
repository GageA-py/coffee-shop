from flask_login import UserMixin
from app import db
from datetime import datetime

# Create a user model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password():
        self.password = generate_password_hash(password)

    def check_password():
        return check_password_hash(self.password, password)

    # create string
    def __repr__(self):
        return '<Name %r>' % self.name

# Create product model
class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125), nullable=False)
    price = db.Column(db.Float)
    image = db.Column(db.String(125))


    
