from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
from models import User, Employee, Machine, Tool, Customer, Vendor, Product


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])


class EmployeeForm(FlaskForm):
    employee_code = StringField('Employee Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    department = StringField('Department', validators=[DataRequired(), Length(max=50)])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    hire_date = DateField('Hire Date', validators=[DataRequired()])
    is_active = BooleanField('Active')


class MachineForm(FlaskForm):
    machine_code = StringField('Machine Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    machine_type = StringField('Machine Type', validators=[DataRequired(), Length(max=50)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    model = StringField('Model', validators=[Optional(), Length(max=50)])
    capacity = StringField('Capacity', validators=[Optional(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    installation_date = DateField('Installation Date', validators=[Optional()])
    is_active = BooleanField('Active')


class ToolForm(FlaskForm):
    tool_code = StringField('Tool Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    tool_type = StringField('Tool Type', validators=[DataRequired(), Length(max=50)])
    specification = TextAreaField('Specification')
    quantity_available = IntegerField('Quantity Available', validators=[DataRequired(), NumberRange(min=0)])
    minimum_stock = IntegerField('Minimum Stock', validators=[DataRequired(), NumberRange(min=0)])
    unit_price = DecimalField('Unit Price', validators=[Optional(), NumberRange(min=0)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    is_active = BooleanField('Active')


class CustomerForm(FlaskForm):
    customer_code = StringField('Customer Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Address')
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=10)])
    is_active = BooleanField('Active')


class VendorForm(FlaskForm):
    vendor_code = StringField('Vendor Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Address')
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=10)])
    is_active = BooleanField('Active')


class ProductForm(FlaskForm):
    product_code = StringField('Product Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    unit_of_measure = StringField('Unit of Measure', validators=[DataRequired(), Length(max=20)])
    standard_price = DecimalField('Standard Price', validators=[Optional(), NumberRange(min=0)])
    product_type = SelectField('Product Type', choices=[
        ('Raw Material', 'Raw Material'),
        ('Work in Progress', 'Work in Progress'),
        ('Finished Goods', 'Finished Goods'),
        ('Consumables', 'Consumables')
    ])
    is_active = BooleanField('Active')


class GRNForm(FlaskForm):
    grn_number = StringField('GRN Number', validators=[DataRequired(), Length(max=20)])
    vendor_id = SelectField('Vendor', coerce=int, validators=[DataRequired()])
    received_date = DateField('Received Date', validators=[DataRequired()])
    invoice_number = StringField('Invoice Number', validators=[Optional(), Length(max=50)])
    total_amount = DecimalField('Total Amount', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])


class WorkOrderForm(FlaskForm):
    work_order_number = StringField('Work Order Number', validators=[DataRequired(), Length(max=20)])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_ordered = DecimalField('Quantity Ordered', validators=[DataRequired(), NumberRange(min=0)])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent')
    ])
    planned_start_date = DateField('Planned Start Date', validators=[Optional()])
    planned_end_date = DateField('Planned End Date', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Created', 'Created'),
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ])


class QualityInspectionForm(FlaskForm):
    inspection_number = StringField('Inspection Number', validators=[DataRequired(), Length(max=20)])
    inspection_type = SelectField('Inspection Type', choices=[
        ('Incoming', 'Incoming'),
        ('In-Process', 'In-Process'),
        ('Final', 'Final')
    ], validators=[DataRequired()])
    work_order_id = SelectField('Work Order', coerce=int, validators=[Optional()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_inspected = DecimalField('Quantity Inspected', validators=[DataRequired(), NumberRange(min=0)])
    quantity_accepted = DecimalField('Quantity Accepted', validators=[DataRequired(), NumberRange(min=0)])
    quantity_rejected = DecimalField('Quantity Rejected', validators=[DataRequired(), NumberRange(min=0)])
    inspector_id = SelectField('Inspector', coerce=int, validators=[DataRequired()])
    inspection_date = DateField('Inspection Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed')
    ])
    remarks = TextAreaField('Remarks')


class ToolIssuanceForm(FlaskForm):
    issue_number = StringField('Issue Number', validators=[DataRequired(), Length(max=20)])
    tool_id = SelectField('Tool', coerce=int, validators=[DataRequired()])
    employee_id = SelectField('Employee', coerce=int, validators=[DataRequired()])
    work_order_id = SelectField('Work Order', coerce=int, validators=[Optional()])
    quantity_issued = IntegerField('Quantity Issued', validators=[DataRequired(), NumberRange(min=1)])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    expected_return_date = DateField('Expected Return Date', validators=[Optional()])


class PurchaseOrderForm(FlaskForm):
    po_number = StringField('PO Number', validators=[DataRequired(), Length(max=20)])
    vendor_id = SelectField('Vendor', coerce=int, validators=[DataRequired()])
    po_date = DateField('PO Date', validators=[DataRequired()])
    delivery_date = DateField('Delivery Date', validators=[Optional()])
    total_amount = DecimalField('Total Amount', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Acknowledged', 'Acknowledged'),
        ('Delivered', 'Delivered'),
        ('Closed', 'Closed')
    ])
    terms_and_conditions = TextAreaField('Terms and Conditions')


class SalesOrderForm(FlaskForm):
    order_number = StringField('Order Number', validators=[DataRequired(), Length(max=20)])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    order_date = DateField('Order Date', validators=[DataRequired()])
    delivery_date = DateField('Delivery Date', validators=[Optional()])
    total_amount = DecimalField('Total Amount', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Draft', 'Draft'),
        ('Confirmed', 'Confirmed'),
        ('In Production', 'In Production'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered')
    ])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent')
    ])
