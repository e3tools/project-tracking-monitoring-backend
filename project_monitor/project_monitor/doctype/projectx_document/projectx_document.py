# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXDocument(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attach_file: DF.Attach
		document_type: DF.Link
		is_public: DF.Check
		naming_series: DF.Data | None
		project: DF.Link
		project_location: DF.ReadOnly | None
		project_status: DF.ReadOnly | None
		project_title: DF.ReadOnly | None
		remarks: DF.SmallText | None
	# end: auto-generated types
	pass
