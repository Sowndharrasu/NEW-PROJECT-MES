# Switch this project to MongoDB (works with Compass)

This project currently uses **Flask + SQLAlchemy** (relational DB). To use **MongoDB** (so you can view/manage in **MongoDB Compass**), follow these steps.
This starter shows *how* to rewire the app using **MongoEngine** (ODM for MongoDB). You still need to convert **all models & queries** in your routes.

---

## 1) Install MongoDB & Compass
- Install **MongoDB Community Server** (or use **Atlas**).
- Install **MongoDB Compass**.
- Start MongoDB locally (default: `mongodb://localhost:27017`).

## 2) Create `.env`
Copy `.env.example` to `.env` and edit:
```env
SECRET_KEY=change-me-in-prod
MONGO_URI=mongodb://localhost:27017/manufacturingdb
# For Atlas (cloud):
# MONGO_URI=mongodb+srv://<username>:<password>@<cluster>/<dbname>?retryWrites=true&w=majority
```

## 3) Install Python dependencies
```bash
pip install -r requirements_mongo.txt
```

## 4) Use the new Mongo app entry
- New files added:
  - `app_mongo.py` → Flask app wired to MongoDB
  - `models_mongo.py` → MongoEngine `Document` classes (examples: `UserDoc`, `EmployeeDoc`, `MachineDoc`)
  - `routes_mongo.py` → Example routes showing `.objects(...)` and `.save()`
  - `auth_mongo.py` → Login using `UserDoc`
  - `requirements_mongo.txt`, `.env.example`, this README

## 5) Start the app (dev)
```bash
# Linux/macOS
export FLASK_APP=app_mongo.py
flask run
# or
python app_mongo.py
```
```powershell
# Windows PowerShell
$env:FLASK_APP="app_mongo.py"
flask run
# or
python app_mongo.py
```

## 6) Verify in MongoDB Compass
- Open Compass → **New Connection**.
- Paste your `MONGO_URI` → **Connect**.
- Database `manufacturingdb` → Collections `users`, `employees`, `machines` will appear after you create data.

## 7) Refactor your code
Your original code uses SQLAlchemy (e.g., `db.session.add(...)`, `db.create_all()`, `Model.query.filter_by(...)`).
With MongoEngine:
- Create: `doc = MachineDoc(...); doc.save()`
- Read: `MachineDoc.objects(machine_code="MC-001").first()`
- Update: `m = MachineDoc.objects(id=some_id).first(); m.name = "New"; m.save()`
- Delete: `m.delete()`
- Remove `db.create_all()` — MongoDB creates collections on first write.

Replace **every** SQLAlchemy model with a corresponding `Document` class and update queries in your blueprints.

## 8) Optional: migrate existing data
- Export relational tables (CSV) and use **Compass → Import Data** into each collection.
- Or write a one-off Python script to read from old DB and `.save()` to Mongo.

## 9) Common gotchas
- IDs are `ObjectId` (strings for Flask-Login `get_id()`).
- No joins; use `ReferenceField` and fetch related docs separately.
- Transactions differ; design with document boundaries in mind.

---

### Quick sanity test
1. Run the server.
2. Hit `http://localhost:5000/auth/bootstrap-admin` once to create default admin.
3. Log in at `/auth/login` with `admin` / `admin123`.
4. `POST /machines` with JSON to create a machine, then list `/machines`.
5. Open **Compass** and verify documents are saved.