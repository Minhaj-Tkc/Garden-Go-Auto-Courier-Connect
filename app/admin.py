import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Category, db, User, Product, Order

from forms import RegistrationForm, AdminProfileUpdateForm, ProductForm
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    user_count = User.query.count()
    product_count = Product.query.count()
    order_count = Order.query.count()
    return render_template('admin/admin_dashboard.html', user_count=user_count, product_count=product_count, order_count=order_count)


# Route to list users
@admin_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    customers = User.query.filter_by(role="Customer").all()
    couriers = User.query.filter_by(role="Courier").all()
    return render_template('admin/users.html', customers=customers, couriers=couriers)

# Route to create a new user
@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully!", "success")
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_form.html', form=form, action="Create")

# Route to update a user
@admin_bp.route('/users/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminProfileUpdateForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.role = form.name.data
        user.phone_number = form.phone_number.data
        user.country = form.country.data
        user.region = form.region.data
        user.address = form.address.data
        user.pincode = form.pincode.data
        user.vehicle_info = form.vehicle_info.data
        user.vehicle_number = form.vehicle_number.data
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for('admin.list_users'))

    return render_template('admin/user_form.html', form=form, action="Update")

# Route to delete a user
@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin.list_users'))




@admin_bp.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/manage_products.html', products=products, categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        product_name = request.form['name']
        description = request.form['description']
        cost_price = float(request.form['cost_price'])
        selling_price = float(request.form['selling_price'])
        product_weight = float(request.form['product_weight'])
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
            cost_price=cost_price,
            selling_price=selling_price,
            product_weight=product_weight,
            stock_quantity=stock_quantity,
            category_id=category_id,
            image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.list_products'))

    categories = Category.query.all()
    return render_template('admin/add_edit_product.html', categories=categories)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if current_user.role != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.cost_price = float(request.form['cost_price'])
        product.selling_price = float(request.form['selling_price'])
        product.product_weight = float(request.form['product_weight'])
        product.stock_quantity = int(request.form['quantity'])
        product.category_id = int(request.form['category'])

        image_option = request.form.get('image_option')
        if image_option == 'url':
            product.image_url = request.form['image_url']
        elif image_option == 'file' and 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file.filename != '':
                image_path = os.path.join('static/uploads', image_file.filename)
                image_file.save(image_path)
                product.image_url = image_path

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.list_products'))

    categories = Category.query.all()
    return render_template('admin/add_edit_product.html', product=product, categories=categories, edit=True)


# @admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
# def edit_product(product_id):
#     product = Product.query.get_or_404(product_id)
#     form = ProductForm(obj=product)
#     if form.validate_on_submit():
#         product.name = form.name.data
#         product.cost_price = form.cost_price.data
#         product.selling_price = form.selling_price.data
#         product.description = form.description.data
#         product.stock_quantity = form.stock_quantity.data
#         product.image_url = form.image_url.data
#         product.product_weight = form.product_weight.data
#         product.category_id = form.category_id.data
#         db.session.commit()
#         flash('Product updated successfully!', 'success')
#         return redirect(url_for('list_products'))
#     return render_template('edit_product.html', form=form, product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.list_products'))


@admin_bp.route('/orders')
def manage_orders():
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/analytics')
def analytics():
    # Add any logic for analytics or load a static page.
    return render_template('admin/analytics.html')

