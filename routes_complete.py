from flask import Blueprint, redirect, render_template, request, jsonify, url_for, flash
from flask_login import login_required, current_user
from forms import (CustomerForm, WorkOrderForm, EmployeeForm, MachineForm,
                   ToolForm, VendorForm, ProductForm, QualityInspectionForm,
                   PurchaseOrderForm, SalesOrderForm, ToolIssuanceForm, GRNForm)
from models_mongo import (EmployeeDoc, MachineDoc, WorkOrderDoc, InventoryItemDoc,
                         UserDoc, PurchaseOrderDoc)

from utils import SimplePagination
from datetime import datetime
from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, FloatField, ReferenceField, IntField

# Additional Models that are missing from models_mongo.py
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
    status = StringField(default="Issued", max_length=50)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "tool_issuances", "indexes": ["issue_number", "status"]}

    def __str__(self):
        return self.issue_number

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

main_bp = Blueprint("main", __name__)

# Helper functions for badge classes
def get_status_badge_class(status):
    status_classes = {
        'Active': 'bg-success',
        'Inactive': 'bg-secondary',
        'Pending': 'bg-warning',
        'Completed': 'bg-success',
        'In Progress': 'bg-info',
        'Cancelled': 'bg-danger',
        'Draft': 'bg-secondary',
        'Confirmed': 'bg-info',
        'Dispatched': 'bg-warning',
        'Delivered': 'bg-success',
        'Sent': 'bg-info',
        'Acknowledged': 'bg-primary',
        'Closed': 'bg-success',
        'Passed': 'bg-success',
        'Failed': 'bg-danger',
        'Issued': 'bg-warning',
        'Fully Returned': 'bg-success',
        'Assigned': 'bg-info'
    }
    return status_classes.get(status, 'bg-secondary')

def get_priority_badge_class(priority):
    priority_classes = {
        'Low': 'bg-secondary',
        'Normal': 'bg-primary',
        'High': 'bg-warning',
        'Urgent': 'bg-danger'
    }
    return priority_classes.get(priority, 'bg-primary')

# Add to app context
@main_bp.context_processor
def utility_processor():
    return dict(
        get_status_badge_class=get_status_badge_class,
        get_priority_badge_class=get_priority_badge_class,
        moment=lambda: datetime.now()  # For template date comparisons
    )

# ---------------- Home ----------------
@main_bp.route("/")
@main_bp.route("/index")
@login_required
def index():
    return render_template("index.html")

@main_bp.route('/dashboard')
@login_required
def dashboard():
    context = {
        "stats": {
            "work_orders": WorkOrderDoc.objects().count(),
            "pending_inspections": InspectionDoc.objects(status="Pending").count(),
            "low_stock_tools": ToolDoc.objects().filter(quantity_available__lte=0).count(),
            "active_employees": EmployeeDoc.objects(is_active=True).count(),
            "active_machines": MachineDoc.objects(is_active=True).count(),
            "pending_pos": PurchaseOrderDoc.objects(status="Pending").count(),
        },
        "recent_work_orders": list(WorkOrderDoc.objects().order_by('-created_at')[:5]),
    }
    return render_template('dashboard.html', **context)

# =======================
# API ROUTES (JSON)
# =======================

# ---- Machines API ----
@main_bp.route("/machines", methods=["GET"], endpoint="machines_list_api")
@login_required
def machines_list_api():
    machines = list(MachineDoc.objects().order_by("-created_at"))
    return jsonify([{
        "id": str(m.id),
        "machine_code": m.machine_code,
        "name": m.name,
        "machine_type": m.machine_type,
        "manufacturer": m.manufacturer,
        "model": m.model,
    } for m in machines])

@main_bp.route("/machines", methods=["POST"], endpoint="machines_create_api")
@login_required
def machines_create_api():
    data = request.get_json(force=True, silent=True) or request.form
    doc = MachineDoc(
        machine_code=data.get("machine_code"),
        name=data.get("name"),
        machine_type=data.get("machine_type"),
        manufacturer=data.get("manufacturer"),
        model=data.get("model"),
    )
    doc.save()
    return jsonify({"ok": True, "id": str(doc.id)}), 201

