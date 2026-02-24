# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXPMCMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		designation: DF.Literal["", "Chairperson", "Secretary", "Treasurer", "Member"]
		full_name: DF.Data
		gender: DF.Link
		group_representing: DF.Literal["", "Faith Based Organization", "PWD", "Youth", "Women", "Professional", "Development Committee", "Special Committee"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		telephone_number: DF.Data
	# end: auto-generated types
	pass
