# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXFeedbackResponse(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email: DF.ReadOnly | None
		feedback: DF.Link
		full_name: DF.ReadOnly | None
		is_anonymous: DF.Check
		is_public: DF.Check
		phone_number: DF.ReadOnly | None
		project: DF.Link | None
		project_name: DF.ReadOnly | None
		response: DF.SmallText | None
		subject: DF.ReadOnly | None
	# end: auto-generated types
	pass