# ---- Employees API ----
@main_bp.route("/employees", methods=["GET"], endpoint="employees_list_api")
@login_required
def employees_list_api():
    employees = list(EmployeeDoc.objects().order_by("-created_at"))
    return jsonify([{
        "id": str(e.id),
        "employee_code": getattr(e, "code", None),
        "name": getattr(e, "name", None),
        "department": str(getattr(e, "department", None)) if getattr(e, "department", None) else None,
        "role": getattr(e, "role", None)
    } for e in employees])

@main_bp.route("/employees", methods=["POST"], endpoint="employees_create_api")
@login_required
def employees_create_api():
    data = request.get_json(force=True, silent=True) or request.form
    doc = EmployeeDoc(
        code=data.get("employee_code"),
        name=data.get("name"),
        department=data.get("department"),
        role=data.get("role")
    )
    doc.save()
    return jsonify({"ok": True, "id": str(doc.id)}), 201

# =======================
# CUSTOMERS
# =======================
@main_bp.route('/customers')
@login_required
def customers_list():
    page = request.args.get('page', 1, type=int)
    customers_list = list(CustomerDoc.objects().order_by('-created_at'))
    customers = SimplePagination(customers_list, page, per_page=10)
    return render_template('customers/list.html', customers=customers)

@main_bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def customers_new():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = CustomerDoc(
            customer_code=form.customer_code.data,
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            postal_code=form.postal_code.data,
            is_active=form.is_active.data
        )
        customer.save()
        flash('Customer created successfully!', 'success')
        return redirect(url_for('main.customers_list'))
    return render_template('customers/form.html', form=form, title="Add Customer")

@main_bp.route('/customers/<customer_id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(customer_id):
    customer = CustomerDoc.objects.get_or_404(id=customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.customer_code = form.customer_code.data
        customer.name = form.name.data
        customer.contact_person = form.contact_person.data
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.address = form.address.data
        customer.city = form.city.data
        customer.state = form.state.data
        customer.country = form.country.data
        customer.postal_code = form.postal_code.data
        customer.is_active = form.is_active.data
        customer.save()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('main.customers_list'))
    return render_template('customers/form.html', form=form, title="Edit Customer")

# =======================
# EMPLOYEES
# =======================
@main_bp.route('/employees_list')
@login_required
def employees_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    all_employees = list(EmployeeDoc.objects().order_by('-created_at'))
    employees = SimplePagination(all_employees, page, per_page)
    return render_template('employees/list.html', employees=employees)

@main_bp.route('/employees_new', methods=['GET', 'POST'])
@login_required
def employees_new():
    form = EmployeeForm()

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        form = EmployeeForm(data=data)

        if form.validate_on_submit():
            employee = EmployeeDoc(
                code=form.employee_code.data,
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                join_date=form.hire_date.data,
                role=form.designation.data,
                is_active=form.is_active.data
            )
            employee.save()
            flash('Employee created successfully!', 'success')
            return redirect(url_for('main.employees_list'))
        else:
            print(form.errors)

    return render_template('employees/form.html', form=form, title="New Employee")

@main_bp.route('/employees/<employee_id>/edit', methods=['GET', 'POST'])
@login_required
def employees_edit(employee_id):
    employee = EmployeeDoc.objects.get_or_404(id=employee_id)
    form = EmployeeForm()

    if request.method == 'GET':
        form.employee_code.data = employee.code
        form.name.data = employee.name
        form.phone.data = employee.phone
        form.email.data = employee.email
        form.hire_date.data = employee.join_date
        form.designation.data = employee.role
        form.is_active.data = employee.is_active

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        form = EmployeeForm(data=data)

        if form.validate_on_submit():
            employee.code = form.employee_code.data
            employee.name = form.name.data
            employee.phone = form.phone.data
            employee.email = form.email.data
            employee.join_date = form.hire_date.data
            employee.role = form.designation.data
            employee.is_active = form.is_active.data
            employee.save()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('main.employees_list'))

    return render_template('employees/form.html', form=form, title="Edit Employee")

# =======================
# MACHINES
# =======================
@main_bp.route('/machines_list')
@login_required
def machines_list():
    page = request.args.get('page', 1, type=int)
    machines_list = list(MachineDoc.objects().order_by('-created_at'))
    machines = SimplePagination(machines_list, page, per_page=10)
    return render_template('machines/list.html', machines=machines)

