from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from mongoengine import (
    Document, StringField, EmailField, BooleanField, DateTimeField,
    FloatField, ReferenceField, IntField
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
    capacity = StringField(max_length=50)
    location = StringField(max_length=100)
    installation_date = DateTimeField()
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
    current_stock = FloatField(default=0)
    minimum_stock = FloatField(default=0)
    unit_price = FloatField()
    location = StringField(max_length=100)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "inventory_items", "indexes": ["code", "name"]}

    def __str__(self):
        return self.name


class CustomerDoc(Document):
    customer_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    contact_person = StringField(max_length=100)
    phone = StringField(max_length=20)
    email = EmailField()
    address = StringField()
    city = StringField(max_length=50)
    state = StringField(max_length=50)
    country = StringField(max_length=50, default="India")
    postal_code = StringField(max_length=10)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "customers", "indexes": ["customer_code", "name"]}

    def __str__(self):
        return self.name


class VendorDoc(Document):
    vendor_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    contact_person = StringField(max_length=100)
    phone = StringField(max_length=20)
    email = EmailField()
    address = StringField()
    city = StringField(max_length=50)
    state = StringField(max_length=50)
    country = StringField(max_length=50, default="India")
    postal_code = StringField(max_length=10)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "vendors", "indexes": ["vendor_code", "name"]}

    def __str__(self):
        return self.name


class ToolDoc(Document):
    tool_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    tool_type = StringField(required=True, max_length=50)
    specification = StringField()
    quantity_available = IntField(default=0)
    minimum_stock = IntField(default=1)
    unit_price = FloatField()
    location = StringField(max_length=100)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "tools", "indexes": ["tool_code", "name"]}

    def __str__(self):
        return self.name


class ProductDoc(Document):
    product_code = StringField(required=True, unique=True, max_length=20)
    name = StringField(required=True, max_length=100)
    description = StringField()
    unit_of_measure = StringField(required=True, max_length=10)
    standard_price = FloatField()
    product_type = StringField(max_length=50)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "products", "indexes": ["product_code", "name"]}

    def __str__(self):
        return self.name


# ==========================
# PRODUCTION
# ==========================
class WorkOrderDoc(Document):
    work_order_number = StringField(required=True, unique=True, max_length=50)
    item = ReferenceField(InventoryItemDoc)
    product = ReferenceField(ProductDoc)  # Alternative reference for products
    quantity = FloatField(required=True)
    quantity_ordered = FloatField()  # Alternative field name used in templates
    quantity_produced = FloatField(default=0)
    unit = ReferenceField(UnitDoc)
    start_date = DateTimeField()
    due_date = DateTimeField()
    planned_start_date = DateTimeField()
    planned_end_date = DateTimeField()
    priority = StringField(default="Normal", max_length=20)
    status = StringField(default="Pending", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "work_orders", "indexes": ["work_order_number", "status"]}

    def __str__(self):
        return self.work_order_number


class JobCardDoc(Document):
    job_card_number = StringField(required=True, unique=True, max_length=50)
    work_order = ReferenceField(WorkOrderDoc)
    machine = ReferenceField(MachineDoc)
    operator = ReferenceField(EmployeeDoc)
    operation_description = StringField(required=True)
    standard_time = FloatField()
    actual_time = FloatField()
    quantity_completed = IntField(default=0)
    status = StringField(default="Assigned", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "job_cards", "indexes": ["job_card_number", "status"]}

    def __str__(self):
        return self.job_card_number


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
# QUALITY CONTROL
# ==========================
class InspectionDoc(Document):
    inspection_number = StringField(required=True, unique=True, max_length=50)
    inspection_type = StringField(required=True, max_length=50)
    product = ReferenceField(ProductDoc)
    work_order = ReferenceField(WorkOrderDoc)
    quantity_inspected = FloatField(required=True)
    quantity_accepted = FloatField(default=0)
    quantity_rejected = FloatField(default=0)
    inspector = ReferenceField(EmployeeDoc)
    inspection_date = DateTimeField()
    status = StringField(default="Pending", max_length=50)
    remarks = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "inspections", "indexes": ["inspection_number", "status"]}

    def __str__(self):
        return self.inspection_number


# ==========================
# TOOL ROOM MANAGEMENT
# ==========================
class ToolIssuanceDoc(Document):
    issue_number = StringField(required=True, unique=True, max_length=50)
    tool = ReferenceField(ToolDoc)
    employee = ReferenceField(EmployeeDoc)
    work_order = ReferenceField(WorkOrderDoc)
    quantity_issued = IntField(required=True)
    quantity_returned = IntField(default=0)
    issue_date = DateTimeField()
    expected_return_date = DateTimeField()
    actual_return_date = DateTimeField()
    status = StringField(default="Issued", max_length=50)  # Issued, Partially Returned, Fully Returned
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "tool_issuances", "indexes": ["issue_number", "status"]}

    def __str__(self):
        return self.issue_number


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
# PURCHASES & INVENTORY
# ==========================
class PurchaseOrderDoc(Document):
    po_number = StringField(required=True, unique=True, max_length=50)
    supplier_name = StringField(required=True, max_length=100)
    vendor = ReferenceField(VendorDoc)  # Reference to vendor
    item = ReferenceField(InventoryItemDoc)
    quantity = FloatField(required=True)
    unit = ReferenceField(UnitDoc)
    order_date = DateTimeField()
    expected_date = DateTimeField()
    po_date = DateTimeField()  # Alternative field name
    delivery_date = DateTimeField()  # Alternative field name
    total_amount = FloatField()
    terms_and_conditions = StringField()
    status = StringField(default="Pending", max_length=50)
    created_by_user = ReferenceField(UserDoc)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "purchase_orders", "indexes": ["po_number", "status"]}

    def __str__(self):
        return self.po_number


class GRNDoc(Document):
    grn_number = StringField(required=True, unique=True, max_length=50)
    vendor = ReferenceField(VendorDoc)
    received_date = DateTimeField()
    invoice_number = StringField(max_length=50)
    total_amount = FloatField()
    status = StringField(default="Received", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "grns", "indexes": ["grn_number", "status"]}

    def __str__(self):
        return self.grn_number


# ==========================
# SALES
# ==========================
class SalesOrderDoc(Document):
    order_number = StringField(required=True, unique=True, max_length=50)
    customer = ReferenceField(CustomerDoc)
    order_date = DateTimeField()
    delivery_date = DateTimeField()
    total_amount = FloatField()
    priority = StringField(default="Normal", max_length=20)
    status = StringField(default="Draft", max_length=50)
    created_by_user = ReferenceField(UserDoc)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "sales_orders", "indexes": ["order_number", "status"]}

    def __str__(self):
        return self.order_number
