from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User
from forms import RegistrationForm, LoginForm, ProfileUpdateForm


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
    # Fetch the user from the database
    user = User.query.get_or_404(user_id)

    # Ensure only the current user or admin can update
    if user != current_user and not current_user.is_admin:
        flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('home'))

    form = ProfileUpdateForm(obj=user)  # Pre-fill form fields with user data
    
    print("Form validation:", form.validate_on_submit())
    print("Form errors:", form.errors)

    # Handle form submission
    if form.validate_on_submit():
        try:
            # Update fields based on user role
            user.name = form.name.data
            user.phone = form.phone.data
            if user.role == 'Customer':
                user.address = form.address.data
                user.pincode = form.pincode.data
            elif user.role == 'Courier':
                user.vehicle_info = form.vehicle_info.data
                user.vehicle_number = form.vehicle_number.data

            # Save changes
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('update_profile', user_id=user_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {e}")
            flash('An error occurred. Please try again.', 'danger')

    return render_template('profile.html', form=form, user=user)







@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Logic to handle password reset
    return "Reset Password Page"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)
