# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from project_monitor.utils import recalculate_project_metrics


class ProjectXPaymentCertificate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

    # end: auto-generated types
    pass

    def validate(self):
        """Validate amounts and calculate net payable."""
        if flt(self.gross_certified_amount) <= 0:
            frappe.throw(_("Gross Certified Amount must be greater than zero."))

        if flt(self.retention_amount) < 0:
            frappe.throw(_("Retention Amount cannot be negative."))

        if flt(self.retention_amount) > flt(self.gross_certified_amount):
            frappe.throw(_("Retention Amount cannot exceed Gross Certified Amount."))

        self.net_payable_amount = flt(self.gross_certified_amount) - flt(
            self.retention_amount
        )

    def on_submit(self):
        """Update parent ProjectX totals on submission."""
        formatted_net = frappe.format_value(
            self.net_payable_amount, dict(fieldtype="Currency")
        )
        msg = _("Certified net payment of {0} via {1}").format(formatted_net, self.name)
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)
        # self.update_parent_project_totals()

    def on_cancel(self):
        """Recalculate parent ProjectX totals on cancellation."""
        msg = _("Cancelled payment certificate {0}").format(self.name)
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)
        # self.update_parent_project_totals()

    def update_parent_project_totals(self):
        """
        Recalculates aggregate certified amounts and pending liabilities
        for the linked ProjectX document.
        """
        if not self.project:
            return

        # 1. Calculate total net certified amount from all submitted certificates
        total_certified = (
            frappe.db.sql(
                """
			SELECT COALESCE(SUM(net_payable_amount), 0.0)
			FROM `tabProject Payment Certificate`
			WHERE project = %s AND docstatus = 1
		""",
                (self.project,),
            )[0][0]
            or 0.0
        )

        # 2. Get total actual expenditure paid to date on the project
        total_expenditure = (
            frappe.db.get_value("ProjectX", self.project, "total_expenditure") or 0.0
        )

        # 3. Pending Bills = Total Certified - Total Paid
        pending_bills = max(flt(total_certified) - flt(total_expenditure), 0.0)

        # 4. Fetch target ProjectX document object
        project_doc = frappe.get_doc("ProjectX", self.project)

        # 5. Attach in-memory updater reference flag for timeline logging
        formatted_net = frappe.format_value(
            self.net_payable_amount, dict(fieldtype="Currency")
        )
        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Certified Net Payment of {0} via {1}").format(
                formatted_net, self.name
            ),
        }

        # 6. Apply metric updates and save target document
        project_doc.total_certified_amount = total_certified
        project_doc.pending_bills_amount = pending_bills
        project_doc.flags.ignore_permissions = True
        project_doc.save()

        # Trigger UI refresh on open forms
        frappe.publish_realtime(
            "doc_update",
            {"doctype": "ProjectX", "name": self.project},
            after_commit=True,
        )
