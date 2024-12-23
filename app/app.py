from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User, Category, Product, Cart, CartItem, Order, OrderItem
from forms import RegistrationForm, LoginForm, ProfileUpdateForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///garden_go.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def update_last_login():
    if current_user.is_authenticated:
        current_user.last_login = datetime.utcnow()
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')

            # Redirect based on user role
            if user.role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'Courier':
                return redirect(url_for('courier_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)



@app.route('/products')
def products():
    # products = Product.query.all()
    products = "Products"
    return render_template("products.html", products=products, user=current_user)



@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    return "Reset Password Page"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))







if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
