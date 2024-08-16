from flask_wtf import Form, FlaskForm
from wtforms import StringField, BooleanField, EmailField, SubmitField, PasswordField
from wtforms.validators import Length, DataRequired, Email, email
from flask_wtf import CSRFProtect

# Create a register form wtforms
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

# Create Login Form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')