@main_bp.route('/machines_new', methods=['GET', 'POST'])
@login_required
def machines_new():
    form = MachineForm()
    if form.validate_on_submit():
        machine = MachineDoc(
            machine_code=form.machine_code.data,
            name=form.name.data,
            machine_type=form.machine_type.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            is_active=form.is_active.data
        )
        machine.save()
        flash('Machine created successfully!', 'success')
        return redirect(url_for('main.machines_list'))
    return render_template('machines/form.html', form=form, title="Add Machine")

@main_bp.route('/machines/<machine_id>/edit', methods=['GET', 'POST'])
@login_required
def machines_edit(machine_id):
    machine = MachineDoc.objects.get_or_404(id=machine_id)
    form = MachineForm(obj=machine)
    if form.validate_on_submit():
        machine.machine_code = form.machine_code.data
        machine.name = form.name.data
        machine.machine_type = form.machine_type.data
        machine.manufacturer = form.manufacturer.data
        machine.model = form.model.data
        machine.is_active = form.is_active.data
        machine.save()
        flash('Machine updated successfully!', 'success')
        return redirect(url_for('main.machines_list'))
    return render_template('machines/form.html', form=form, title="Edit Machine")

# =======================
# TOOLS
# =======================
@main_bp.route('/tools_list')
@login_required
def tools_list():
    page = request.args.get('page', 1, type=int)
    tools_list = list(ToolDoc.objects().order_by('-created_at'))
    tools = SimplePagination(tools_list, page, per_page=10)
    return render_template('tools/list.html', tools=tools)

@main_bp.route('/tools_new', methods=['GET', 'POST'])
@login_required
def tools_new():
    form = ToolForm()
    if form.validate_on_submit():
        tool = ToolDoc(
            tool_code=form.tool_code.data,
            name=form.name.data,
            tool_type=form.tool_type.data,
            specification=form.specification.data,
            quantity_available=form.quantity_available.data,
            minimum_stock=form.minimum_stock.data,
            unit_price=form.unit_price.data,
            location=form.location.data,
            is_active=form.is_active.data
        )
        tool.save()
        flash('Tool created successfully!', 'success')
        return redirect(url_for('main.tools_list'))
    return render_template('tools/form.html', form=form, title="Add Tool")

@main_bp.route('/tools/<tool_id>/edit', methods=['GET', 'POST'])
@login_required
def tools_edit(tool_id):
    tool = ToolDoc.objects.get_or_404(id=tool_id)
    form = ToolForm(obj=tool)
    if form.validate_on_submit():
        tool.tool_code = form.tool_code.data
        tool.name = form.name.data
        tool.tool_type = form.tool_type.data
        tool.specification = form.specification.data
        tool.quantity_available = form.quantity_available.data
        tool.minimum_stock = form.minimum_stock.data
        tool.unit_price = form.unit_price.data
        tool.location = form.location.data
        tool.is_active = form.is_active.data
        tool.save()
        flash('Tool updated successfully!', 'success')
        return redirect(url_for('main.tools_list'))
    return render_template('tools/form.html', form=form, title="Edit Tool")

# =======================
# VENDORS
# =======================
@main_bp.route('/vendors_list')
@login_required
def vendors_list():
    page = request.args.get('page', 1, type=int)
    vendors_list = list(VendorDoc.objects().order_by('-created_at'))
    vendors = SimplePagination(vendors_list, page, per_page=10)
    return render_template('vendors/list.html', vendors=vendors)

@main_bp.route('/vendors_new', methods=['GET', 'POST'])
@login_required
def vendors_new():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = VendorDoc(
            vendor_code=form.vendor_code.data,
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            postal_code=form.postal_code.data,
            is_active=form.is_active.data
        )
        vendor.save()
        flash('Vendor created successfully!', 'success')
        return redirect(url_for('main.vendors_list'))
    return render_template('vendors/form.html', form=form, title="Add Vendor")

@main_bp.route('/vendors/<vendor_id>/edit', methods=['GET', 'POST'])
@login_required
def vendors_edit(vendor_id):
    vendor = VendorDoc.objects.get_or_404(id=vendor_id)
    form = VendorForm(obj=vendor)
    if form.validate_on_submit():
        vendor.vendor_code = form.vendor_code.data
        vendor.name = form.name.data
        vendor.contact_person = form.contact_person.data
        vendor.phone = form.phone.data
        vendor.email = form.email.data
        vendor.address = form.address.data
        vendor.city = form.city.data
        vendor.state = form.state.data
        vendor.country = form.country.data
        vendor.postal_code = form.postal_code.data
        vendor.is_active = form.is_active.data
        vendor.save()
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('main.vendors_list'))
    return render_template('vendors/form.html', form=form, title="Edit Vendor")

