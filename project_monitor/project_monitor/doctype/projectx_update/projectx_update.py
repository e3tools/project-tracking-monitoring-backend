# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today
from frappe import _


class ProjectXUpdate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        is_project_progress: DF.Check
        is_visible_to_public: DF.Check
        naming_series: DF.Data | None
        posting_date: DF.Date
        progress: DF.Percent
        project: DF.Link
        project_location: DF.ReadOnly | None
        project_name: DF.ReadOnly | None
        project_status: DF.ReadOnly | None
        project_update_type: DF.Link
        remarks: DF.SmallText | None
    # end: auto-generated types
    pass

    def validate(self):
        if not 0 <= flt(self.progress) <= 100:
            frappe.throw(_("The value of Progress must be between 0 and 100"))
        if getdate(self.posting_date) > getdate(today()):
            frappe.throw(_("Posting Date cannot be later than today"))
