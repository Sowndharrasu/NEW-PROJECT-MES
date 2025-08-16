from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from mongoengine import (
    Document, StringField, EmailField, BooleanField, DateTimeField,
    IntField, FloatField, ReferenceField
)

# ==========================
# USER & AUTHENTICATION
# ==========================
class UserDoc(UserMixin, Document):
    username = StringField(required=True, unique=True, max_length=80)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(default="Operator", max_length=50)  # Admin, Manager, Operator, Storekeeper
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "users", "indexes": ["username", "email"]}

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return str(self.id)

    def __str__(self):
        return self.username


# ==========================
# MASTER DATA
# ==========================
class DepartmentDoc(Document):
    name = StringField(required=True, unique=True, max_length=100)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "departments", "indexes": ["name"]}

    def __str__(self):
        return self.name


class UnitDoc(Document):
    name = StringField(required=True, unique=True, max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "units", "indexes": ["name"]}

    def __str__(self):
        return self.name


class EmployeeDoc(Document):
    code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    phone = StringField(max_length=20)
    email = EmailField()
    department = ReferenceField(DepartmentDoc)  # matches department_id in forms.py
    join_date = DateTimeField()
    role = StringField(default="Operator", max_length=50)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "employees", "indexes": ["code", "name"]}

    def __str__(self):
        return self.name


class MachineDoc(Document):
    machine_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    department = ReferenceField(DepartmentDoc)  # department_id in forms.py
    purchase_date = DateTimeField()
    machine_type = StringField(required=True, max_length=50)
    manufacturer = StringField(max_length=100)
    model = StringField(max_length=50)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "machines", "indexes": ["machine_code", "name"]}

    def __str__(self):
        return self.name


class InventoryItemDoc(Document):
    code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    description = StringField()
    quantity = FloatField(default=0)
    unit = ReferenceField(UnitDoc)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "inventory_items", "indexes": ["code", "name"]}

    def __str__(self):
        return self.name


# ==========================
# PRODUCTION
# ==========================
class WorkOrderDoc(Document):
    work_order_number = StringField(required=True, unique=True, max_length=50)
    item = ReferenceField(InventoryItemDoc)
    quantity = FloatField(required=True)
    unit = ReferenceField(UnitDoc)
    start_date = DateTimeField()
    due_date = DateTimeField()
    status = StringField(default="Pending", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "work_orders", "indexes": ["work_order_number", "status"]}

    def __str__(self):
        return self.work_order_number


class ProductionEntryDoc(Document):
    work_order = ReferenceField(WorkOrderDoc)
    machine = ReferenceField(MachineDoc)
    operator = ReferenceField(EmployeeDoc)
    date = DateTimeField()
    shift = StringField(max_length=20)
    quantity_produced = FloatField()
    unit = ReferenceField(UnitDoc)
    remarks = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "production_entries", "indexes": ["date", "shift"]}

    def __str__(self):
        return f"{self.work_order} - {self.date}"


# ==========================
# MATERIALS & MAINTENANCE
# ==========================
class MaterialIssueDoc(Document):
    work_order = ReferenceField(WorkOrderDoc)
    item = ReferenceField(InventoryItemDoc)
    quantity = FloatField(required=True)
    unit = ReferenceField(UnitDoc)
    issued_to = ReferenceField(EmployeeDoc)
    date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "material_issues", "indexes": ["date"]}

    def __str__(self):
        return f"{self.item} - {self.quantity}"


class MaintenanceLogDoc(Document):
    machine = ReferenceField(MachineDoc)
    maintenance_date = DateTimeField()
    maintenance_type = StringField(max_length=50)  # Preventive / Breakdown
    remarks = StringField()
    performed_by = ReferenceField(EmployeeDoc)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "maintenance_logs", "indexes": ["maintenance_date", "maintenance_type"]}

    def __str__(self):
        return f"{self.machine} - {self.maintenance_type}"


# ==========================
# PURCHASES
# ==========================
class PurchaseOrderDoc(Document):
    po_number = StringField(required=True, unique=True, max_length=50)
    supplier_name = StringField(required=True, max_length=100)
    item = ReferenceField(InventoryItemDoc)
    quantity = FloatField(required=True)
    unit = ReferenceField(UnitDoc)
    order_date = DateTimeField()
    expected_date = DateTimeField()
    status = StringField(default="Pending", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "purchase_orders", "indexes": ["po_number", "status"]}

    def __str__(self):
        return self.po_number
    

# ==========================
# CUSTOMERS
# ==========================
class CustomerDoc(Document):
    customer_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    contact_person = StringField(max_length=100)
    phone = StringField(max_length=20)
    email = EmailField()
    address = StringField()
    city = StringField(max_length=50)
    state = StringField(max_length=50)
    country = StringField(max_length=50)
    postal_code = StringField(max_length=20)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "customers", "indexes": ["customer_code", "name"]}

    def __str__(self):
        return self.name

