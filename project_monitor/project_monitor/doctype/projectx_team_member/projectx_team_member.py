# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXTeamMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		full_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project_team_role: DF.Link
		telephone_number: DF.Data | None
	# end: auto-generated types
	pass
