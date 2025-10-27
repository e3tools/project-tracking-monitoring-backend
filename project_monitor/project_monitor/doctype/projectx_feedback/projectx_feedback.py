# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXFeedback(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attachment: DF.Attach | None
		description: DF.Text
		email: DF.Data | None
		full_name: DF.Data | None
		is_group: DF.Check
		is_public: DF.Check
		lft: DF.Int
		old_parent: DF.Link | None
		parent_projectx_feedback: DF.Link | None
		phone_number: DF.Data | None
		project: DF.Link | None
		project_name: DF.ReadOnly | None
		rgt: DF.Int
		subject: DF.Data
	# end: auto-generated types
	pass
