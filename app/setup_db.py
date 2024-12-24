from app import app, db  # Import the app and db from your Flask app
from models import Category, Product, User, Cart, Subscription  # Import your models
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_db():
    with app.app_context():  # Ensure the app context is active
        # Create all tables in the database
        db.create_all()

        # Add categories
        flowers = Category(
            category_name="Flowers", 
            category_description="A variety of beautiful flowers."
        )
        vegetables = Category(
            category_name="Vegetables", 
            category_description="Fresh and organic vegetables."
        )
        herbs = Category(
            category_name="Herbs", 
            category_description="Aromatic and medicinal herbs."
        )

        db.session.add_all([flowers, vegetables, herbs])
        db.session.commit()

        # Add dummy products
        dummy_products = [
            Product(
                name="Rose Plant",
                description="A beautiful red rose plant.",
                cost_price=150,
                selling_price=200,
                category_id=flowers.category_id,
                stock_quantity=50,
                product_weight=0.5,
                image_url="https://bouqs.com/blog/wp-content/uploads/2018/08/shutterstock_1662182848-min-1080x719.jpg"
            ),
            Product(
                name="Tulip Plant",
                description="Bright and colorful tulips for your garden.",
                cost_price=180,
                selling_price=230,
                category_id=flowers.category_id,
                stock_quantity=40,
                product_weight=0.4,
                image_url="https://static.wixstatic.com/media/7d9393_3bb37ec5f92445f59d49e3b6aad09f34~mv2.jpg/v1/fill/w_568,h_378,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/7d9393_3bb37ec5f92445f59d49e3b6aad09f34~mv2.jpg"
            ),
            Product(
                name="Tomato Plant",
                description="Healthy tomato plant for fresh produce.",
                cost_price=100,
                selling_price=120,
                category_id=vegetables.category_id,
                stock_quantity=30,
                product_weight=0.8,
                image_url="https://t3.ftcdn.net/jpg/02/71/63/24/360_F_271632489_iZexHnP4LtGvDD39QvklpgrgdMeGj7PH.jpg"
            ),
            Product(
                name="Cucumber Plant",
                description="Crisp cucumber plant for your kitchen garden.",
                cost_price=70,
                selling_price=90,
                category_id=vegetables.category_id,
                stock_quantity=60,
                product_weight=0.6,
                image_url="https://media.greenmatters.com/brand-img/xNJqPQnf-/0x0/cucumber-growing-in-vegetable-garden-1687980078564.jpg"
            ),
            Product(
                name="Aloe Vera",
                description="Low-maintenance aloe vera plant with medicinal properties.",
                cost_price=80,
                selling_price=110,
                category_id=herbs.category_id,
                stock_quantity=40,
                product_weight=1.2,
                image_url="https://m.media-amazon.com/images/I/81XWpVvk5AL._AC_UF1000,1000_QL80_.jpg"
            ),
            Product(
                name="Mint Plant",
                description="Fresh mint plant for your kitchen and beverages.",
                cost_price=40,
                selling_price=60,
                category_id=herbs.category_id,
                stock_quantity=70,
                product_weight=0.3,
                image_url="https://www.geturbanleaf.com/cdn/shop/articles/1008bcba2907fadf07e2f5986a9aab49.jpg?v=1704822162"
            ),
            Product(
                name="Marigold Plant",
                description="Bright yellow marigold plant to beautify your garden.",
                cost_price=50,
                selling_price=75,
                category_id=flowers.category_id,
                stock_quantity=60,
                product_weight=0.4,
                image_url="https://www.almanac.com/sites/default/files/users/AlmanacStaffArchive/marigold-field_full_width.jpg"
            ),
            Product(
                name="Spinach Plant",
                description="Nutritious and fresh spinach plant for your kitchen garden.",
                cost_price=30,
                selling_price=50,
                category_id=vegetables.category_id,
                stock_quantity=80,
                product_weight=0.3,
                image_url="https://rukminim2.flixcart.com/image/850/1000/xif0q/plant-sapling/z/s/b/annual-yes-yes-spinach-1-pot-elitegreen-original-imagjpcsgfdjmd6d.jpeg?q=90&crop=false"
            ),
            Product(
                name="Chili Plant",
                description="Hot chili plant for your spicy dishes.",
                cost_price=40,
                selling_price=60,
                category_id=vegetables.category_id,
                stock_quantity=50,
                product_weight=0.2,
                image_url="https://cdn.mos.cms.futurecdn.net/2EkmdRvyUvHJjnwrCpCToE.jpg"
            ),
            Product(
                name="Basil Plant",
                description="Fresh basil plant for cooking and medicinal uses.",
                cost_price=50,
                selling_price=75,
                category_id=herbs.category_id,
                stock_quantity=60,
                product_weight=0.3,
                image_url="https://www.marthastewart.com/thmb/w1f38EKcAYkVTe2JjqIccB7qOeY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/ms-how-to-grow-basil-69c2254cf454424fbc55992cc8155dbe.jpg"
            ),
            Product(
                name="Geranium Plant",
                description="Colorful geranium plant for brightening your garden.",
                cost_price=120,
                selling_price=160,
                category_id=flowers.category_id,
                stock_quantity=40,
                product_weight=0.5,
                image_url="https://5.imimg.com/data5/SELLER/Default/2024/7/433081468/LT/UH/XY/107425613/geranium-plant.jpg"
            ),
            Product(
                name="Cabbage Plant",
                description="Fresh cabbage plant for your kitchen garden.",
                cost_price=50,
                selling_price=80,
                category_id=vegetables.category_id,
                stock_quantity=90,
                product_weight=1.0,
                image_url="https://kellogggarden.com/wp-content/uploads/2021/03/Cabbage.jpg"
            ),
        ]

        db.session.add_all(dummy_products)
        db.session.commit()

        # Add dummy users
        dummy_users = [
            User(
                name="Admin",
                email="admin@gmail.com",
                password_hash=generate_password_hash("010203"),
                role="Admin",
                created_at=datetime.utcnow()
            ),
            User(
                name="Courier1",
                email="courier1@gmail.com",
                password_hash=generate_password_hash("010203"),
                role="Courier",
                phone_number="1234567890",
                vehicle_info="Motorcycle",
                vehicle_number="AB123CD",
                created_at=datetime.utcnow()
            ),
            User(
                name="Courier2",
                email="courier2@example.com",
                password_hash=generate_password_hash("courierpassword"),
                role="Courier",
                phone_number="1234567891",
                vehicle_info="Bicycle",
                vehicle_number="EF456GH",
                created_at=datetime.utcnow()
            ),
            User(
                name="Courier3",
                email="courier3@gmail.com",
                password_hash=generate_password_hash("010203"),
                role="Courier",
                phone_number="1234567890",
                vehicle_info="Motorcycle",
                vehicle_number="AB153CD",
                created_at=datetime.utcnow()
            ),
            User(
                name="Courier4",
                email="courier4@example.com",
                password_hash=generate_password_hash("courierpassword"),
                role="Courier",
                phone_number="1234567891",
                vehicle_info="Bicycle",
                vehicle_number="EF453GH",
                created_at=datetime.utcnow()
            ),
            User(
                name="User",
                email="user@gmail.com",
                password_hash=generate_password_hash("010203"),
                role="Customer",
                phone_number="1234567892",
                country="India",
                address="123 Main Street",
                pincode="141104",
                created_at=datetime.utcnow()
            ),
            User(
                name="Minhaj",
                email="minhajtkc@gmail.com",
                password_hash=generate_password_hash("010203"),
                role="Customer",
                phone_number="1234567893",
                country="India",
                address="456 Elm Street",
                pincode="673572",
                created_at=datetime.utcnow()
            ),
        ]

        db.session.add_all(dummy_users)
        db.session.commit()

        # Add a subscription for demonstration
        subscription = Subscription(
            user_id=1,  # Assuming the first user is valid
            endpoint="https://example.com/endpoint",
            auth="auth-token",
            p256dh="p256dh-key"
        )

        db.session.add(subscription)
        db.session.commit()

        print("Database setup complete. Categories, products, users, and subscriptions have been added.")

if __name__ == "__main__":
    setup_db()
