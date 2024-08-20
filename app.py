from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from db import db, migrate
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, Products, CartItem
from forms import RegistrationForm, LoginForm, CheckoutForm
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_mail import Mail, Message
import stripe
import random

load_dotenv()

app = Flask(__name__)

# Configure db URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

csrf = CSRFProtect(app)
stripe.api_key = os.getenv('STRIPE_API_KEY')
mail = Mail(app)

# Initialize the db and migrate objects with the app
db.init_app(app)
migrate.init_app(app, db)

# Login details
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
    

@app.route('/')
def index():
    return render_template('index.html')

# COFFEE PRODUCTS PAGE
@app.route('/coffee')
def show_products():
    csrf_token = generate_csrf()
    products = Products.query.all()
    print("Products:", products)
    return render_template('coffee_shop.html', products=products, csrf_token=csrf_token)

@app.route('/send-email')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new User with form data
        password_hash = generate_password_hash(form.password.data)
        user = Users(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=password_hash)
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful!', 'success')
        return redirect(url_for('index'))
    # Render template and pass in form
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # Check hashed pass
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Wrong Password. Try Again.', 'error')
        else:
            flash('That User Doesn\'t Exist', 'error')

    return render_template('login.html', form=form)

def calculate_total_price():
    cart_items = CartItem.query.all()
    total = round(sum(item.quantity * item.product.price for item in cart_items), 2)
    return total

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)  
    if quantity <= 0:
        return redirect(url_for('show_products', error='Invalid quantity'))
    
    # Find an existing cart item or create a new one
    cart_item = CartItem.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if cart_item:
        cart_item.quantity += quantity  # Update the quantity
    else:
        cart_item = CartItem(product_id=product_id, quantity=quantity, user_id=current_user.id)
        db.session.add(cart_item)  # Add new item to the cart
    
    db.session.commit()  

    return redirect(url_for('show_products'))  # Redirect back to the products page


@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = round(sum(item.quantity * item.product.price for item in cart_items), 2)
    checkout_form = CheckoutForm()
    return render_template('cart.html', cart_items=cart_items, total=total, checkout_form=checkout_form) 



@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if request.method == 'POST':
        cart_item = CartItem.query.filter_by(product_id=product_id, user_id=current_user.id).first()
        if cart_item.quantity <= 1:
            db.session.delete(cart_item)
        
        else:
            cart_item.quantity -= 1
            calculate_total_price()
        db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def create_checkout_session():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'cad',   
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100)  # Convert dollars to cents
            },
            'quantity': item.quantity
        })
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:5000/success',
        cancel_url='http://127.0.0.1:5000/cancel'
    )
    return redirect(session.url, code=303)


@app.route('/success')
def success():
    # Query database for cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = round(sum(item.quantity * item.product.price for item in cart_items), 2)
    # render email with cart items, user info, total
    html_content = render_template('email_order_template.html', 
    user_name=current_user.first_name,
    order_items=cart_items, total=total)

    # Create order email 
    msg = Message('Order Confirmation',
    sender=os.getenv('MAIL_DEFAULT_SENDER'), 
    recipients=[current_user.email])
    msg.html = html_content

    # Send email message 
    mail.send(msg)
    return "Payment Successful! Thanks! :)"
    

@app.route('/cancelled')
def cancel():
    return "Payment Cancelled. :("

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged Out. Goodbye!', 'success')
    return redirect(url_for('login'))