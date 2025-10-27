import frappe


def execute():
    roles = [
        "Project Sponsor",
        "Project Manager",
        "Team Member",
        "Subject Matter Expert",
        "Steering Committee",
        "Project Stakeholder",
    ]
    for role in roles:
        exists = frappe.db.exists("ProjectX Team Role", role)
        if exists:
            continue
        doc = frappe.new_doc(
            {"doctype": "ProjectX Team Role", "project_team_role": role}
        ).insert(ignore_permissions=True)
