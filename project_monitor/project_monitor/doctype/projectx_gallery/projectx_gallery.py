# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import get_file_name
from frappe import _


class ProjectXGallery(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.projectx_gallery_item.projectx_gallery_item import (
            ProjectXGalleryItem,
        )

        amended_from: DF.Link | None
        description: DF.SmallText
        items: DF.Table[ProjectXGalleryItem]
        project: DF.Link
        project_title: DF.ReadOnly | None
    # end: auto-generated types
    pass

    def on_submit(self):
        cover_images = [x for x in self.items if x.is_cover_image]
        if cover_images:
            is_image = (
                cover_images[0]
                .attach_file.lower()
                .endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"))
            )
            if is_image:
                # Instead of unsetting the other cover_images, leave them as they are
                # to ensure if a Gallery record is cancelled, then we can use those that have remained
                # # Unset 'is_cover_image' on other gallery items for this project

                # frappe.db.sql(
                #     """UPDATE `tabProjectX Gallery Item` AS c
                # 	INNER JOIN `tabProjectX Gallery` AS p
                # 	ON p.name = c.parent
                # 	SET c.is_cover_image = 0
                # 	WHERE p.project = %s AND c.name != %s""",
                #     (self.project, cover_images[0].name),
                # )

                self.update_cover_image(
                    project=cover_images[0].project,
                    image_file=cover_images[0].attach_file,
                    message=_("Updated Cover Image via {} {}").format(
                        self.doctype, self.name
                    ),
                )

                project = frappe.get_doc("ProjectX", self.project)
                if project.cover_image != cover_images[0].attach_file:
                    project.cover_image = cover_images[0].attach_file

                    project.flags.updater_reference = {
                        "doctype": self.doctype,
                        "docname": self.name,
                        "label": _("Updated Cover Image via {} {}").format(
                            self.doctype, self.name
                        ),
                    }
                    project.save(ignore_permissions=True)

    def on_cancel(self):
        cover_images = [x for x in self.items if x.is_cover_image]
        if cover_images:
            # check if there are other gallery items that have is_cover
            items = frappe.db.sql(
                """select p.name as parent, p.project, c.name as item, c.attach_file
						from `tabProjectX Gallery Item` c 
						INNER JOIN `tabProjectX Gallery` p 
						ON c.parent = p.name
						WHERE c.is_cover_image = 1 and p.docstatus=1 and p.project=%s
			""",
                (self.project),
                as_dict=True,
            )
            if items:
                item = items[0]
                self.update_cover_image(
                    project=item.project,
                    image_file=item.attach_file,
                    message=_("Updated Cover Image on Cancelling {} {}").format(
                        self.doctype, self.name
                    ),
                )
            else:
                # Get default image
                default_image = frappe.db.get_singles_value(
                    "Project Monitor Settings", "default_cover_image"
                )
                self.update_cover_image(
                    project=item.project,
                    image_file=default_image,
                    message=_(
                        "Updated To Default Cover Image on Cancelling {} {}"
                    ).format(self.doctype, self.name),
                )

    def update_cover_image(self, project, image_file, message):
        """Update the main Project DocType's cover image directly"""
        project = frappe.get_doc("ProjectX", project)
        if project.cover_image != image_file:
            project.cover_image = image_file
            # Update the main Project DocType's cover image directly
            project.flags.updater_reference = {
                "doctype": self.doctype,
                "docname": self.name,
                "label": message,
            }
            project.save(ignore_permissions=True)
