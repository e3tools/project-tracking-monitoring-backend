# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PartnerX(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		partner_name: DF.Data
		partner_type: DF.Literal["", "NGO", "CSO", "International Agency"]
	# end: auto-generated types
	pass
