import frappe
import json


@frappe.whitelist(allow_guest=True)
def submit_feedback(feedback=None):
    feedback = frappe.form_dict or feedback
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
            "description": vals.description,
            "is_group": vals.is_group or True,
            "parent_projectx_feedback": vals.parent,
            "category": vals.category,
            "status": "Submitted",
        }
    )
    # append attachments
    if vals.attachments:
        for itm in vals.attachments:
            doc.append(
                "attachments",
                {
                    "doctype": "ProjectX Feedback Attachment Item",
                    "attachment": itm.get("attachment"),
                    "attachment_type": itm.get("attachment_type") or "File",
                    "attachment_name": itm.get("attachment_name"),
                },
            )
    res = doc.insert(ignore_permissions=True)
    return res


@frappe.whitelist(allow_guest=True)
def upload_file():
    if "filedata" in frappe.form_dict:
        import base64
        from frappe.utils import cint

        # 1. Decode the string received from the ReactUI
        file_bytes = base64.b64decode(frappe.form_dict.filedata)
        file_type = frappe.form_dict.filetype
        filename = frappe.form_dict.filename or f"audio.{file_type}"

        # 2. Directly call the low-level File document generator (bypasses UI MIME filters)
        file_doc = frappe.get_doc(
            (
                {
                    "doctype": "File",
                    "file_name": filename,
                    "content": file_bytes,
                    "attached_to_doctype": frappe.form_dict.doctype,
                    "attached_to_name": frappe.form_dict.docname,
                    "is_private": cint(frappe.form_dict.is_private, 0),
                }
            )
        )
        file_doc.insert(ignore_permissions=True)

        frappe.response["message"] = {
            "success": True,
            "file_url": file_doc.file_url,
            "name": file_doc.name,
        }
    else:
        frappe.throw("Missing file data parameter")


@frappe.whitelist(allow_guest=True)
def get_doc_list(
    doctype: str, fields=None, filters=None, limit=0, order_by="creation desc"
):
    # if isinstance(fields, str):
    #     fields = json.loads(fields)

    # if isinstance(filters, str):
    #     filters = json.loads(filters)

    fields = json.loads(fields) if fields else ["name"]
    filters = json.loads(filters) if filters else {}

    # frappe.get_all will not check for permissions as opposed to frappe.get_list
    return frappe.get_all(
        doctype,
        fields=fields or ["name"],
        filters=filters or {},
        order_by=order_by,
        limit=int(limit),
    )
