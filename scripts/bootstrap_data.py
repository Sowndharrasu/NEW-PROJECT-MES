import os
from mongoengine import connect, disconnect, get_db
from models_mongo import UserDoc



def bootstrap_data():
    connect('mes_db', host=os.getenv('MONGO_URI', 'mongodb://localhost:27017/mes_db'))

    print("Connected to MongoDB for bootstrapping data.")

    # Print All collection
    db = get_db()

    collections = db.list_collection_names()
    print("Collections in the database:")

    for collection in collections:
        n_docs = db[collection].count_documents({})

        print(f"- {collection} ({n_docs} documents)")

    # Create default users
    user_to_be_created = [
        {
            "username": "admin",
            "email": "admin@admin.com",
            "password": "admin123",
            "role": "Admin",
            "is_active": True
        },
        {
            "username": "manager",
            "email": "manager@manager.com",
            "password": "manager123",
            "role": "Manager",
            "is_active": True
        },
        {
            "username": "operator",
            "email": "operator@operator.com",
            "password": "operator123",
        },
        {
            "username": "storekeeper",
            "email": "storekeeper@storekeeper.com",
            "password": "storekeeper123",
        }
    ]

    for user in user_to_be_created:
        existing_user = db.users.find_one({"username": user["username"]})
        if not existing_user:
            userDoc = UserDoc(
                username=user["username"],
                email=user["email"],
                role=user.get("role", "Operator"),
                is_active=user.get("is_active", True)
            )

            userDoc.set_password(user["password"])

            userDoc.save()
            print(f"✅ Created user: {user['username']}")

    disconnect()
    print("Disconnected from MongoDB.")



if __name__ == "__main__":
    bootstrap_data()
