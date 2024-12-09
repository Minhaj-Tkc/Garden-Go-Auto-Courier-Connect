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


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_profile(user_id):
    user = User.query.get_or_404(user_id)

    if user != current_user and not current_user.is_admin:
        flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('home'))

    form = ProfileUpdateForm(obj=user)

    if form.validate_on_submit():
        try:
            user.name = form.name.data
            user.phone = form.phone.data
            if user.role == 'Customer':
                user.address = form.address.data
                user.pincode = form.pincode.data
            elif user.role == 'Courier':
                user.vehicle_info = form.vehicle_info.data
                user.vehicle_number = form.vehicle_number.data

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('update_profile', user_id=user_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('profile.html', form=form, user=user)

# @app.route('/products')
# def products():
#     products = Product.query.all()
#     return render_template("products.html", products=products)

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template("products.html", products=products, user=current_user)



@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/admin_products_page')
@login_required
def view_products():
    if current_user.role != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    categories = Category.query.all()
    category_dict = {}

    for category in categories:
        category_dict[category.category_Name] = [
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'stock_quantity': product.stock_quantity,
                'image_url': product.image_url
            } for product in category.products
        ]

    return render_template('admin_dashboard.html', categories=category_dict)


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        product_name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock_quantity = int(request.form['quantity'])
        category_id = int(request.form['category'])

        image_option = request.form.get('image_option')
        image_url = None

        if image_option == 'url':
            image_url = request.form['image_url']
        elif image_option == 'file' and 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file.filename != '':
                image_path = os.path.join('static/uploads', image_file.filename)
                image_file.save(image_path)
                image_url = image_path

        new_product = Product(
            name=product_name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id,
            image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('view_products'))

    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    return "Reset Password Page"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html')


@app.route('/courier_dashboard')
@login_required
def courier_dashboard():
    if current_user.role != 'Courier':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('courier_dashboard.html')


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

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('products'))

@app.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('products'))

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('view_cart'))

    new_quantity = int(request.form.get('quantity', 1))
    if new_quantity < 1:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    else:
        cart_item.quantity = new_quantity
        flash('Cart updated.', 'success')

    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('view_cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.cart_items:
        flash('Your cart is empty. Add some products before checking out.', 'info')
        return redirect(url_for('products'))

    # Create the order
    total_price = sum(item.quantity * item.product.price for item in cart.cart_items)
    order = Order(user_id=current_user.id, total_price=total_price, status='Pending')
    db.session.add(order)
    db.session.commit()

    # Add items to the order
    for cart_item in cart.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.session.add(order_item)
        db.session.delete(cart_item)  # Remove the item from the cart

    # Empty the cart after checkout
    db.session.commit()

    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('order_summary', order_id=order.id))


@app.route('/order/<int:order_id>')
@login_required
def order_summary(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access to this order.', 'danger')
        return redirect(url_for('products'))

    return render_template('order_summary.html', order=order)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
