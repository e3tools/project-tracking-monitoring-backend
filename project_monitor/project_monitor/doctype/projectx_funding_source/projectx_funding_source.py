# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXFundingSource(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		funded_by: DF.Literal["", "County Government", "Partner", "Local Organization"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		partner: DF.Link | None
		percentage_of_funding: DF.Percent
	# end: auto-generated types
	pass
