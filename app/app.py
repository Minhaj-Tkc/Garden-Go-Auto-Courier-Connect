import random
from flask import Flask, jsonify, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Category, Product, Cart, CartItem, Order, OrderItem
from forms import RegistrationForm, LoginForm, ProfileUpdateForm
import os
import requests

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


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    print(product)

    # Get the quantity from the form
    quantity = int(request.form['quantity'])

    # Get or create the cart
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart:
        cart = Cart(user_id=current_user.user_id)
        db.session.add(cart)
        db.session.commit()

    # Check if the product is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product.product_id).first()
    if cart_item:
        cart_item.quantity += quantity  # Update the quantity by the user-selected amount
        toast_message = f'Added {quantity} more {product.name} to your cart!'
    else:
        cart_item = CartItem(cart_id=cart.cart_id, product_id=product.product_id, quantity=quantity)
        db.session.add(cart_item)
        toast_message = f'{product.name} added to your cart!'

    db.session.commit()

    # Use the toaster-specific flash
    flash(toast_message, 'success')  # Success indicates the type for the toaster
    return redirect(url_for('show_products'))

def calculate_shipping_cost(pincode, total_weight, country):
    fixed_rate_for_outside_india = 500  # Fixed rate for countries outside India
    base_shipping_cost = 20  # Base cost for nearby locations

    # If the country is not India, return the fixed rate
    if country.lower() != 'india':
        return fixed_rate_for_outside_india

    # For locations within India, calculate cost based on distance using pincode
    outlet_pincode = '673001'  # Kozhikode, Kerala pincode

    # Using Google Maps Distance Matrix API
    try:
        api_key = "AIzaSyAv44pEZqLcd3Tck0ppI4TgTsAVetKeVfc"  
        response = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins": outlet_pincode,
                "destinations": pincode,
                "key": api_key,
            }
        )
        response.raise_for_status()
        distance_info = response.json()
        rows = distance_info.get('rows', [])
        elements = rows[0].get('elements', []) if rows else []
        distance = elements[0].get('distance', {}).get('value', 0) / 1000  # Convert meters to kilometers
    except Exception as e:
        flash(f"Could not calculate shipping cost: {e}", 'warning')
        return base_shipping_cost  # Fallback to base cost

    # Distance-based charges
    if distance <= 200:
        distance_cost = 20  # Nearby locations
    elif distance <= 500:
        distance_cost = 50  # Medium range
    else:
        distance_cost = 100  # Long-distance

    # Weight-based charges
    if total_weight <= 2:
        weight_cost = 20  # Flat rate for up to 2 kg
    else:
        weight_cost = 20 + (10 * (total_weight - 2))  # ₹10 per kg for additional weight

    # Calculate total shipping cost
    shipping_cost = base_shipping_cost + weight_cost + distance_cost
    return shipping_cost




@app.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart or not cart.cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('show_products'))

    # Get all cart items
    cart_items = CartItem.query.filter_by(cart_id=cart.cart_id).all()

    # Calculate total price (sum of quantity * price per product)
    total_price = sum(item.quantity * item.product.selling_price for item in cart_items)

    # Calculate total weight of all cart items
    total_weight = sum(item.product.product_weight * item.quantity for item in cart_items)

    # Calculate shipping cost
    try:
        total_shipping_cost = calculate_shipping_cost(
            pincode=current_user.pincode,
            total_weight=total_weight,
            country=current_user.country
        )
    except Exception as e:
        flash("Shipping cost could not be calculated. Please check your details.", "danger")
        total_shipping_cost = 0

    # Total price including shipping
    total_price_with_shipping = total_price + total_shipping_cost

    return render_template(
        'cart.html',
        user=current_user,
        cart_items=cart_items,
        total_price=total_price,
        total_weight=total_weight,
        shipping_cost=total_shipping_cost,
        total_price_with_shipping=total_price_with_shipping
    )




