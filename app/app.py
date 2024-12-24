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
                return redirect(url_for('home'))

        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_profile(user_id):
    user = User.query.get_or_404(user_id)

    if user != current_user and not current_user.is_admin:
        flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('home'))

    form = ProfileUpdateForm(obj=user)
    # Get the referrer URL
    referrer = request.args.get('next', request.referrer)
    if form.validate_on_submit():
        try:
            # Update common fields
            user.name = form.name.data
            user.phone_number = form.phone_number.data

            # Update role-specific fields
            if user.role == 'Customer':
                user.address = form.address.data
                user.pincode = form.pincode.data
                user.country = form.country.data
                user.region = form.region.data
            elif user.role == 'Courier':
                user.vehicle_info = form.vehicle_info.data
                user.vehicle_number = form.vehicle_number.data

            # Update the profile_updated_at field
            user.profile_updated_at = datetime.utcnow()

            db.session.commit()
            flash('Profile updated successfully!', 'success')

            # Redirect to the previous page if referrer is available, otherwise to the home page
            return redirect(referrer or url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    return render_template('edit_profile.html', form=form, user=user, next=referrer)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Customer':
        return render_template('customer_dashboard.html')
    elif current_user.role == 'Courier':
        return redirect(url_for('courier_dashboard'))
    elif current_user.role == 'Admin':
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Unknown role.', 'danger')
        return redirect(url_for('logout'))


@app.route('/show_products', methods=['GET'])
def show_products():
    category_name = request.args.get('category')
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by', 'name')

    products_query = Product.query

    if category_name:
        products_query = products_query.join(Category).filter(Category.category_name == category_name)

    if search_query:
        products_query = products_query.filter(
            Product.name.ilike(f"%{search_query}%") |
            Product.description.ilike(f"%{search_query}%")
        )

    if sort_by == 'price':
        products_query = products_query.order_by(Product.selling_price)
    elif sort_by == 'weight':
        products_query = products_query.order_by(Product.product_weight)
    else:
        products_query = products_query.order_by(Product.name)

    products = products_query.all()
    categories = Category.query.with_entities(Category.category_name).distinct()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check for AJAX
        return render_template('partials/product_grid.html', products=products, search_query=search_query)

    return render_template('products.html', products=products, categories=categories, user=current_user)

@app.route('/product/<int:product_id>', methods=['GET'])
def product_details(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch product by ID or return 404
    return render_template('product_details.html', product=product, user=current_user)

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
