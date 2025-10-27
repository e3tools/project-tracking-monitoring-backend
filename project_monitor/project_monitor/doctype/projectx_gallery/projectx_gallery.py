# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXGallery(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from project_monitor.project_monitor.doctype.projectx_gallery_item.projectx_gallery_item import ProjectXGalleryItem

		description: DF.SmallText
		items: DF.Table[ProjectXGalleryItem]
		project: DF.Link
		project_title: DF.ReadOnly | None
	# end: auto-generated types
	pass
