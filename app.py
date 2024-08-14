from flask import Flask, render_template, url_for, flash, redirect
from db import db, migrate
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, Products
from forms import RegistrationForm, LoginForm
from flask_wtf import CSRFProtect

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

@app.route('/coffee')
def show_products():
    products = Products.query.all()
    print("Products:", products)
    return render_template('coffee_shop.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new User with form data
        password_hash = generate_password_hash(form.password.data)
        user = Users(name=form.name.data, email=form.email.data, password=password_hash)
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
                flash('Login Successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Wrong Password. Try Again.', 'error')
        else:
            flash('That User Doesn\'t Exist', 'error')

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged Out. Goodbye!', 'success')
    return redirect(url_for('login'))