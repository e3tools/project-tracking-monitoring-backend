# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, date_diff, getdate


class ProjectXPostEvaluation(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        actual_completion_date: DF.Date
        amended_from: DF.Link | None
        approved_budget: DF.Currency
        budget_rating: DF.Literal[
            "5 - Outstanding",
            "4 - Exceeds Expectations",
            "3 - Satisfactory",
            "2 - Needs Improvement",
            "1 - Unsatisfactory",
        ]
        community_impact_rating: DF.Literal[
            "5 - Outstanding",
            "4 - Exceeds Expectations",
            "3 - Satisfactory",
            "2 - Needs Improvement",
            "1 - Unsatisfactory",
        ]
        cost_variance: DF.Currency
        department: DF.ReadOnly | None
        evaluation_date: DF.Date
        evaluator_name: DF.Data
        final_expenditure: DF.Currency
        is_project_serving_its_intended_purpose: DF.Check
        key_challenges: DF.SmallText | None
        lessons_learned: DF.SmallText | None
        objectives_achieved: DF.SmallText | None
        overall_rating: DF.Literal[
            "Highly Successful", "Successful", "Partially Successful", "Unsuccessful"
        ]
        planned_end_date: DF.Date | None
        project: DF.Link
        project_name: DF.ReadOnly | None
        quality_rating: DF.Literal[
            "5 - Outstanding",
            "4 - Exceeds Expectations",
            "3 - Satisfactory",
            "2 - Needs Improvement",
            "1 - Unsatisfactory",
        ]
        remarks: DF.SmallText | None
        schedule_rating: DF.Literal[
            "5 - Outstanding",
            "4 - Exceeds Expectations",
            "3 - Satisfactory",
            "2 - Needs Improvement",
            "1 - Unsatisfactory",
        ]
        schedule_variance_days: DF.Int
        sustainability_plan: DF.SmallText | None
    # end: auto-generated types

    def validate(self):
        """Perform validation checks before saving."""
        if not self.project:
            frappe.throw(_("Please select a target Project."))

        if getdate(self.actual_completion_date) > getdate(self.evaluation_date):
            frappe.throw(
                _("Evaluation Date cannot be prior to Actual Completion Date.")
            )

        # Calculate final cost variance (Budget - Actual Spent)
        self.cost_variance = flt(self.approved_budget) - flt(self.final_expenditure)

        # Calculate schedule variance in days
        if self.planned_end_date and self.actual_completion_date:
            self.schedule_variance_days = date_diff(
                self.actual_completion_date, self.planned_end_date
            )

    def on_submit(self):
        """Update parent ProjectX status and store evaluation details."""
        project_doc = frappe.get_doc("ProjectX", self.project)

        # Ensure project isn't evaluated twice concurrently
        if project_doc.status == "Evaluated":
            frappe.throw(
                _("Project {0} has already undergone Post Evaluation.").format(
                    self.project
                )
            )

        # Update ProjectX status and metrics
        # project_doc.status = "Evaluated"
        project_doc.is_evaluated = 1
        project_doc.post_evaluation_rating = self.overall_rating
        project_doc.actual_completion_date = self.actual_completion_date

        # Attach in-memory timeline update log
        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Completed Post-Implementation Evaluation ({0})").format(
                self.overall_rating
            ),
        }

        project_doc.flags.ignore_permissions = True
        project_doc.save()

        frappe.msgprint(
            _("Project {0} status updated to Evaluated.").format(self.project)
        )

    def on_cancel(self):
        """Revert parent ProjectX status upon evaluation cancellation."""
        project_doc = frappe.get_doc("ProjectX", self.project)
        # project_doc.status = "Completed"
        project_doc.is_evaluated = False
        project_doc.post_evaluation_rating = None

        project_doc.flags.updater_reference = {
            "doctype": self.doctype,
            "docname": self.name,
            "label": _("Cancelled Post Evaluation {0}").format(self.name),
        }

        project_doc.flags.ignore_permissions = True
        project_doc.save()
