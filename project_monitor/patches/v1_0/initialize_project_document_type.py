import frappe


def execute():
    types = [
        "Site Inspection Report",
        "Feasibility Study",
        "Meeting Minutes",
        "Vendor Contract",
        "Purchase Order",
        "Invoice",
        "Quality Audit Report",
        "Project Handover Document",
        "Project Closure Certificate",
    ]
    doctype = "ProjectX Document Type"
    for itm in types:
        exists = frappe.db.exists(doctype, itm)
        if exists:
            continue
        frappe.get_doc({"doctype": doctype, "document_type": itm}).insert(
            ignore_permissions=True
        )
