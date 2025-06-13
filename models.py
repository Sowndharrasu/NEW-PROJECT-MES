from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Operator')  # Admin, Manager, Operator, Storekeeper
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        return self.role == role
    
    def __repr__(self):
        return f'<User {self.username}>'


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    hire_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Employee {self.name}>'


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    machine_type = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(50))
    capacity = db.Column(db.String(50))
    location = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Machine {self.name}>'


class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    tool_type = db.Column(db.String(50), nullable=False)
    specification = db.Column(db.Text)
    quantity_available = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2))
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tool {self.name}>'


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Customer {self.name}>'


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vendor {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_of_measure = db.Column(db.String(20), nullable=False)
    standard_price = db.Column(db.Numeric(10, 2))
    product_type = db.Column(db.String(50))  # Raw Material, Finished Goods, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'


class RawMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_of_measure = db.Column(db.String(20), nullable=False)
    current_stock = db.Column(db.Numeric(10, 3), default=0)
    minimum_stock = db.Column(db.Numeric(10, 3), default=0)
    unit_price = db.Column(db.Numeric(10, 2))
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RawMaterial {self.name}>'


class GoodsReceiptNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(20), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    invoice_number = db.Column(db.String(50))
    total_amount = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    received_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendor = db.relationship('Vendor', backref='grns')
    received_by_user = db.relationship('User', backref='grns_received')
    
    def __repr__(self):
        return f'<GRN {self.grn_number}>'


class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_order_number = db.Column(db.String(20), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_ordered = db.Column(db.Numeric(10, 3), nullable=False)
    quantity_produced = db.Column(db.Numeric(10, 3), default=0)
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High, Urgent
    status = db.Column(db.String(20), default='Created')  # Created, Scheduled, In Progress, Completed, Cancelled
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='work_orders')
    created_by_user = db.relationship('User', backref='work_orders_created')
    
    def __repr__(self):
        return f'<WorkOrder {self.work_order_number}>'


class JobCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_card_number = db.Column(db.String(20), unique=True, nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    operation_description = db.Column(db.Text, nullable=False)
    standard_time = db.Column(db.Numeric(5, 2))  # in hours
    actual_time = db.Column(db.Numeric(5, 2))
    quantity_completed = db.Column(db.Numeric(10, 3), default=0)
    status = db.Column(db.String(20), default='Assigned')  # Assigned, In Progress, Completed, On Hold
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    work_order = db.relationship('WorkOrder', backref='job_cards')
    machine = db.relationship('Machine', backref='job_cards')
    operator = db.relationship('Employee', backref='job_cards')
    
    def __repr__(self):
        return f'<JobCard {self.job_card_number}>'


class QualityInspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspection_number = db.Column(db.String(20), unique=True, nullable=False)
    inspection_type = db.Column(db.String(50), nullable=False)  # Incoming, In-Process, Final
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_inspected = db.Column(db.Numeric(10, 3), nullable=False)
    quantity_accepted = db.Column(db.Numeric(10, 3), default=0)
    quantity_rejected = db.Column(db.Numeric(10, 3), default=0)
    inspector_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Passed, Failed
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    work_order = db.relationship('WorkOrder', backref='inspections')
    product = db.relationship('Product', backref='inspections')
    inspector = db.relationship('Employee', backref='inspections')
    
    def __repr__(self):
        return f'<QualityInspection {self.inspection_number}>'


class ToolIssuance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_number = db.Column(db.String(20), unique=True, nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'))
    quantity_issued = db.Column(db.Integer, nullable=False)
    quantity_returned = db.Column(db.Integer, default=0)
    issue_date = db.Column(db.Date, nullable=False)
    expected_return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Issued')  # Issued, Partially Returned, Fully Returned
    issued_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tool = db.relationship('Tool', backref='issuances')
    employee = db.relationship('Employee', backref='tool_issuances')
    work_order = db.relationship('WorkOrder', backref='tool_issuances')
    issued_by_user = db.relationship('User', backref='tool_issuances')
    
    def __repr__(self):
        return f'<ToolIssuance {self.issue_number}>'


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(20), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    po_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date)
    total_amount = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), default='Draft')  # Draft, Sent, Acknowledged, Delivered, Closed
    terms_and_conditions = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendor = db.relationship('Vendor', backref='purchase_orders')
    created_by_user = db.relationship('User', backref='purchase_orders_created')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'


class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date)
    total_amount = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), default='Draft')  # Draft, Confirmed, In Production, Dispatched, Delivered
    priority = db.Column(db.String(20), default='Normal')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='sales_orders')
    created_by_user = db.relationship('User', backref='sales_orders_created')
    
    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'
