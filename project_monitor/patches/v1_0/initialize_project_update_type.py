import frappe


def execute():
    items = [
        ["Project Kickoff", True, False],
        ["Milestone Achievement", True, True],
        ["Implementation Progress", True, True],
        ["Project Handover", True, False],
        ["Public Inspection", True, False],
        ["Public Participation", True, False],
    ]
    doctype = "ProjectX Update Type"
    for itm in items:
        exists = frappe.db.exists(doctype, itm[0])
        if exists:
            continue
        frappe.get_doc(
            {
                "doctype": doctype,
                "update_type": itm[0],
                "is_visible_to_public": itm[1],
                "is_updating_project_progress": itm[2],
            }
        ).insert(ignore_permissions=True)
