# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXGalleryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attach_file: DF.Attach
		caption: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		use_as_the_cover_image: DF.Check
	# end: auto-generated types
	pass
