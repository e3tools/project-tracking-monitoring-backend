# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectXFeedback(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.projectx_feedback_attachment_item.projectx_feedback_attachment_item import ProjectXFeedbackAttachmentItem

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
        status: DF.Literal["", "Submitted", "Under Review", "Action In Progress", "Awaiting Information", "Resolved", "Closed", "Not Actionable"]
        subject: DF.Data
    # end: auto-generated types
    pass


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
