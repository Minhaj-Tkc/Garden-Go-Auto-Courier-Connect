from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField
from wtforms.validators import InputRequired, DataRequired, Email, Length, EqualTo, Optional, NumberRange


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('Customer', 'Customer'), ('Courier', 'Courier'), ('Admin', 'Admin')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class ProfileUpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    phone_number = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    
    # New fields
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    region = SelectField('Region', choices=[('East', 'East'), ('West', 'West'), ('North', 'North'), ('South', 'South')], validators=[Optional()])

    # Customer-specific fields
    address = TextAreaField('Address', validators=[Length(max=250)])
    pincode = StringField('Pincode', validators=[Optional(), Length(min=6, max=10)])

    # Courier-specific fields
    vehicle_info = StringField('Vehicle Info', validators=[Length(max=250)])
    vehicle_number = StringField('Vehicle Number', validators=[Length(max=50)])

    submit = SubmitField('Update Profile')



class AdminProfileUpdateForm(FlaskForm):
    # Common fields
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    role = SelectField(
        'Role', 
        choices=[
            ('Customer', 'Customer'),
            ('Courier', 'Courier'),
            ('Admin', 'Admin')
        ], 
        validators=[DataRequired()]
    )
    
    # New fields
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    region = SelectField(
        'Region', 
        choices=[
            ('East', 'East'),
            ('West', 'West'),
            ('North', 'North'),
            ('South', 'South')
        ], 
        validators=[Optional()]
    )
    
    # Customer-specific fields
    address = TextAreaField('Address', validators=[Length(max=250)])
    pincode = StringField('Pincode', validators=[Optional(), Length(min=6, max=10)])

    # Courier-specific fields
    vehicle_info = StringField('Vehicle Info', validators=[Length(max=250)])
    vehicle_number = StringField('Vehicle Number', validators=[Length(max=50)])
    
    submit = SubmitField('Update Admin Profile')



class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=80)])
    cost_price = FloatField('Cost Price', validators=[DataRequired(), NumberRange(min=0)])
    selling_price = FloatField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    product_weight = FloatField('Product Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField('Image URL', validators=[Length(max=200)])
    category_id = SelectField('Category', coerce=int)
    submit = SubmitField('Save')
