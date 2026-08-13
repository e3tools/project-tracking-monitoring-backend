# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from project_monitor.project_monitor.doctype.projectx.projectx import (
    update_earned_value_and_pending_bills,
)
from frappe import _
from project_monitor.utils import recalculate_project_metrics
from frappe.utils import get_fullname


class ProjectXProgressReport(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        inspected_by: DF.Link | None
        inspection_date: DF.Date
        inspector_name: DF.Data | None
        is_public: DF.Check
        issues_flagged: DF.Check
        physical_progress_percent: DF.Percent
        project: DF.Link
        project_name: DF.ReadOnly | None
        remarks: DF.SmallText
        site_images: DF.AttachImage | None
        work_status: DF.Literal["On Schedule", "Ahead of Schedule", "Behind Schedule", "Stalled / Suspended"]
    # end: auto-generated types
    pass

    def has_permission(self, permtype="read", *, debug=False, user=None):
        """
        Ensure someone cannot directly view an internal report by guessing its URL
        """
        if not user:
            user = frappe.session.user

        # If user is Guest or external, allow access if is_public is checked
        if user == "Guest" or "Projects Portal User" in frappe.get_roles(user):
            if permtype == "read":
                return self.is_public == 1
            return False

        return True

    def validate(self):
        if self.inspected_by:
            self.inspector_name = get_fullname(self.inspected_by)
        if not self.inspector_name:
            self.inspector_name = "N/A"

    def on_submit(self):
        # self.update_parent_project()
        msg = _("Updated physical progress to {0}% via {1}").format(
            self.physical_progress_percent, self.name
        )
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)

    def on_cancel(self):
        msg = _("Cancelled progress report {0}").format(self.name)
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)
        # self.update_parent_project()

    def update_parent_project(self):
        """
        Fetches the latest submitted progress report for the linked project
        and updates the project's current physical progress metric.
        """
        latest_report = frappe.db.get_all(
            "ProjectX Progress Report",
            filters={"project": self.project, "docstatus": 1},
            fields=["physical_progress_percent", "inspection_date"],
            order_by="inspection_date desc, creation desc",
            limit=1,
        )

        if latest_report:
            progress = latest_report[0].physical_progress_percent
            last_date = latest_report[0].inspection_date
        else:
            progress = 0.0
            last_date = None

        # Fetch the target ProjectX document object
        project_doc = frappe.get_doc("ProjectX", self.project)

        # Set the in-memory updater reference flag on the target doc
        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Updated physical progress to {0}% via {1} {2}").format(
                self.physical_progress_percent, self.doctype, self.name
            ),
        }

        # frappe.db.set_value(
        #     "ProjectX",
        #     self.project,
        #     {
        #         "current_physical_progress": progress,
        #         "last_progress_update_date": last_date,
        #     },
        # )

        # Update actual values
        project_doc.current_physical_progress = progress
        project_doc.last_progress_update_date = last_date

        # Save target doc to trigger its validation & timeline hooks
        project_doc.save(ignore_permissions=True)

        update_earned_value_and_pending_bills(self.project)


def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    # Internal users see all records
    if user != "Guest" and "System Manager" in frappe.get_roles(user):
        return

    # Guests and external public users can only see records marked as public
    if user == "Guest" or "Projects Portal User" in frappe.get_roles(user):
        return "`tabProjectX Progress Report`.is_public = 1"

    return ""
