# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectEx(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.model.document import Document
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.project_document_item_ex.project_document_item_ex import ProjectDocumentItemEx
        from project_monitor.project_monitor.doctype.projectx_location_item.projectx_location_item import ProjectXLocationItem

        admin_names: DF.SmallText | None
        administrative_areas: DF.Table[ProjectXLocationItem]
        administrative_level: DF.Literal["", "Admin 0", "Admin 1", "Admin 2"]
        department: DF.Link | None
        estimated_cost: DF.Currency
        expected_end_date: DF.Date | None
        expected_start_date: DF.Date | None
        implemented_by: DF.Literal["", "County Government", "Partner"]
        joint_inspection_report: DF.Table[ProjectDocumentItemEx]
        partner: DF.Link | None
        pmc_members: DF.Table[Document]
        project_name: DF.Data
        project_scope: DF.TextEditor | None
        status: DF.Link | None
    # end: auto-generated types

    def validate(self):
        frappe.rename_doc("DocType", "Project Ex", "ProjectX", True)
        self.admin_names = ",".join([x.admin for x in self.administrative_areas])

    @frappe.whitelist(allow_guest=True)
    def get_vector(self, doctype, docname):
        geom = frappe.db.get_value(doctype, docname, "geom")
        return geom
