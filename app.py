from flask import Flask, render_template, url_for, flash, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_wtf import Form, FlaskForm
from wtforms import StringField, BooleanField, EmailField, SubmitField, PasswordField
from wtforms.validators import Length, DataRequired, Email, email
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# Configure db URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect(app)

#Initialize the db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create a model
class Users(db.Model):
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

# Create a register form wtforms
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')
    

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/login')
def login():
    form = RegistrationForm()
    return render_template('login.html', form=form)