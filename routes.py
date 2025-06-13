from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import *
from forms import *
from utils import generate_code, check_permission
from datetime import datetime, date

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get basic statistics for dashboard
    stats = {
        'work_orders': WorkOrder.query.filter_by(status='In Progress').count(),
        'pending_inspections': QualityInspection.query.filter_by(status='Pending').count(),
        'low_stock_tools': Tool.query.filter(Tool.quantity_available <= Tool.minimum_stock).count(),
        'active_employees': Employee.query.filter_by(is_active=True).count(),
        'active_machines': Machine.query.filter_by(is_active=True).count(),
        'pending_pos': PurchaseOrder.query.filter_by(status='Draft').count()
    }
    
    # Recent work orders
    recent_work_orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).limit(5).all()
    
    # Low stock alerts
    low_stock_items = Tool.query.filter(Tool.quantity_available <= Tool.minimum_stock).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, 
                         recent_work_orders=recent_work_orders, 
                         low_stock_items=low_stock_items)


# Employee Management Routes
@main_bp.route('/employees')
@login_required
def employees_list():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    employees = Employee.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('employees/list.html', employees=employees)


@main_bp.route('/employees/new', methods=['GET', 'POST'])
@login_required
def employees_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            employee_code=form.employee_code.data,
            name=form.name.data,
            department=form.department.data,
            designation=form.designation.data,
            phone=form.phone.data,
            email=form.email.data,
            hire_date=form.hire_date.data,
            is_active=form.is_active.data
        )
        db.session.add(employee)
        db.session.commit()
        flash('Employee created successfully!', 'success')
        return redirect(url_for('main.employees_list'))
    
    return render_template('employees/form.html', form=form, title='New Employee')


@main_bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def employees_edit(id):
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    
    if form.validate_on_submit():
        form.populate_obj(employee)
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('main.employees_list'))
    
    return render_template('employees/form.html', form=form, title='Edit Employee', employee=employee)


# Machine Management Routes
@main_bp.route('/machines')
@login_required
def machines_list():
    page = request.args.get('page', 1, type=int)
    machines = Machine.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('machines/list.html', machines=machines)


