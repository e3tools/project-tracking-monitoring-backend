# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.core.doctype.sms_settings.sms_settings import send_sms


class ProjectXFeedback(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.projectx_feedback_attachment_item.projectx_feedback_attachment_item import (
            ProjectXFeedbackAttachmentItem,
        )

        attachments: DF.Table[ProjectXFeedbackAttachmentItem]
        category: DF.Literal["", "Complaint", "Suggestion", "Inquiry", "Appreciation"]
        description: DF.SmallText
        email: DF.Data | None
        full_name: DF.Data | None
        is_anonymous: DF.Check
        is_public: DF.Check
        naming_series: DF.Data | None
        phone_number: DF.Data | None
        project: DF.Link
        project_name: DF.ReadOnly | None
        status: DF.Literal[
            "",
            "Submitted",
            "Under Review",
            "Action In Progress",
            "Awaiting Information",
            "Resolved",
            "Closed",
            "Not Actionable",
        ]
        subject: DF.Data
    # end: auto-generated types
    pass


def send_feedback_alert(doc, method):
    # Prepare Recipient Email & Phone
    recipient_email = doc.email  # frappe.db.get_value("User", doc.owner, "email")
    # phone_number = (
    #     doc.phone_number
    # )  # doc.contact_phone if hasattr(doc, "contact_phone") else None
    contact_phone = doc.phone_number

    if not recipient_email:
        # Option A: Get email of the Project Lead / Manager from ProjectX
        if hasattr(doc, "project") and doc.project:
            recipient_email = frappe.db.get_value(
                "ProjectX", doc.project, "project_lead_email"
            )

        if not recipient_email:
            # Option B: Ultimate fallback to System Manager / Administrator
            recipient_email = frappe.db.get_value(
                "User", {"enabled": 1, "name": "Administrator"}, "email"
            )

        if not recipient_email:
            frappe.log_error(
                f"No recipient email for feedback notification for project {doc.project_name}",
                title="Feedback Alert Warning",
            )

    if recipient_email:
        # 2. Extract Submitter Identity (Anonymous vs Logged-In)
        is_guest = doc.owner == "Guest" or not doc.owner
        submitter_name = getattr(doc, "full_name", None) or (
            "Anonymous User" if is_guest else doc.owner
        )

        # 3. Construct and Send Email
        subject = f"New Feedback Received: {doc.name} for {doc.project or 'General'}"
        message = f"""
                <h3>New Project Feedback Submitted</h3>
                <p><strong>Project:</strong> {doc.project_name or 'N/A'}</p>
                <p><strong>Submitted On:</strong> {getdate(doc.creation)}</p>
                <p><strong>Submitted By:</strong> {submitter_name} {'(Anonymous)' if is_guest else ''}</p>
                <p><strong>Contact Phone:</strong> {contact_phone or 'Not provided'}</p>
                <hr>
                <p><strong>Feedback Content:</strong> {doc.description}</p> 
                <blockquote>{getattr(doc, 'description', 'No message provided.')}</blockquote>
            """

        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            now=True,
        )

    # Send SMS (Only if phone number was provided during submission)
    if contact_phone:
        sms_text = (
            f"New Feedback ({doc.name}) submitted for {doc.project or 'Project'}."
        )
        try:
            send_sms(receiver_list=[contact_phone], msg=sms_text)
        except Exception as e:
            frappe.log_error(message=str(e), title="SMS Notification Failed")


# if "filedata" in frappe.form_dict:
# 	import base64
# 	from frappe.utils import cint

# 	# 1. Decode the string received from the ReactUI
# 	file_bytes = base64.b64decode(frappe.form_dict.filedata)
# 	filename = frappe.form_dict.filename or "audio.mp3"

# 	# 2. Directly call the low-level File document generator (bypasses UI MIME filters)
# 	file_doc = frappe.get_doc(({
# 		"doctype": "File",
# 		"file_name": filename,
# 		"content": file_bytes,
# 		"attached_to_doctype": frappe.form_dict.doctype,
# 		"attached_to_name": frappe.form_dict.docname,
# 		"is_private": cint(frappe.form_dict.is_private, 0)
# 	}))
# 	file_doc.insert(ignore_permissions=True)

# 	frappe.response["message"] = {
# 		"success": True,
# 		"file_url": file_doc.file_url,
# 		"name": file_doc.name
# 	}
# else:
# 	frappe.throw("Missing file data parameter")