@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.user_id:
        return jsonify({"success": False, "error": "Unauthorized action."}), 403

    try:
        new_quantity = int(request.form.get('quantity', 1))
        if new_quantity < 1:
            db.session.delete(cart_item)
            message = "Item removed from cart."
        else:
            cart_item.quantity = new_quantity
            message = "Cart updated."

        db.session.commit()
        return jsonify({"success": True, "message": message})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.user_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('view_cart'))

    product_name = cart_item.product.name

    db.session.delete(cart_item)
    db.session.commit()
    flash(f'{product_name} removed from your cart.', 'info')
    return redirect(url_for('view_cart'))




@app.route('/cart_summary', methods=['POST'])
@login_required
def cart_summary():
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart or not cart.cart_items:
        return jsonify({'success': False, 'error': 'Cart is empty.'}), 400

    cart_items = CartItem.query.filter_by(cart_id=cart.cart_id).all()

    # Calculate total price and weight
    total_price = sum(item.quantity * item.product.selling_price for item in cart_items)
    total_weight = sum(item.product.product_weight * item.quantity for item in cart_items)

    # Calculate shipping cost
    try:
        shipping_cost = calculate_shipping_cost(
            pincode=current_user.pincode,
            total_weight=total_weight,
            country=current_user.country
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    # Calculate total price with shipping
    total_price_with_shipping = total_price + shipping_cost

    return jsonify({
        'success': True,
        'subtotal': round(total_price, 2),
        'total_weight': round(total_weight, 2),
        'shipping_cost': round(shipping_cost, 2),
        'total_price_with_shipping': round(total_price_with_shipping, 2),
    })




@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart or not cart.cart_items:
        flash('Your cart is empty. Add some products before checking out.', 'info')
        return redirect(url_for('show_products'))

    # Check for product availability in stock and purchase limit
    for cart_item in cart.cart_items:
        product = cart_item.product
        if cart_item.quantity > product.stock_quantity:
            flash(f'Not enough stock for {product.name}. Available stock: {product.stock_quantity}.', 'info')
            return redirect(url_for('view_cart'))
        elif cart_item.quantity > 10:
            flash(f'You cannot purchase more than 10 of {product.name}.', 'info')
            return redirect(url_for('view_cart'))

    # Calculate total weight for the cart
    total_weight = sum(item.product.product_weight * item.quantity for item in cart.cart_items)

    # Calculate shipping cost based on total weight
    shipping_cost = calculate_shipping_cost(
        pincode=current_user.pincode,
        total_weight=total_weight,
        country=current_user.country
    )

    # Assign courier
    couriers = User.query.filter_by(role='Courier').all()
    print(couriers)
    if not couriers:
        flash('No couriers are available at the moment. Please try again later.', 'danger')
        return redirect(url_for('view_cart'))
    assigned_courier = random.choice(couriers)

    # Create the order
    total_price = sum(item.quantity * item.product.selling_price for item in cart.cart_items)
    order = Order(
        user_id=current_user.user_id,
        total_price=total_price,
        status='Pending',
        assigned_to=assigned_courier.user_id,  # Randomly assigned courier
        address=current_user.address,
        pincode=current_user.pincode,
        shipping_cost=shipping_cost,
        estimated_delivery=datetime.utcnow() + timedelta(days=5)  # Estimated delivery in 5 days
    )
    db.session.add(order)
    db.session.commit()

    # Add items to the order and update stock
    for cart_item in cart.cart_items:
        # Update product stock
        product = cart_item.product
        product.stock_quantity -= cart_item.quantity

        # Add order items
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.session.add(order_item)
        db.session.delete(cart_item)  # Remove the item from the cart

    # Empty the cart after checkout
    db.session.commit()

    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('order_details', order_id=order.order_id))




@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id:
        flash('Unauthorized access to this order.', 'danger')
        return redirect(url_for('login'))

    return render_template('order_details.html', order=order)





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
