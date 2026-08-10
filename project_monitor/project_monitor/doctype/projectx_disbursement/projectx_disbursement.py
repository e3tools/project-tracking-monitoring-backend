# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ProjectXDisbursement(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Currency
        disbursement_date: DF.Date
        funding_source: DF.Link
        is_partner: DF.Check
        partner: DF.Link | None
        payment_reference: DF.Data
        project: DF.Link
        project_title: DF.ReadOnly | None
        remarks: DF.SmallText | None
    # end: auto-generated types
    pass

    def validate(self):
        """Pre-submission validations"""
        self.validate_disbursement_amount()

    def on_submit(self):
        """Update parent ProjectX total disbursements upon submission."""
        self.update_project_disbursement_totals()

    def on_cancel(self):
        """Recalculate parent ProjectX total disbursements upon cancellation."""
        self.update_project_disbursement_totals()

    def validate_disbursement_amount(self):
        """Ensures disbursement amount is positive and warns/blocks if it exceeds budget."""
        if self.amount <= 0:
            frappe.throw(_("Disbursement amount must be greater than zero."))

        # Fetch current project budget details
        project_data = frappe.db.get_value(
            "ProjectX",
            self.project,
            ["approved_budget", "total_disbursed_amount"],
            as_dict=True,
        )

        if not project_data:
            frappe.throw(_("Project {0} not found.").format(self.project))

        # validate source
        project_doc = frappe.get_doc("ProjectX", self.project)
        source_types = [x.funded_by for x in project_doc.source_of_funds]
        if self.funding_source not in source_types:
            frappe.throw(
                _(
                    "Funding Source Type {0} is not part of the source of funds for this project"
                ).format(frappe.bold(self.funding_source))
            )
        else:
            # if is partner
            if self.is_partner:
                partners = [
                    x.partner for x in project_doc.source_of_funds if x.is_partner
                ]
                if self.partner not in partners:
                    _(
                        "Partner {0} is not part of the source of funds for this project"
                    ).format(frappe.bold(self.partner))

        approved_budget = project_data.approved_budget or 0.0
        current_total = project_data.total_disbursed_amount or 0.0

        # Calculate pending new total (exclude current doc's old amount if modifying draft)
        new_total = current_total + self.amount

        if approved_budget > 0 and new_total > approved_budget:
            excess_amount = new_total - approved_budget
            frappe.msgprint(
                _(
                    "Warning: Total disbursements ({0}) will exceed the approved budget ({1}) by {2}."
                ).format(
                    frappe.format_value(new_total, dict(fieldtype="Currency")),
                    frappe.format_value(approved_budget, dict(fieldtype="Currency")),
                    frappe.format_value(excess_amount, dict(fieldtype="Currency")),
                ),
                alert=True,
                indicator="orange",
            )

    def update_project_disbursement_totals(self):
        """
        Calculates the aggregate sum of all submitted disbursements for the
        associated ProjectX document and updates the project fields.
        """
        if not self.project:
            return
        # Sum all submitted (docstatus = 1) disbursements for this project
        result = frappe.db.sql(
            """
			SELECT COALESCE(SUM(amount), 0.0)
			FROM `tabProjectX Disbursement`
			WHERE project = %s AND docstatus = 1
		""",
            (self.project,),
        )

        total_disbursed = result[0][0] if result else 0.0

        # Get total budget to update disbursement coverage percentage
        approved_budget = (
            frappe.db.get_value("ProjectX", self.project, "approved_budget") or 0.0
        )

        disbursement_coverage = 0.0
        if approved_budget > 0:
            disbursement_coverage = (total_disbursed / approved_budget) * 100.0

        # Fetch the target ProjectX document object
        project_doc = frappe.get_doc("ProjectX", self.project)

        # Set the in-memory updater reference flag on the target doc
        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Updated disbursement via {0} {1}").format(
                self.doctype, self.name
            ),
        }
        # Update ProjectX master document
        project_doc.total_disbursed_amount = total_disbursed
        project_doc.percent_disbursed_amount = min(100.0, disbursement_coverage)

        # Save target doc to trigger its validation & timeline hooks
        project_doc.save(ignore_permissions=True)

        # # Atomic update directly to the ProjectX table
        # frappe.db.set_value(
        # 	"ProjectX",
        # 	self.project,
        # 	{
        # 		"total_disbursed_amount": total_disbursed,
        # 		"percent_disbursed_amount": min(100.0, disbursement_coverage),
        # 	},
        # )

        # Publish a realtime UI update event to refresh open ProjectX forms
        frappe.publish_realtime(
            "doc_update",
            {"doctype": "ProjectX", "name": self.project},
            after_commit=True,
        )
