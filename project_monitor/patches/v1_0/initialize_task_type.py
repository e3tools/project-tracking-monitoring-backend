import frappe


def execute():
    types = [
        "Planning",
        "Execution",
        "Handover",
    ]
    for itm in types:
        exists = frappe.db.exists("TaskX Type", itm)
        if exists:
            continue
        frappe.get_doc({"doctype": "TaskX Type", "task_type": itm}).insert(
            ignore_permissions=True
        )
