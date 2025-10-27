import frappe


def execute():
    items = [
        "Open",
        "In Progress",
        "Overdue",
        "Completed",
        "Cancelled",
    ]
    for itm in items:
        exists = frappe.db.exists("TaskX Status", itm)
        if exists:
            continue
        doc = frappe.new_doc({"doctype": "TaskX Status", "task_status": itm}).insert(
            ignore_permissions=True
        )
