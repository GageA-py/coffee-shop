from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from db import db, migrate
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, Products, CartItem
from forms import RegistrationForm, LoginForm
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

load_dotenv()

app = Flask(__name__)

# Configure db URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect(app)

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

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Check if item is already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    return redirect(url_for('show_products'))



@app.route('/cart')
@login_required
def view_cart():
    csrf_token = generate_csrf()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    data = request.get_json()
    quantity = data.get('quantity')
    # Update the cart with the new quantity
    update_cart_item(product_id, quantity)

    # Calculate the new total price
    total_price = calculate_total_price()  # Implement this function based on your logic

    return jsonify({'success': True, 'total_price': total_price})

    

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    csrf_token = generate_csrf()
    # Check if item is already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    # Check if cart item exists and if there's more than one
    # decrement if more than 1
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            # If 1 or less items delete from db
            db.session.delete(cart_item)
    
    db.session.commit()
    return redirect(url_for('view_cart'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged Out. Goodbye!', 'success')
    return redirect(url_for('login'))