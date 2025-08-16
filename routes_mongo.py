from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_login import login_required
from forms import CustomerForm, WorkOrderForm
from models_mongo import EmployeeDoc, MachineDoc, WorkOrderDoc, InventoryItemDoc

main_bp = Blueprint("main", __name__)

# ---------------- Home ----------------
@main_bp.route("/")
@main_bp.route("/index")
@login_required
def index():
    return render_template("index.html")


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
        "employee_code": getattr(e, "employee_code", None),
        "name": getattr(e, "name", None),
        "department": getattr(e, "department", None),
        "role": getattr(e, "role", None)
    } for e in employees])

@main_bp.route("/employees", methods=["POST"], endpoint="employees_create_api")
@login_required
def employees_create_api():
    data = request.get_json(force=True, silent=True) or request.form
    doc = EmployeeDoc(
        employee_code=data.get("employee_code"),
        name=data.get("name"),
        department=data.get("department"),
        role=data.get("role")
    )
    doc.save()
    return jsonify({"ok": True, "id": str(doc.id)}), 201

@main_bp.route('/customers')
@login_required
def customers_list():
    page = request.args.get('page', 1, type=int)
    # TODO: replace [] with real DB fetch (e.g., list(CustomerDoc.objects().order_by('-created_at')))
    items = []
    customers = SimplePagination(items, page, per_page=10)
    return render_template('customers/list.html', customers=customers)

@main_bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def customers_new():
    form = CustomerForm()
    if form.validate_on_submit():
        # TODO: save customer to DB here
        return redirect(url_for('main.customers_list'))
    return render_template('customers/form.html', form=form, title="Add Customer")



# =======================
# HTML RENDER ROUTES (PAGES)
# Endpoint names EXACT match with templates' url_for('main.X')
# =======================


@main_bp.route('/dashboard')
@login_required
def dashboard():
    context = {
        "stats": {
            "work_orders": 0,  # TODO: replace with actual count
            "pending_inspections": 0,  # TODO: replace with actual count
            "low_stock_tools": 0,  # TODO: replace with actual count
            "active_employees": EmployeeDoc.objects(is_active=True).count(),
            "active_machines": MachineDoc.objects(is_active=True).count(),
            "pending_pos": 0,  # TODO: replace with actual count
        },
        "recent_work_orders": WorkOrderDoc.objects().all(),  # TODO: replace with actual data

    }
    return render_template('dashboard.html', **context)

@main_bp.route('/employees_list')
@login_required
def employees_list():
    return render_template('employees_list.html')

@main_bp.route('/employees_new')
@login_required
def employees_new():
    return render_template('employees_new.html')

@main_bp.route('/grn_new')
@login_required
def grn_new():
    return render_template('grn_new.html')

@main_bp.route('/inspections_list')
@login_required
def inspections_list():
    return render_template('inspections_list.html')

@main_bp.route('/inspections_new')
@login_required
def inspections_new():
    return render_template('inspections_new.html')

@main_bp.route('/inventory_raw_materials')
@login_required
def inventory_raw_materials():
    return render_template('inventory_raw_materials.html')

@main_bp.route('/job_cards_list')
@login_required
def job_cards_list():
    return render_template('job_cards_list.html')

# NOTE: this is the HTML page for machines list (template link in base.html)
@main_bp.route('/machines_list')
@login_required
def machines_list():
    return render_template('machines_list.html')

@main_bp.route('/machines_new')
@login_required
def machines_new():
    return render_template('machines_new.html')

@main_bp.route('/products_list')
@login_required
def products_list():
    return render_template('products_list.html')

@main_bp.route('/products_new')
@login_required
def products_new():
    return render_template('products_new.html')

@main_bp.route('/purchase_orders_list')
@login_required
def purchase_orders_list():
    return render_template('purchase_orders_list.html')

@main_bp.route('/purchase_orders_new')
@login_required
def purchase_orders_new():
    return render_template('purchase_orders_new.html')

@main_bp.route('/reports_dashboard')
@login_required
def reports_dashboard():
    return render_template('reports_dashboard.html')

@main_bp.route('/sales_orders_list')
@login_required
def sales_orders_list():
    return render_template('sales_orders_list.html')

@main_bp.route('/sales_orders_new')
@login_required
def sales_orders_new():
    return render_template('sales_orders_new.html')

@main_bp.route('/tool_issuances_list')
@login_required
def tool_issuances_list():
    return render_template('tool_issuances_list.html')

@main_bp.route('/tool_issuances_new')
@login_required
def tool_issuances_new():
    return render_template('tool_issuances_new.html')

@main_bp.route('/tools_list')
@login_required
def tools_list():
    return render_template('tools_list.html')

@main_bp.route('/tools_new')
@login_required
def tools_new():
    return render_template('tools_new.html')

@main_bp.route('/vendors_list')
@login_required
def vendors_list():
    return render_template('vendors_list.html')

@main_bp.route('/vendors_new')
@login_required
def vendors_new():
    return render_template('vendors_new.html')

@main_bp.route('/work_orders_list')
@login_required
def work_orders_list():
    return render_template('production/work_orders.html')


@main_bp.route('/work_orders_new', methods=['GET', 'POST'])
@login_required
def work_orders_new():
    form = WorkOrderForm()
    # Populate product choices
    form.product_id.choices = [(str(i.id), i.name) for i in InventoryItemDoc.objects()]

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        form = WorkOrderForm(data=data)
        form.product_id.choices = [(str(i.id), i.name) for i in InventoryItemDoc.objects()]

        if form.validate_on_submit():
            # Fetch referenced InventoryItemDoc
            item_doc = InventoryItemDoc.objects(id=form.product_id.data).first()
            if not item_doc:
                form.product_id.errors.append("Invalid product selected.")
                return render_template('production/work_order_form.html', form=form, title="New Work Order")

            work_order = WorkOrderDoc(
                work_order_number=form.work_order_number.data,
                item=item_doc,
                quantity=form.quantity_ordered.data,
                # You can add unit if you want, e.g., unit=unit_doc,
                start_date=form.planned_start_date.data,
                due_date=form.planned_end_date.data,
                status=form.status.data
            )
            work_order.save()
            return redirect(url_for('main.work_orders_list'))
        else:
            # Optionally print or flash form.errors for debugging
            print(form.errors)

    return render_template('production/work_order_form.html', form=form, title="New Work Order")

# @main_bp.route('/work_orders_new')
# @login_required
# def work_orders_new():
#     form = WorkOrderForm()

#     if request.method == 'POST':

#         data = request.get_json(silent=True) or request.form

#         # Fetch referenced documents
#         item_doc = InventoryItemDoc.objects(id=data.get('item')).first()
#         unit_doc = UnitDoc.objects(id=data.get('unit')).first()

#         if form.validate_on_submit():
#             # Create a new WorkOrderDoc instance
#             work_order = WorkOrderDoc(
#                 work_order_number=form.work_order_number.data,
#                 item=form.item.data,
#                 quantity=form.quantity.data,
#                 unit=form.unit.data,
#                 start_date=form.start_date.data,
#                 due_date=form.due_date.data
#             )
#             work_order.save()
#             return redirect(url_for('main.work_orders_list'))

#     return render_template('production/work_order_form.html', form=form, title="New Work Order")
