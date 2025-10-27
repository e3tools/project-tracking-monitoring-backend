# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXTeam(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		members: DF.Table[Document]
		project: DF.Link | None
		project_location: DF.ReadOnly | None
		project_name: DF.ReadOnly | None
		project_status: DF.ReadOnly | None
	# end: auto-generated types
	pass
