import os

templates_dir = os.path.join(os.getcwd(), "templates")
print(f"📂 Templates directory: {templates_dir}")
os.makedirs(templates_dir, exist_ok=True)

pages = [
    "employees_list.html", "employees_new.html",
    "customers_list.html", "customers_new.html",
    "machines_list.html", "machines_new.html",
    "products_list.html", "products_new.html",
    "purchase_orders_list.html", "purchase_orders_new.html",
    "sales_orders_list.html", "sales_orders_new.html",
    "vendors_list.html", "vendors_new.html",
    "tools_list.html", "tools_new.html",
    "tool_issuances_list.html", "tool_issuances_new.html",
    "work_orders_list.html", "work_orders_new.html",
    "job_cards_list.html", "grn_new.html",
    "inspections_list.html", "inspections_new.html",
    "inventory_raw_materials.html", "reports_dashboard.html",
    "dashboard.html", "index.html"
]

for page in pages:
    path = os.path.join(templates_dir, page)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(f"<h1>{page.replace('_', ' ').title()}</h1>\n<p>Placeholder page</p>")
        print(f"✅ Created: {page}")
    else:
        print(f"✔ Exists: {page}")

print("\n🎯 All templates ready!")
