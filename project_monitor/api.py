import frappe
import json


@frappe.whitelist(allow_guest=True)
def submit_feedback(feedback=None):
    if isinstance(feedback, str):
        feedback = json.loads(feedback)
    vals = frappe._dict(feedback)  # frappe.form_dict
    doc = frappe.new_doc("ProjectX Feedback")
    doc.update(
        {
            "subject": vals.subject,
            # "attachment": vals.attach_file,
            "project": vals.project,
            "project_name": vals.project_name,
            "is_public": True,
            "email": vals.email,
            "full_name": vals.full_name,
            "phone_number": vals.phone_number,
            "description": vals.feedback,
            "is_group": vals.is_group or True,
            "parent_projectx_feedback": vals.parent,
        }
    )
    res = doc.insert(ignore_permissions=True)
    return res
