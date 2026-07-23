import frappe


def execute():
    roles = [
        "Project Sponsor",
        "Project Manager",
        "Project Member",
        "Project Lead",
        "Subject Matter Expert",
        "Steering Committee",
        "External Stakeholder",
    ]
    doctype = "ProjectX Team Role"
    for role in roles:
        exists = frappe.db.exists(doctype, role)
        if exists:
            continue
        frappe.get_doc({"doctype": doctype, "project_team_role": role}).insert(
            ignore_permissions=True
        )