@main_bp.route('/machines/new', methods=['GET', 'POST'])
@login_required
def machines_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = MachineForm()
    if form.validate_on_submit():
        machine = Machine(
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
        db.session.add(machine)
        db.session.commit()
        flash('Machine created successfully!', 'success')
        return redirect(url_for('main.machines_list'))
    
    return render_template('machines/form.html', form=form, title='New Machine')


@main_bp.route('/machines/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def machines_edit(id):
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    machine = Machine.query.get_or_404(id)
    form = MachineForm(obj=machine)
    
    if form.validate_on_submit():
        form.populate_obj(machine)
        db.session.commit()
        flash('Machine updated successfully!', 'success')
        return redirect(url_for('main.machines_list'))
    
    return render_template('machines/form.html', form=form, title='Edit Machine', machine=machine)


# Tool Management Routes
@main_bp.route('/tools')
@login_required
def tools_list():
    page = request.args.get('page', 1, type=int)
    tools = Tool.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('tools/list.html', tools=tools)


@main_bp.route('/tools/new', methods=['GET', 'POST'])
@login_required
def tools_new():
    if not check_permission(['Admin', 'Manager', 'Storekeeper']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ToolForm()
    if form.validate_on_submit():
        tool = Tool(
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
        db.session.add(tool)
        db.session.commit()
        flash('Tool created successfully!', 'success')
        return redirect(url_for('main.tools_list'))
    
    return render_template('tools/form.html', form=form, title='New Tool')


@main_bp.route('/tools/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def tools_edit(id):
    if not check_permission(['Admin', 'Manager', 'Storekeeper']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    tool = Tool.query.get_or_404(id)
    form = ToolForm(obj=tool)
    
    if form.validate_on_submit():
        form.populate_obj(tool)
        db.session.commit()
        flash('Tool updated successfully!', 'success')
        return redirect(url_for('main.tools_list'))
    
    return render_template('tools/form.html', form=form, title='Edit Tool', tool=tool)


# Customer Management Routes
@main_bp.route('/customers')
@login_required
def customers_list():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('customers/list.html', customers=customers)


@main_bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def customers_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
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
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully!', 'success')
        return redirect(url_for('main.customers_list'))
    
    return render_template('customers/form.html', form=form, title='New Customer')


@main_bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(id):
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('main.customers_list'))
    
    return render_template('customers/form.html', form=form, title='Edit Customer', customer=customer)


# Vendor Management Routes
@main_bp.route('/vendors')
@login_required
def vendors_list():
    page = request.args.get('page', 1, type=int)
    vendors = Vendor.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('vendors/list.html', vendors=vendors)


@main_bp.route('/vendors/new', methods=['GET', 'POST'])
@login_required
def vendors_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(
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
        db.session.add(vendor)
        db.session.commit()
        flash('Vendor created successfully!', 'success')
        return redirect(url_for('main.vendors_list'))
    
    return render_template('vendors/form.html', form=form, title='New Vendor')


@main_bp.route('/vendors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def vendors_edit(id):
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vendor = Vendor.query.get_or_404(id)
    form = VendorForm(obj=vendor)
    
    if form.validate_on_submit():
        form.populate_obj(vendor)
        db.session.commit()
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('main.vendors_list'))
    
    return render_template('vendors/form.html', form=form, title='Edit Vendor', vendor=vendor)


# Product Management Routes
@main_bp.route('/products')
@login_required
def products_list():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('products/list.html', products=products)


@main_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def products_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            product_code=form.product_code.data,
            name=form.name.data,
            description=form.description.data,
            unit_of_measure=form.unit_of_measure.data,
            standard_price=form.standard_price.data,
            product_type=form.product_type.data,
            is_active=form.is_active.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('main.products_list'))
    
    return render_template('products/form.html', form=form, title='New Product')


@main_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def products_edit(id):
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.products_list'))
    
    return render_template('products/form.html', form=form, title='Edit Product', product=product)


# Inventory Management Routes
@main_bp.route('/inventory/raw-materials')
@login_required
def inventory_raw_materials():
    page = request.args.get('page', 1, type=int)
    raw_materials = RawMaterial.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('inventory/raw_materials.html', raw_materials=raw_materials)


@main_bp.route('/inventory/grn/new', methods=['GET', 'POST'])
@login_required
def grn_new():
    if not check_permission(['Admin', 'Manager', 'Storekeeper']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = GRNForm()
    form.vendor_id.choices = [(v.id, v.name) for v in Vendor.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        grn = GoodsReceiptNote(
            grn_number=form.grn_number.data,
            vendor_id=form.vendor_id.data,
            received_date=form.received_date.data,
            invoice_number=form.invoice_number.data,
            total_amount=form.total_amount.data,
            status=form.status.data,
            received_by=current_user.id
        )
        db.session.add(grn)
        db.session.commit()
        flash('GRN created successfully!', 'success')
        return redirect(url_for('main.inventory_raw_materials'))
    
    return render_template('inventory/grn_form.html', form=form, title='New GRN')


# Production Management Routes
@main_bp.route('/production/work-orders')
@login_required
def work_orders_list():
    page = request.args.get('page', 1, type=int)
    work_orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('production/work_orders.html', work_orders=work_orders)


@main_bp.route('/production/work-orders/new', methods=['GET', 'POST'])
@login_required
def work_orders_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = WorkOrderForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        work_order = WorkOrder(
            work_order_number=form.work_order_number.data,
            product_id=form.product_id.data,
            quantity_ordered=form.quantity_ordered.data,
            priority=form.priority.data,
            status=form.status.data,
            planned_start_date=form.planned_start_date.data,
            planned_end_date=form.planned_end_date.data,
            created_by=current_user.id
        )
        db.session.add(work_order)
        db.session.commit()
        flash('Work Order created successfully!', 'success')
        return redirect(url_for('main.work_orders_list'))
    
    return render_template('production/work_order_form.html', form=form, title='New Work Order')


@main_bp.route('/production/job-cards')
@login_required
def job_cards_list():
    page = request.args.get('page', 1, type=int)
    job_cards = JobCard.query.order_by(JobCard.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('production/job_cards.html', job_cards=job_cards)


# Quality Management Routes
@main_bp.route('/quality/inspections')
@login_required
def inspections_list():
    page = request.args.get('page', 1, type=int)
    inspections = QualityInspection.query.order_by(QualityInspection.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('quality/inspections.html', inspections=inspections)


@main_bp.route('/quality/inspections/new', methods=['GET', 'POST'])
@login_required
def inspections_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = QualityInspectionForm()
    form.work_order_id.choices = [(0, 'Select Work Order')] + [(wo.id, wo.work_order_number) for wo in WorkOrder.query.filter_by(status='In Progress').all()]
    form.product_id.choices = [(p.id, p.name) for p in Product.query.filter_by(is_active=True).all()]
    form.inspector_id.choices = [(e.id, e.name) for e in Employee.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        inspection = QualityInspection(
            inspection_number=form.inspection_number.data,
            inspection_type=form.inspection_type.data,
            work_order_id=form.work_order_id.data if form.work_order_id.data != 0 else None,
            product_id=form.product_id.data,
            quantity_inspected=form.quantity_inspected.data,
            quantity_accepted=form.quantity_accepted.data,
            quantity_rejected=form.quantity_rejected.data,
            inspector_id=form.inspector_id.data,
            inspection_date=form.inspection_date.data,
            status=form.status.data,
            remarks=form.remarks.data
        )
        db.session.add(inspection)
        db.session.commit()
        flash('Quality Inspection created successfully!', 'success')
        return redirect(url_for('main.inspections_list'))
    
    return render_template('quality/inspection_form.html', form=form, title='New Quality Inspection')


# Tool Room Management Routes
@main_bp.route('/toolroom/issuances')
@login_required
def tool_issuances_list():
    page = request.args.get('page', 1, type=int)
    issuances = ToolIssuance.query.order_by(ToolIssuance.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('toolroom/issuance.html', issuances=issuances)


@main_bp.route('/toolroom/issuances/new', methods=['GET', 'POST'])
@login_required
def tool_issuances_new():
    if not check_permission(['Admin', 'Manager', 'Storekeeper']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ToolIssuanceForm()
    form.tool_id.choices = [(t.id, f"{t.name} (Available: {t.quantity_available})") for t in Tool.query.filter_by(is_active=True).all()]
    form.employee_id.choices = [(e.id, e.name) for e in Employee.query.filter_by(is_active=True).all()]
    form.work_order_id.choices = [(0, 'Select Work Order')] + [(wo.id, wo.work_order_number) for wo in WorkOrder.query.filter_by(status='In Progress').all()]
    
    if form.validate_on_submit():
        issuance = ToolIssuance(
            issue_number=form.issue_number.data,
            tool_id=form.tool_id.data,
            employee_id=form.employee_id.data,
            work_order_id=form.work_order_id.data if form.work_order_id.data != 0 else None,
            quantity_issued=form.quantity_issued.data,
            issue_date=form.issue_date.data,
            expected_return_date=form.expected_return_date.data,
            issued_by=current_user.id
        )
        
        # Update tool quantity
        tool = Tool.query.get(form.tool_id.data)
        if tool.quantity_available >= form.quantity_issued.data:
            tool.quantity_available -= form.quantity_issued.data
            db.session.add(issuance)
            db.session.commit()
            flash('Tool issued successfully!', 'success')
            return redirect(url_for('main.tool_issuances_list'))
        else:
            flash('Insufficient tool quantity available!', 'error')
    
    return render_template('toolroom/issuance_form.html', form=form, title='New Tool Issuance')


# Procurement Management Routes
@main_bp.route('/procurement/purchase-orders')
@login_required
def purchase_orders_list():
    page = request.args.get('page', 1, type=int)
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('procurement/purchase_orders.html', purchase_orders=purchase_orders)


@main_bp.route('/procurement/purchase-orders/new', methods=['GET', 'POST'])
@login_required
def purchase_orders_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = PurchaseOrderForm()
    form.vendor_id.choices = [(v.id, v.name) for v in Vendor.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        purchase_order = PurchaseOrder(
            po_number=form.po_number.data,
            vendor_id=form.vendor_id.data,
            po_date=form.po_date.data,
            delivery_date=form.delivery_date.data,
            total_amount=form.total_amount.data,
            status=form.status.data,
            terms_and_conditions=form.terms_and_conditions.data,
            created_by=current_user.id
        )
        db.session.add(purchase_order)
        db.session.commit()
        flash('Purchase Order created successfully!', 'success')
        return redirect(url_for('main.purchase_orders_list'))
    
    return render_template('procurement/purchase_order_form.html', form=form, title='New Purchase Order')


# Sales Management Routes
@main_bp.route('/sales/orders')
@login_required
def sales_orders_list():
    page = request.args.get('page', 1, type=int)
    sales_orders = SalesOrder.query.order_by(SalesOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('sales/orders.html', sales_orders=sales_orders)


@main_bp.route('/sales/orders/new', methods=['GET', 'POST'])
@login_required
def sales_orders_new():
    if not check_permission(['Admin', 'Manager']):
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = SalesOrderForm()
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        sales_order = SalesOrder(
            order_number=form.order_number.data,
            customer_id=form.customer_id.data,
            order_date=form.order_date.data,
            delivery_date=form.delivery_date.data,
            total_amount=form.total_amount.data,
            status=form.status.data,
            priority=form.priority.data,
            created_by=current_user.id
        )
        db.session.add(sales_order)
        db.session.commit()
        flash('Sales Order created successfully!', 'success')
        return redirect(url_for('main.sales_orders_list'))
    
    return render_template('sales/order_form.html', form=form, title='New Sales Order')


# Reports Routes
@main_bp.route('/reports')
@login_required
def reports_dashboard():
    # Production statistics
    total_work_orders = WorkOrder.query.count()
    completed_work_orders = WorkOrder.query.filter_by(status='Completed').count()
    in_progress_work_orders = WorkOrder.query.filter_by(status='In Progress').count()
    
    # Quality statistics
    total_inspections = QualityInspection.query.count()
    passed_inspections = QualityInspection.query.filter_by(status='Passed').count()
    failed_inspections = QualityInspection.query.filter_by(status='Failed').count()
    
    # Inventory statistics
    total_tools = Tool.query.count()
    low_stock_tools = Tool.query.filter(Tool.quantity_available <= Tool.minimum_stock).count()
    
    # Purchase Order statistics
    total_pos = PurchaseOrder.query.count()
    pending_pos = PurchaseOrder.query.filter_by(status='Draft').count()
    
    stats = {
        'production': {
            'total_work_orders': total_work_orders,
            'completed_work_orders': completed_work_orders,
            'in_progress_work_orders': in_progress_work_orders,
            'completion_rate': round((completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0, 1)
        },
        'quality': {
            'total_inspections': total_inspections,
            'passed_inspections': passed_inspections,
            'failed_inspections': failed_inspections,
            'pass_rate': round((passed_inspections / total_inspections * 100) if total_inspections > 0 else 0, 1)
        },
        'inventory': {
            'total_tools': total_tools,
            'low_stock_tools': low_stock_tools,
            'stock_health': round(((total_tools - low_stock_tools) / total_tools * 100) if total_tools > 0 else 0, 1)
        },
        'procurement': {
            'total_pos': total_pos,
            'pending_pos': pending_pos,
            'fulfillment_rate': round(((total_pos - pending_pos) / total_pos * 100) if total_pos > 0 else 0, 1)
        }
    }
    
    return render_template('reports/dashboard.html', stats=stats)
