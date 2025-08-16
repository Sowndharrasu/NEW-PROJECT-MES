from flask import Blueprint, redirect, render_template, request, jsonify, url_for, flash
from flask_login import login_required, current_user
from forms import (CustomerForm, WorkOrderForm, EmployeeForm, MachineForm,
                   ToolForm, VendorForm, ProductForm, QualityInspectionForm,
                   PurchaseOrderForm, SalesOrderForm, ToolIssuanceForm, GRNForm,
                   DepartmentForm)
from models_mongo import (EmployeeDoc, MachineDoc, WorkOrderDoc,
                        InventoryItemDoc, CustomerDoc, ProductDoc, GRNDoc,
                            InspectionDoc, ToolIssuanceDoc, JobCardDoc,
                         PurchaseOrderDoc, SalesOrderDoc, ToolDoc, VendorDoc, DepartmentDoc)

from utils import SimplePagination
from datetime import datetime

# Additional Models that are missing from models_mongo.py

# Create the Blueprint
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
        'Assigned': 'bg-info',
        'Scheduled': 'bg-primary'
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
        moment=lambda: type('MockMoment', (), {'date': lambda: datetime.now().date()})()
    )

# Helper function to generate unique codes
def generate_unique_code(prefix, doc_class, field_name):
    date_str = datetime.now().strftime('%Y%m%d')
    counter = 1
    while True:
        code = f"{prefix}{date_str}{counter:04d}"
        if not doc_class.objects(**{field_name: code}).first():
            return code
        counter += 1

