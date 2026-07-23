import frappe


def execute():
    items = [
        ["Ongoing", "Info", "Ongoing"],
        ["Not Started", "Warning", "Not Started"],
        ["Complete", "Success", "Completed"],
        ["Stalled", "Danger", "Stalled"],
    ]
    doctype = "ProjectX Status"
    for itm in items:
        exists = frappe.db.exists(doctype, itm[0])
        if exists:
            continue
        frappe.get_doc(
            {
                "doctype": doctype,
                "status_name": itm[0],
                "theme": itm[1],
                "description": itm[2],
            }
        ).insert(ignore_permissions=True)