# =======================
# PRODUCTS
# =======================
@main_bp.route('/products_list')
@login_required
def products_list():
    page = request.args.get('page', 1, type=int)
    products_list = list(ProductDoc.objects().order_by('-created_at'))
    products = SimplePagination(products_list, page, per_page=10)
    return render_template('products/list.html', products=products)

@main_bp.route('/products_new', methods=['GET', 'POST'])
@login_required
def products_new():
    form = ProductForm()
    if form.validate_on_submit():
        product = ProductDoc(
            product_code=form.product_code.data,
            name=form.name.data,
            description=form.description.data,
            unit_of_measure=form.unit_of_measure.data,
            standard_price=form.standard_price.data,
            product_type=form.product_type.data,
            is_active=form.is_active.data
        )
        product.save()
        flash('Product created successfully!', 'success')
        return redirect(url_for('main.products_list'))
    return render_template('products/form.html', form=form, title="Add Product")

@main_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@login_required
def products_edit(product_id):
    product = ProductDoc.objects.get_or_404(id=product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.product_code = form.product_code.data
        product.name = form.name.data
        product.description = form.description.data
        product.unit_of_measure = form.unit_of_measure.data
        product.standard_price = form.standard_price.data
        product.product_type = form.product_type.data
        product.is_active = form.is_active.data
        product.save()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.products_list'))
    return render_template('products/form.html', form=form, title="Edit Product")

# =======================
# WORK ORDERS
# =======================
@main_bp.route('/work_orders_list')
@login_required
def work_orders_list():
    page = request.args.get('page', 1, type=int)
    work_orders_list = list(WorkOrderDoc.objects().order_by('-created_at'))
    work_orders = SimplePagination(work_orders_list, page, per_page=10)
    return render_template('production/work_orders.html', work_orders=work_orders)

@main_bp.route('/work_orders_new', methods=['GET', 'POST'])
@login_required
def work_orders_new():
    form = WorkOrderForm()
    form.product_id.choices = [(str(i.id), i.name) for i in InventoryItemDoc.objects()]

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        form = WorkOrderForm(data=data)
        form.product_id.choices = [(str(i.id), i.name) for i in InventoryItemDoc.objects()]

        if form.validate_on_submit():
            item_doc = InventoryItemDoc.objects(id=form.product_id.data).first()
            if not item_doc:
                form.product_id.errors.append("Invalid product selected.")
                return render_template('production/work_order_form.html', form=form, title="New Work Order")

            work_order = WorkOrderDoc(
                work_order_number=form.work_order_number.data,
                item=item_doc,
                quantity=form.quantity_ordered.data,
                start_date=form.planned_start_date.data,
                due_date=form.planned_end_date.data,
                status=form.status.data
            )
            work_order.save()
            flash('Work Order created successfully!', 'success')
            return redirect(url_for('main.work_orders_list'))
        else:
            print(form.errors)

    return render_template('production/work_order_form.html', form=form, title="New Work Order")

# =======================
# INSPECTIONS
# =======================
@main_bp.route('/inspections_list')
@login_required
def inspections_list():
    page = request.args.get('page', 1, type=int)
    inspections_list = list(InspectionDoc.objects().order_by('-created_at'))
    inspections = SimplePagination(inspections_list, page, per_page=10)
    return render_template('quality/inspections.html', inspections=inspections)

@main_bp.route('/inspections_new', methods=['GET', 'POST'])
@login_required
def inspections_new():
    form = QualityInspectionForm()
    # Populate choices for dropdowns
    form.product_id.choices = [(str(p.id), p.name) for p in ProductDoc.objects()]
    form.work_order_id.choices = [('', 'Select Work Order')] + [(str(w.id), w.work_order_number) for w in WorkOrderDoc.objects()]
    form.inspector_id.choices = [(str(e.id), e.name) for e in EmployeeDoc.objects()]

    if form.validate_on_submit():
        inspection = InspectionDoc(
            inspection_number=form.inspection_number.data,
            inspection_type=form.inspection_type.data,
            product=ProductDoc.objects.get(id=form.product_id.data),
            work_order=WorkOrderDoc.objects.get(id=form.work_order_id.data) if form.work_order_id.data else None,
            quantity_inspected=form.quantity_inspected.data,
            quantity_accepted=form.quantity_accepted.data,
            quantity_rejected=form.quantity_rejected.data,
            inspector=EmployeeDoc.objects.get(id=form.inspector_id.data),
            inspection_date=form.inspection_date.data,
            status=form.status.data,
            remarks=form.remarks.data
        )
        inspection.save()
        flash('Inspection created successfully!', 'success')
        return redirect(url_for('main.inspections_list'))
    return render_template('quality/inspection_form.html', form=form, title="New Inspection")

# =======================
# PURCHASE ORDERS
# =======================
@main_bp.route('/purchase_orders_list')
@login_required
def purchase_orders_list():
    page = request.args.get('page', 1, type=int)
    purchase_orders_list = list(PurchaseOrderDoc.objects().order_by('-created_at'))
    purchase_orders = SimplePagination(purchase_orders_list, page, per_page=10)
    return render_template('procurement/purchase_orders.html', purchase_orders=purchase_orders)

@main_bp.route('/purchase_orders_new', methods=['GET', 'POST'])
@login_required
def purchase_orders_new():
    form = PurchaseOrderForm()
    form.vendor_id.choices = [(str(v.id), v.name) for v in VendorDoc.objects()]

    if form.validate_on_submit():
        purchase_order = PurchaseOrderDoc(
            po_number=form.po_number.data,
            supplier_name=VendorDoc.objects.get(id=form.vendor_id.data).name,
            order_date=form.po_date.data,
            expected_date=form.delivery_date.data,
            status=form.status.data
        )
        purchase_order.save()
        flash('Purchase Order created successfully!', 'success')
        return redirect(url_for('main.purchase_orders_list'))
    return render_template('procurement/purchase_order_form.html', form=form, title="New Purchase Order")

# =======================
# SALES ORDERS
# =======================
@main_bp.route('/sales_orders_list')
@login_required
def sales_orders_list():
    page = request.args.get('page', 1, type=int)
    sales_orders_list = list(SalesOrderDoc.objects().order_by('-created_at'))
    sales_orders = SimplePagination(sales_orders_list, page, per_page=10)
    return render_template('sales/orders.html', sales_orders=sales_orders)

@main_bp.route('/sales_orders_new', methods=['GET', 'POST'])
@login_required
def sales_orders_new():
    form = SalesOrderForm()
    form.customer_id.choices = [(str(c.id), c.name) for c in CustomerDoc.objects()]

    if form.validate_on_submit():
        sales_order = SalesOrderDoc(
            order_number=form.order_number.data,
            customer=CustomerDoc.objects.get(id=form.customer_id.data),
            order_date=form.order_date.data,
            delivery_date=form.delivery_date.data,
            total_amount=form.total_amount.data,
            priority=form.priority.data,
            status=form.status.data,
            created_by_user=current_user
        )
        sales_order.save()
        flash('Sales Order created successfully!', 'success')
        return redirect(url_for('main.sales_orders_list'))
    return render_template('sales/order_form.html', form=form, title="New Sales Order")

# =======================
# TOOL ISSUANCES
# =======================
@main_bp.route('/tool_issuances_list')
@login_required
def tool_issuances_list():
    page = request.args.get('page', 1, type=int)
    issuances_list = list(ToolIssuanceDoc.objects().order_by('-created_at'))
    issuances = SimplePagination(issuances_list, page, per_page=10)
    return render_template('toolroom/issuance.html', issuances=issuances)

@main_bp.route('/tool_issuances_new', methods=['GET', 'POST'])
@login_required
def tool_issuances_new():
    form = ToolIssuanceForm()
    form.tool_id.choices = [(str(t.id), f"{t.name} (Available: {t.quantity_available})") for t in ToolDoc.objects()]
    form.employee_id.choices = [(str(e.id), e.name) for e in EmployeeDoc.objects()]
    form.work_order_id.choices = [('', 'Select Work Order')] + [(str(w.id), w.work_order_number) for w in WorkOrderDoc.objects()]

    if form.validate_on_submit():
        tool = ToolDoc.objects.get(id=form.tool_id.data)
        if tool.quantity_available < form.quantity_issued.data:
            flash('Insufficient quantity available!', 'error')
            return render_template('toolroom/issuance_form.html', form=form, title="Issue Tool")

        # Generate unique issue number
        import random
        issue_number = f"TI{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

        issuance = ToolIssuanceDoc(
            issue_number=issue_number,
            tool=tool,
            employee=EmployeeDoc.objects.get(id=form.employee_id.data),
            work_order=WorkOrderDoc.objects.get(id=form.work_order_id.data) if form.work_order_id.data else None,
            quantity_issued=form.quantity_issued.data,
            issue_date=form.issue_date.data,
            expected_return_date=form.expected_return_date.data
        )
        issuance.save()

        # Update tool quantity
        tool.quantity_available -= form.quantity_issued.data
        tool.save()

        flash('Tool issued successfully!', 'success')
        return redirect(url_for('main.tool_issuances_list'))
    return render_template('toolroom/issuance_form.html', form=form, title="Issue Tool")

# =======================
# JOB CARDS
# =======================
@main_bp.route('/job_cards_list')
@login_required
def job_cards_list():
    page = request.args.get('page', 1, type=int)
    job_cards_list = list(JobCardDoc.objects().order_by('-created_at'))
    job_cards = SimplePagination(job_cards_list, page, per_page=10)
    return render_template('production/job_cards.html', job_cards=job_cards)

# =======================
# INVENTORY
# =======================
@main_bp.route('/inventory_raw_materials')
@login_required
def inventory_raw_materials():
    page = request.args.get('page', 1, type=int)
    raw_materials_list = list(InventoryItemDoc.objects().order_by('-created_at'))
    raw_materials = SimplePagination(raw_materials_list, page, per_page=10)
    return render_template('inventory/raw_materials.html', raw_materials=raw_materials)

@main_bp.route('/grn_new', methods=['GET', 'POST'])
@login_required
def grn_new():
    form = GRNForm()
    form.vendor_id.choices = [(str(v.id), v.name) for v in VendorDoc.objects()]

    if form.validate_on_submit():
        grn = GRNDoc(
            grn_number=form.grn_number.data,
            vendor=VendorDoc.objects.get(id=form.vendor_id.data),
            received_date=form.received_date.data,
            invoice_number=form.invoice_number.data,
            total_amount=form.total_amount.data,
            status=form.status.data
        )
        grn.save()
        flash('GRN created successfully!', 'success')
        return redirect(url_for('main.inventory_raw_materials'))
    return render_template('inventory/grn_form.html', form=form, title="New GRN")

# =======================
# REPORTS
# =======================
@main_bp.route('/reports_dashboard')
@login_required
def reports_dashboard():
    # Calculate statistics for the dashboard
    total_work_orders = WorkOrderDoc.objects().count()
    completed_work_orders = WorkOrderDoc.objects(status="Completed").count()
    in_progress_work_orders = WorkOrderDoc.objects(status="In Progress").count()

    total_inspections = InspectionDoc.objects().count()
    passed_inspections = InspectionDoc.objects(status="Passed").count()
    failed_inspections = InspectionDoc.objects(status="Failed").count()

    total_tools = ToolDoc.objects().count()
    low_stock_tools = len([t for t in ToolDoc.objects() if t.quantity_available <= t.minimum_stock])

    pending_pos = PurchaseOrderDoc.objects(status="Pending").count()

    stats = {
        "production": {
            "completion_rate": round((completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0, 1),
            "completed_work_orders": completed_work_orders,
            "total_work_orders": total_work_orders,
            "in_progress_work_orders": in_progress_work_orders
        },
        "quality": {
            "pass_rate": round((passed_inspections / total_inspections * 100) if total_inspections > 0 else 0, 1),
            "passed_inspections": passed_inspections,
            "failed_inspections": failed_inspections,
            "total_inspections": total_inspections
        },
        "inventory": {
            "stock_health": round(((total_tools - low_stock_tools) / total_tools * 100) if total_tools > 0 else 0, 1),
            "low_stock_tools": low_stock_tools,
            "total_tools": total_tools
        },
        "procurement": {
            "fulfillment_rate": 85,  # Mock data
            "pending_pos": pending_pos
        }
    }

    return render_template('reports/dashboard.html', stats=stats)
