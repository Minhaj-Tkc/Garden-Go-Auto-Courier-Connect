from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_updated_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    address = db.Column(db.String(300))
    phone_number = db.Column(db.String(15))
    pincode = db.Column(db.String(10))
    region = db.Column(db.String(50))
    country = db.Column(db.String(50))
    vehicle_info = db.Column(db.String(150))
    vehicle_number = db.Column(db.String(50))

    # Relationships
    orders = db.relationship('Order', foreign_keys='Order.user_id', back_populates='user')  # Updated
    assigned_orders = db.relationship('Order', foreign_keys='Order.assigned_to', back_populates='assigned_user')  # New relationship
    carts = db.relationship('Cart', back_populates='user')
    password_resets = db.relationship('PasswordReset', back_populates='user')
    subscriptions = db.relationship('Subscription', back_populates='user')

    # Password utilities
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)

class PasswordReset(db.Model):
    __tablename__ = 'passwordreset'
    passwordreset_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ptoken = db.Column(db.String(256), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='password_resets')

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='carts')
    cart_items = db.relationship('CartItem', back_populates='cart')

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)

    cart = db.relationship('Cart', back_populates='cart_items')
    product = db.relationship('Product', back_populates='cart_items')

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String)
    stock_quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String)
    product_weight = db.Column(db.Float, nullable=False)  # New attribute
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))

    category = db.relationship('Category', back_populates='products')
    cart_items = db.relationship('CartItem', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    category_description = db.Column(db.String)

    products = db.relationship('Product', back_populates='category')

class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # New attribute
    status = db.Column(db.String, nullable=False)
    address = db.Column(db.String(300))
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    pincode = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='orders')  # Updated
    assigned_user = db.relationship('User', foreign_keys=[assigned_to], back_populates='assigned_orders')  # New relationship
    order_items = db.relationship('OrderItem', back_populates='order')
    audit_logs = db.relationship('Audit', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Audit(db.Model):
    __tablename__ = 'audit'
    record_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    status = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.String, nullable=False)
    reason = db.Column(db.String)

    order = db.relationship('Order', back_populates='audit_logs')

class Subscription(db.Model):
    __tablename__ = 'subscription'
    subscription_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    endpoint = db.Column(db.String, nullable=False)
    auth = db.Column(db.String, nullable=False)
    p256dh = db.Column(db.String, nullable=False)

    user = db.relationship('User', back_populates='subscriptions')
