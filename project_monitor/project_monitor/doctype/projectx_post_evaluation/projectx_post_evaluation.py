# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXPostEvaluation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		evaluation_date: DF.Date
		is_project_serving_its_intended_purpose: DF.Check
		project: DF.Link
		project_title: DF.ReadOnly | None
		remarks: DF.SmallText | None
	# end: auto-generated types
	pass
