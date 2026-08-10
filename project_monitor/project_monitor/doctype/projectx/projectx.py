# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate
import json
from frappe.utils import get_link_to_form


class ProjectX(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.projectx_funding_source.projectx_funding_source import ProjectXFundingSource
        from project_monitor.project_monitor.doctype.projectx_location_item.projectx_location_item import ProjectXLocationItem

        actual_end_date: DF.Date | None
        admin_names: DF.SmallText | None
        administrative_areas: DF.Table[ProjectXLocationItem]
        administrative_level: DF.Literal["", "Admin 0", "Admin 1", "Admin 2", "Admin 3"]
        amount_paid: DF.Currency
        amount_to_complete_stalled_project: DF.Int
        approval_date: DF.Date
        approval_number: DF.Data | None
        approved_budget: DF.Currency
        available_funds: DF.Currency
        climate_and_disaster_risk_reasons_for_not_screening: DF.SmallText | None
        climate_disaster_risk_mitigation: DF.SmallText | None
        completion_level: DF.Percent
        contract_period: DF.Int
        contractor_name: DF.Data
        county_government_cost_component: DF.Currency
        current_financial_progress: DF.Percent
        current_physical_progress: DF.Percent
        department: DF.Link | None
        development_partner_cost_component: DF.Currency
        environment_social_health_gender_risk_mitigation: DF.SmallText | None
        environment_social_health_gender_risk_reasons_for_not_screening: DF.SmallText | None
        estimated_cost: DF.Currency
        expected_end_date: DF.Date | None
        expected_start_date: DF.Date | None
        financial_year: DF.Link
        has_been_screened_for_climate_and_disaster_risks: DF.Check
        has_been_screened_for_environment_social_health_gender_risks: DF.Check
        has_been_screened_for_technical_financial_economic_viability: DF.Check
        health_status: DF.Literal["On Track", "Delayed", "Budget Exceeded", "Stalled"]
        implemented_by: DF.Literal["", "County Government", "Partner", "Local Organization"]
        is_handed_over: DF.Check
        is_project_in_budget: DF.Check
        last_progress_update_date: DF.Date | None
        latitude: DF.Float
        longitude: DF.Float
        months_to_complete_stalled_project: DF.Int
        partner: DF.Link | None
        pending_bills_amount: DF.Currency
        percent_disbursed_amount: DF.Currency
        project_balance: DF.Currency
        project_name: DF.Data
        project_number: DF.Data
        project_objective: DF.SmallText | None
        project_output: DF.SmallText | None
        project_risks: DF.SmallText | None
        project_scope: DF.SmallText | None
        recommendation_for_the_stalled_project: DF.Literal["", "Complete", "Cancel", "Defer"]
        sector: DF.Link
        source_of_funds: DF.Table[ProjectXFundingSource]
        stalling_reasons: DF.SmallText | None
        status: DF.Link
        sub_sector: DF.Link | None
        technical_financial_economic_viability_current_measurement: DF.SmallText | None
        technical_financial_economic_viability_mitigation: DF.SmallText | None
        technical_rating: DF.Data | None
        total_certified_amount: DF.Currency
        total_disbursed_amount: DF.Currency
        total_expenditure_amount: DF.Currency
        total_funding_percentage: DF.Percent
        value_of_work_done: DF.Currency
        year_project_stalled: DF.Link | None
    # end: auto-generated types

    def validate(self):
        self.admin_names = ",".join([x.admin for x in self.administrative_areas or []])
        self.validate_funding_sources()
        self.validate_start_dates()
        self.validate_location()

    def on_update(self):
        self.add_updater_timeline_comment()

    def validate_funding_sources(self):
        total = 0
        for src in self.source_of_funds:
            total += src.percentage_of_funding

        self.total_funding_percentage = total
        if total != 100:
            frappe.throw(_("Total for sources of funds must equal to 100%"))

        # check that no duplicates
        for src in self.source_of_funds:
            # check duplicate funding sources
            duplicates = list(
                filter(
                    None,
                    map(
                        lambda rc: (rc.funded_by) == (src.funded_by)
                        and str(rc.idx)
                        or None,
                        self.source_of_funds,
                    ),
                )
            )
            if len(duplicates) > 1:
                frappe.throw(
                    _("Funding source {0} appears multiple times in rows {1}").format(
                        (src.funded_by), ", ".join(duplicates)
                    )
                )

        # set County/Dev partner cost component
        county_total = (
            sum(
                [
                    x.percentage_of_funding
                    for x in self.source_of_funds
                    if not x.is_partner
                ]
            )
            * self.approved_budget
        )
        non_county_total = (
            sum([x.percentage_of_funding for x in self.source_of_funds if x.is_partner])
            * self.approved_budget
        )

        self.development_partner_cost_component = non_county_total
        self.county_government_cost_component = county_total

    def validate_start_dates(self):
        """
        Validate start dates are within the set financial year
        """
        if not self.expected_start_date:
            return

        fy = frappe.db.get_value(
            "Financial YearX",
            self.financial_year,
            ["start_date", "end_date"],
            as_dict=True,
        )
        if not (
            getdate(fy.start_date)
            <= getdate(self.expected_start_date)
            <= getdate(fy.end_date)
        ):
            frappe.throw(
                _(
                    "The expected start date is not within the financial year {0}"
                ).format(self.financial_year)
            )
        # if not (
        #     getdate(fy.start_date)
        #     <= getdate(self.actual_start_date)
        #     <= getdate(fy.end_date)
        # ):
        #     frappe.throw(
        #         _("The actual start date is not within the financial year {0}").format(
        #             self.financial_year
        #         )
        #     )

    def validate_location(self):
        if not self.project_location:
            return

        try:
            geojson = json.loads(self.project_location)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid GeoJSON"))

        features = geojson.get("features", [])

        if not features:
            return

        if len(features) > 1:
            frappe.throw(
                _(
                    "Only one geometry is allowed. Please keep either a single Point or a single Polygon."
                )
            )

        geometry = features[0].get("geometry", {})
        geometry_type = geometry.get("type")

        if geometry_type == "GeometryCollection":
            frappe.throw(_("GeometryCollection is not supported."))

        if geometry_type not in ("Point", "Polygon"):
            frappe.throw(
                _("Exactly one geometry is allowed (one Point or one Polygon).")
            )

    @frappe.whitelist(allow_guest=True)
    def get_vector(self, doctype, docname):
        geom = frappe.db.get_value(doctype, docname, "geom")
        return geom

    def add_updater_timeline_comment(self):
        """
        Reads updater_reference flag if present and posts
        a system comment to the ProjectX Form Timeline.
        """
        updater = self.flags.get("updater_reference")

        if updater:
            # Add a visual timeline entry in the document sidebar feed

            # # Generate a clickable HTML link to the source document (e.g., PPR-00012)
            # doc_link = get_link_to_form(updater.get("doctype"), updater.get("docname"))

            # # Format the text with the embedded link
            # comment_text = _("{0}: {1}").format(doc_link, updater.get("label"))

            # # Call add_comment using valid arguments
            # self.add_comment(comment_type="Info", text=comment_text)

            # create the Comment document directly for custom reporting
            frappe.get_doc(
                {
                    "doctype": "Comment",
                    "comment_type": "Info",
                    "reference_doctype": self.doctype,
                    "reference_name": self.name,
                    "link_doctype": updater.get("doctype"),
                    "link_name": updater.get("docname"),
                    "content": updater.get("label"),
                    "comment_by": frappe.session.user,
                }
            ).insert(ignore_permissions=True)


def update_earned_value_and_pending_bills(project, updater_doc):
    """
    Relies strictly on site inspector progress percentages, calculate the Earned Value of work performed against actual cash outlay.

    Value of Work Completed = Approved Budget * Current Physical Progress / 100

    Pending Liabilities / Outstanding Commitment = Value of Work Completed -  Total Expenditure Paid
    """
    project = frappe.get_doc("ProjectX", project)

    approved_budget = project.approved_budget or 0.0
    physical_progress = project.current_physical_progress or 0.0
    total_expenditure = project.total_expenditure_amount or 0.0

    # Calculate monetary value of physical work completed on site
    value_of_work_done = approved_budget * (physical_progress / 100.0)

    # Pending liability = work done minus cash paid
    pending_commitment = value_of_work_done - total_expenditure

    # If pending commitment is negative, project is prepaid/overpaid relative to work done
    project.flags.updater_reference = {
        "doctype": updater_doc.doctype,
        "docname": updater_doc.name,
        "label": _("Updated Pending Bill to {0} and {1} via {2} {3}").format(
            "Value of Work Done",
            "Pending Bill/Outstanding",
            updater_doc.doctype,
            updater_doc.name,
        ),
    }
    project.value_of_work_done = value_of_work_done
    project.pending_commitment_amount = max(pending_commitment, 0.0)
    # Save target doc to trigger its validation & timeline hooks
    project.save(ignore_permissions=True)

    # frappe.db.set_value(
    #     "ProjectX",
    #     project,
    #     {
    #         "value_of_work_done": value_of_work_done,
    #         "pending_commitment_amount": max(pending_commitment, 0.0),
    #     },
    # )
