# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		creator: DF.Link | None
		creator_full_name: DF.ReadOnly | None
		details: DF.Text | None
		is_project_progress: DF.Check
		posting_date: DF.Date
		progress: DF.Percent
		project: DF.Link
		project_location: DF.ReadOnly | None
		project_log_entry_type: DF.Link
		project_name: DF.ReadOnly | None
		project_status: DF.ReadOnly | None
	# end: auto-generated types
	pass
