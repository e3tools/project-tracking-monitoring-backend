# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate


class ProjectX(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_monitor.project_monitor.doctype.projectx_funding_source.projectx_funding_source import (
            ProjectXFundingSource,
        )
        from project_monitor.project_monitor.doctype.projectx_location_item.projectx_location_item import (
            ProjectXLocationItem,
        )

        admin_names: DF.SmallText | None
        administrative_areas: DF.Table[ProjectXLocationItem]
        administrative_level: DF.Literal["", "Admin 0", "Admin 1", "Admin 2", "Admin 3"]
        approval_number: DF.Data | None
        completion_level: DF.Percent
        department: DF.Link | None
        estimated_cost: DF.Currency
        expected_end_date: DF.Date | None
        expected_start_date: DF.Date | None
        financial_year: DF.Link
        implemented_by: DF.Literal[
            "", "County Government", "Partner", "Local Organization"
        ]
        partner: DF.Link | None
        project_image: DF.AttachImage | None
        project_name: DF.Data
        project_number: DF.Data
        project_scope: DF.Text | None
        source_of_funds: DF.Table[ProjectXFundingSource]
        status: DF.Link
        technical_rating: DF.Data | None
        total_percentage: DF.Percent
    # end: auto-generated types

    def validate(self):
        self.admin_names = ",".join([x.admin for x in self.administrative_areas or []])
        self.validate_funding_sources()
        self.validate_start_dates()

    def validate_funding_sources(self):
        total = 0
        for src in self.source_of_funds:
            total += src.percentage_of_funding
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

    @frappe.whitelist(allow_guest=True)
    def get_vector(self, doctype, docname):
        geom = frappe.db.get_value(doctype, docname, "geom")
        return geom
