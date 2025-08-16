import os
from datetime import timedelta

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from mongoengine import connect

# Load environment variables from .env
load_dotenv()

# MongoDB URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/manufacturingdb")

# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-prod")
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)

# Connect to MongoDB
try:
    connect(host=MONGO_URI)
    print(f"✅ Connected to MongoDB at {MONGO_URI}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

# Models import (MongoEngine)
from models_mongo import UserDoc  # noqa: E402

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return UserDoc.objects(id=user_id).first()
    except Exception as e:
        print(f"⚠ Error loading user: {e}")
        return None

# Blueprints import
from routes_mongo import main_bp  # noqa: E402
from auth_mongo import auth_bp    # noqa: E402

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
