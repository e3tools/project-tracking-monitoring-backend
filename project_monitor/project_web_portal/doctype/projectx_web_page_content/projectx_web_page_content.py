# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ProjectXWebPageContent(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_web_portal.doctype.projectx_web_page_content_item.projectx_web_page_content_item import (
            ProjectXWebPageContentItem,
        )

        web_page: DF.Literal["", "Home Page", "Projects Search Page"]
        web_page_content_items: DF.Table[ProjectXWebPageContentItem]
        web_page_title: DF.Data | None
    # end: auto-generated types
    pass

    def validate(self):
        # check duplicate page
        exists = frappe.db.exists(
            self.doctype, {"web_page": self.web_page, "name": ("!=", self.name)}
        )
        if exists:
            frappe.throw(
                _(
                    f"Another record for Web Page {self.web_page} has been already been defined"
                )
            )
        # check duplicate content items
        for item in self.web_page_content_items:
            lst = [
                x.idx
                for x in self.web_page_content_items
                if x.content_title == item.content_title
            ]
            if len(lst) > 1:
                frappe.throw(
                    _(
                        f"Content Title [{frappe.bold(item.content_title)}] has been specified more than once in rows {lst}"
                    )
                )