# ---------------- Home ----------------
@main_bp.route("/")
@main_bp.route("/index")
@login_required
def index():
    return render_template("index.html")

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        # Calculate real statistics
        total_work_orders = WorkOrderDoc.objects().count()
        completed_work_orders = WorkOrderDoc.objects(status="Completed").count()
        in_progress_work_orders = WorkOrderDoc.objects(status="In Progress").count()

        total_inspections = InspectionDoc.objects().count()
        passed_inspections = InspectionDoc.objects(status="Passed").count()
        failed_inspections = InspectionDoc.objects(status="Failed").count()
        pending_inspections = InspectionDoc.objects(status="Pending").count()

        total_tools = ToolDoc.objects().count()
        low_stock_tools = 0
        if total_tools > 0:
            for tool in ToolDoc.objects():
                if tool.quantity_available <= tool.minimum_stock:
                    low_stock_tools += 1

        active_employees = EmployeeDoc.objects(is_active=True).count()
        active_machines = MachineDoc.objects(is_active=True).count()
        pending_pos = PurchaseOrderDoc.objects(status="Pending").count()

        context = {
            "stats": {
                "work_orders": total_work_orders,
                "pending_inspections": pending_inspections,
                "low_stock_tools": low_stock_tools,
                "active_employees": active_employees,
                "active_machines": active_machines,
                "pending_pos": pending_pos,
            },
            "recent_work_orders": list(WorkOrderDoc.objects().order_by('-created_at')[:5]),
        }
    except Exception:
        # Fallback with mock data if database is not properly set up
        context = {
            "stats": {
                "work_orders": 0,
                "pending_inspections": 0,
                "low_stock_tools": 0,
                "active_employees": 0,
                "active_machines": 0,
                "pending_pos": 0,
            },
            "recent_work_orders": [],
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
        "manufacturer": m.manufacturer or "",
        "model": m.model or "",
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
        role=data.get("role", "Operator")
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
    if request.method == 'GET':
        form.customer_code.data = generate_unique_code("CUST", CustomerDoc, "customer_code")
        form.is_active.data = True

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

@main_bp.route('/customers/<id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(id):
    customer = CustomerDoc.objects.get_or_404(id=id)
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

    # Populate department choices
    departments = DepartmentDoc.objects(is_active=True)
    form.department.choices = [('', 'Select Department')] + [(str(dept.id), dept.name) for dept in departments]

    print(form.department.choices)


    if not departments:
        flash('No active departments found. Please create a department first.', 'warning')

    if request.method == 'GET':
        form.employee_code.data = generate_unique_code("EMP", EmployeeDoc, "code")
        form.is_active.data = True

    if request.method == 'POST':
        if form.validate_on_submit():
            employee = EmployeeDoc(
                code=form.employee_code.data,
                name=form.name.data,
                department=DepartmentDoc.objects.get(id=form.department.data) if form.department.data else None,
                phone=form.phone.data,
                email=form.email.data,
                join_date=form.hire_date.data,
                role=form.designation.data,
                is_active=form.is_active.data
            )
            employee.save()
            flash('Employee created successfully!', 'success')
            return redirect(url_for('main.employees_list'))

    return render_template('employees/form.html', form=form, title="New Employee")

@main_bp.route('/employees/<id>/edit', methods=['GET', 'POST'])
@login_required
def employees_edit(id):
    employee = EmployeeDoc.objects.get_or_404(id=id)
    form = EmployeeForm()

    # Populate department choices
    departments = DepartmentDoc.objects(is_active=True)
    form.department.choices = [('', 'Select Department')] + [(str(dept.id), dept.name) for dept in departments]

    if not departments:
        flash('No active departments found. Please create a department first.', 'warning')

    if request.method == 'GET':
        form.employee_code.data = employee.code
        form.name.data = employee.name
        form.department.data = str(employee.department.id) if employee.department else ''
        form.phone.data = employee.phone
        form.email.data = employee.email
        form.hire_date.data = employee.join_date
        form.designation.data = employee.role
        form.is_active.data = employee.is_active

    if request.method == 'POST':
        if form.validate_on_submit():
            employee.code = form.employee_code.data
            employee.name = form.name.data
            employee.department = DepartmentDoc.objects.get(id=form.department.data) if form.department.data else None
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
    if request.method == 'GET':
        form.machine_code.data = generate_unique_code("MCH", MachineDoc, "machine_code")
        form.is_active.data = True

    if form.validate_on_submit():
        machine = MachineDoc(
            machine_code=form.machine_code.data,
            name=form.name.data,
            machine_type=form.machine_type.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            capacity=form.capacity.data,
            location=form.location.data,
            installation_date=form.installation_date.data,
            is_active=form.is_active.data
        )
        machine.save()
        flash('Machine created successfully!', 'success')
        return redirect(url_for('main.machines_list'))
    return render_template('machines/form.html', form=form, title="Add Machine")

@main_bp.route('/machines/<id>/edit', methods=['GET', 'POST'])
@login_required
def machines_edit(id):
    machine = MachineDoc.objects.get_or_404(id=id)
    form = MachineForm(obj=machine)
    if form.validate_on_submit():
        machine.machine_code = form.machine_code.data
        machine.name = form.name.data
        machine.machine_type = form.machine_type.data
        machine.manufacturer = form.manufacturer.data
        machine.model = form.model.data
        machine.capacity = form.capacity.data
        machine.location = form.location.data
        machine.installation_date = form.installation_date.data
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
    if request.method == 'GET':
        form.tool_code.data = generate_unique_code("TOOL", ToolDoc, "tool_code")
        form.is_active.data = True
        form.minimum_stock.data = 1

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

@main_bp.route('/tools/<id>/edit', methods=['GET', 'POST'])
@login_required
def tools_edit(id):
    tool = ToolDoc.objects.get_or_404(id=id)
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
    if request.method == 'GET':
        form.vendor_code.data = generate_unique_code("VEND", VendorDoc, "vendor_code")
        form.is_active.data = True

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

@main_bp.route('/vendors/<id>/edit', methods=['GET', 'POST'])
@login_required
def vendors_edit(id):
    vendor = VendorDoc.objects.get_or_404(id=id)
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
    if request.method == 'GET':
        form.product_code.data = generate_unique_code("PROD", ProductDoc, "product_code")
        form.is_active.data = True

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

@main_bp.route('/products/<id>/edit', methods=['GET', 'POST'])
@login_required
def products_edit(id):
    product = ProductDoc.objects.get_or_404(id=id)
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
    # Add missing attributes for templates
    for wo in work_orders_list:
        if not hasattr(wo, 'product') and hasattr(wo, 'item'):
            wo.product = wo.item
        if not hasattr(wo, 'quantity_ordered'):
            wo.quantity_ordered = wo.quantity if hasattr(wo, 'quantity') else 0
        if not hasattr(wo, 'quantity_produced'):
            wo.quantity_produced = 0
        if not hasattr(wo, 'priority'):
            wo.priority = "Normal"

    work_orders = SimplePagination(work_orders_list, page, per_page=10)
    return render_template('production/work_orders.html', work_orders=work_orders)

@main_bp.route('/work_orders_new', methods=['GET', 'POST'])
@login_required
def work_orders_new():
    form = WorkOrderForm()
    form.product_id.choices = [(str(i.id), i.name) for i in InventoryItemDoc.objects()]

    if request.method == 'GET':
        form.work_order_number.data = generate_unique_code("WO", WorkOrderDoc, "work_order_number")

    if request.method == 'POST':
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

    if request.method == 'GET':
        form.inspection_number.data = generate_unique_code("INS", InspectionDoc, "inspection_number")

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
    # Add missing attributes for templates
    for po in purchase_orders_list:
        if not hasattr(po, 'created_by_user'):
            po.created_by_user = current_user
        if not hasattr(po, 'vendor') and hasattr(po, 'supplier_name'):
            # Create a mock vendor object
            po.vendor = type('MockVendor', (), {'name': po.supplier_name})()

    purchase_orders = SimplePagination(purchase_orders_list, page, per_page=10)
    return render_template('procurement/purchase_orders.html', purchase_orders=purchase_orders)

@main_bp.route('/purchase_orders_new', methods=['GET', 'POST'])
@login_required
def purchase_orders_new():
    form = PurchaseOrderForm()
    form.vendor_id.choices = [(str(v.id), v.name) for v in VendorDoc.objects()]

    if request.method == 'GET':
        form.po_number.data = generate_unique_code("PO", PurchaseOrderDoc, "po_number")

    if form.validate_on_submit():
        vendor = VendorDoc.objects.get(id=form.vendor_id.data)
        purchase_order = PurchaseOrderDoc(
            po_number=form.po_number.data,
            supplier_name=vendor.name,
            vendor=vendor,
            order_date=form.po_date.data,
            expected_date=form.delivery_date.data,
            total_amount=form.total_amount.data,
            terms_and_conditions=form.terms_and_conditions.data,
            status=form.status.data,
            created_by_user=current_user
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
    # Ensure created_by_user is set
    for so in sales_orders_list:
        if not hasattr(so, 'created_by_user') or not so.created_by_user:
            so.created_by_user = current_user

    sales_orders = SimplePagination(sales_orders_list, page, per_page=10)
    return render_template('sales/orders.html', sales_orders=sales_orders)

@main_bp.route('/sales_orders_new', methods=['GET', 'POST'])
@login_required
def sales_orders_new():
    form = SalesOrderForm()
    form.customer_id.choices = [(str(c.id), c.name) for c in CustomerDoc.objects()]

    if request.method == 'GET':
        form.order_number.data = generate_unique_code("SO", SalesOrderDoc, "order_number")

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

    if request.method == 'GET':
        form.issue_number.data = generate_unique_code("TI", ToolIssuanceDoc, "issue_number")

    if form.validate_on_submit():
        tool = ToolDoc.objects.get(id=form.tool_id.data)
        if tool.quantity_available < form.quantity_issued.data:
            flash('Insufficient quantity available!', 'error')
            return render_template('toolroom/issuance_form.html', form=form, title="Issue Tool")

        issuance = ToolIssuanceDoc(
            issue_number=form.issue_number.data,
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
    # Add missing attributes for templates
    for item in raw_materials_list:
        if not hasattr(item, 'current_stock'):
            item.current_stock = item.quantity if hasattr(item, 'quantity') else 0
        if not hasattr(item, 'minimum_stock'):
            item.minimum_stock = 5  # Default minimum stock
        if not hasattr(item, 'material_code'):
            item.material_code = item.code if hasattr(item, 'code') else "N/A"
        if not hasattr(item, 'unit_of_measure'):
            item.unit_of_measure = "PCS"
        if not hasattr(item, 'unit_price'):
            item.unit_price = 0.0
        if not hasattr(item, 'location'):
            item.location = "Store"
        if not hasattr(item, 'is_active'):
            item.is_active = True

    raw_materials = SimplePagination(raw_materials_list, page, per_page=10)
    return render_template('inventory/raw_materials.html', raw_materials=raw_materials)

@main_bp.route('/grn_new', methods=['GET', 'POST'])
@login_required
def grn_new():
    form = GRNForm()
    form.vendor_id.choices = [(str(v.id), v.name) for v in VendorDoc.objects()]

    if request.method == 'GET':
        form.grn_number.data = generate_unique_code("GRN", GRNDoc, "grn_number")

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
    try:
        # Calculate statistics for the dashboard
        total_work_orders = WorkOrderDoc.objects().count()
        completed_work_orders = WorkOrderDoc.objects(status="Completed").count()
        in_progress_work_orders = WorkOrderDoc.objects(status="In Progress").count()

        total_inspections = InspectionDoc.objects().count()
        passed_inspections = InspectionDoc.objects(status="Passed").count()
        failed_inspections = InspectionDoc.objects(status="Failed").count()

        total_tools = ToolDoc.objects().count()
        low_stock_tools = 0
        if total_tools > 0:
            for tool in ToolDoc.objects():
                if tool.quantity_available <= tool.minimum_stock:
                    low_stock_tools += 1

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
    except Exception:
        # Fallback stats if database queries fail
        stats = {
            "production": {"completion_rate": 0, "completed_work_orders": 0, "total_work_orders": 0, "in_progress_work_orders": 0},
            "quality": {"pass_rate": 0, "passed_inspections": 0, "failed_inspections": 0, "total_inspections": 0},
            "inventory": {"stock_health": 0, "low_stock_tools": 0, "total_tools": 0},
            "procurement": {"fulfillment_rate": 0, "pending_pos": 0}
        }

    return render_template('reports/dashboard.html', stats=stats)

# =======================
# DEPARTMENTS
# =======================
@main_bp.route('/departments_list')
@login_required
def departments_list():
    page = request.args.get('page', 1, type=int)
    departments_list = list(DepartmentDoc.objects().order_by('-created_at'))

    departments = SimplePagination(departments_list, page, per_page=10)
    return render_template('department/list.html', departments=departments)

@main_bp.route('/departments_new', methods=['GET', 'POST'])
@login_required
def departments_new():
    form = DepartmentForm()

    if form.validate_on_submit():
        department = DepartmentDoc(
            name=form.name.data,
        )
        department.save()
        flash('Department created successfully!', 'success')
        return redirect(url_for('main.departments_list'))
    return render_template('department/form.html', form=form, title="Add Department")

@main_bp.route('/departments/<id>/edit', methods=['GET', 'POST'])
@login_required
def departments_edit(id):
    department = DepartmentDoc.objects.get(id=id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.is_active = form.is_active.data
        department.save()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('main.departments_list'))
    return render_template('department/form.html', form=form, title="Edit Department")
