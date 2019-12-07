from datetime import date
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from bid.models import User


class RegistrationForm(FlaskForm):
    """
    User registration form
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already taken by someone. Please, enter another username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already registered. Please, enter another email.')


class LoginForm(FlaskForm):
    """
    Login form
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    """
    Request to reset password by clicking on 'Forgot Password.'
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    """
    Resetting password.
    """
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class AddProductForm(FlaskForm):
    """
    Add new product.
    """

    product_name = StringField('Product Name', validators=[DataRequired(message='Must provide product name.')])
    product_description = TextAreaField('Product Description')
    category = StringField('Category', validators=[DataRequired(message='Must provide product category.')])
    minimum_bid = IntegerField('Minimum Bidding', validators=[DataRequired(message='Enter minimum bidding amount.')])
    last_date_to_bid = DateField('Last Date To Bid', validators=[
        DataRequired(message='Enter last date to bid on product.')
    ])
    picture = FileField('Add picture', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

    def validate_last_date_to_bid(self, *args, **kwargs):
        if self.last_date_to_bid.data < date.today():
            raise ValueError('Last date must be from future.')


class ApplyBid(FlaskForm):
    """
    Start bidding on product.
    """
    bid_value = IntegerField('Bidding Amount',
                             validators=[DataRequired(message='Must provide amount to apply bidding!')])
    note = TextAreaField('Note')
    submit = SubmitField('Apply')
