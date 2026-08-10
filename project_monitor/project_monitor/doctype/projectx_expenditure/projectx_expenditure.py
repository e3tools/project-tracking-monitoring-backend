# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from project_monitor.project_monitor.doctype.projectx.projectx import (
    update_earned_value_and_pending_bills,
)
from frappe import _
from project_monitor.utils import recalculate_project_metrics


class ProjectXExpenditure(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Currency
        expense_category: DF.Link
        posting_date: DF.Date
        project: DF.Link
        project_title: DF.ReadOnly | None
        remarks: DF.SmallText | None
        supporting_documents: DF.Attach | None
        voucher_reference: DF.Data
    # end: auto-generated types
    pass

    def on_submit(self):
        formatted_amount = frappe.format_value(self.amount, dict(fieldtype="Currency"))
        msg = _("Logged expenditure of {0} via {1}").format(formatted_amount, self.name)
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)
        # self.update_project_totals()

    def on_cancel(self):
        msg = _("Cancelled expenditure record {0}").format(self.name)
        recalculate_project_metrics(self.project, source_doc=self, update_message=msg)
        # self.update_project_totals()

    def update_project_totals(self):
        # Calculate total expenditure for the linked project
        total_expenditure = (
            frappe.db.sql(
                """
			SELECT SUM(amount) 
			FROM `tabProject Expenditure` 
			WHERE project = %s AND docstatus = 1
		""",
                self.project,
            )[0][0]
            or 0.0
        )

        # Fetch approved budget to compute financial progress
        approved_budget = (
            frappe.db.get_value("ProjectX", self.project, "approved_budget") or 1.0
        )
        financial_progress = (total_expenditure / approved_budget) * 100
        project_balance = approved_budget - total_expenditure

        # Fetch the target ProjectX document object
        project_doc = frappe.get_doc("ProjectX", self.project)

        # Set the in-memory updater reference flag on the target doc
        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Updated via {0} {1}").format(self.doctype, self.name),
        }
        # Update ProjectX master document
        project_doc.total_expenditure_amount = total_expenditure
        project_doc.financial_progress_percent = min(financial_progress, 100.0)
        project_doc.project_balance = project_balance

        # Save target doc to trigger its validation & timeline hooks
        project_doc.save(ignore_permissions=True)

        # frappe.db.set_value(
        # 	"ProjectX",
        # 	self.project,
        # 	{
        # 		"total_expenditure_amount": total_expenditure,
        # 		"financial_progress_percent": min(financial_progress, 100.0),
        # 		"project_balance": project_balance,
        # 	},
        # )

        update_earned_value_and_pending_bills(self.project)
