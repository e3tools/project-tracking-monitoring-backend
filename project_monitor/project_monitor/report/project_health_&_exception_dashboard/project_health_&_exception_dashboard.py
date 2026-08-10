# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe

from frappe import _
from frappe.utils import flt, today, date_diff


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary


def get_columns():
    return [
        {
            "fieldname": "project",
            "label": _("Project Code"),
            "fieldtype": "Link",
            "options": "ProjectX",
            "width": 140,
        },
        {
            "fieldname": "project_name",
            "label": _("Project Name"),
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "health_status",
            "label": _("Health Status"),
            "fieldtype": "Data",
            "width": 130,
        },
        {
            "fieldname": "exception_flags",
            "label": _("Triggered Exception Flag(s)"),
            "fieldtype": "Data",
            "width": 280,
        },
        {
            "fieldname": "approved_budget",
            "label": _("Approved Budget"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "total_expenditure",
            "label": _("Total Expenditure"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "pending_bills",
            "label": _("Pending Liabilities"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "physical_progress",
            "label": _("Physical Progress (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "financial_progress",
            "label": _("Financial Progress (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "days_since_last_update",
            "label": _("Days Since Last Update"),
            "fieldtype": "Int",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("department"):
        conditions.append("department = %(department)s")
        values["department"] = filters.get("department")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql_query = f"""
        SELECT
            name AS project,
            project_name,
            department,
            approved_budget,
            total_expenditure_amount AS total_expenditure,
            pending_bills_amount AS pending_bills,
            current_physical_progress AS physical_progress,
            financial_progress_percent AS financial_progress,
            health_status,
            last_progress_update_date
        FROM
            `tabProjectX`
        {where_clause}
        ORDER BY
            creation DESC
    """

    raw_projects = frappe.db.sql(sql_query, values, as_dict=True)
    data = []
    current_date = today()

    for p in raw_projects:
        budget = flt(p.approved_budget)
        expenditure = flt(p.total_expenditure)
        pending = flt(p.pending_bills)
        physical = flt(p.physical_progress)
        financial = flt(p.financial_progress)

        last_date = p.last_progress_update_date
        days_stale = date_diff(current_date, last_date) if last_date else 999

        exceptions = []

        # Exception 1: Over Budget
        if expenditure > budget and budget > 0:
            exceptions.append("Over Budget")

        # Exception 2: Progress Lag (> 15% financial vs physical gap)
        if (financial - physical) > 15.0:
            exceptions.append("Physical Progress Lag")

        # Exception 3: Stale Progress Update (> 60 days without inspection)
        if days_stale > 60:
            exceptions.append("Stale Report (>60 Days)")

        # Exception 4: High Pending Liabilities
        if pending > budget * 0.5 and budget > 0:
            exceptions.append("Critical Pending Liabilities")

        exception_str = (
            ", ".join(exceptions) if exceptions else "None (Normal Operations)"
        )

        # Filter by health category if requested
        if filters.get("health_status") and p.health_status != filters.get(
            "health_status"
        ):
            continue

        # Filter by specific exception type if requested
        if (
            filters.get("exception_type") == "Over Budget"
            and "Over Budget" not in exceptions
        ):
            continue
        elif (
            filters.get("exception_type") == "Progress Lag (>15% gap)"
            and "Physical Progress Lag" not in exceptions
        ):
            continue
        elif (
            filters.get("exception_type") == "Stale Progress (>60 days)"
            and "Stale Report (>60 Days)" not in exceptions
        ):
            continue
        elif (
            filters.get("exception_type") == "High Pending Liabilities (> budget)"
            and "Critical Pending Liabilities" not in exceptions
        ):
            continue
        elif filters.get("exception_type") == "All Exceptions" and not exceptions:
            continue

        data.append(
            {
                "project": p.project,
                "project_name": p.project_name,
                "department": p.department,
                "health_status": p.health_status
                or ("Critical / Action Required" if exceptions else "On Track"),
                "exception_flags": exception_str,
                "approved_budget": budget,
                "total_expenditure": expenditure,
                "pending_bills": pending,
                "physical_progress": physical,
                "financial_progress": financial,
                "days_since_last_update": (
                    days_stale if days_stale != 999 else "No Inspection Logged"
                ),
            }
        )

    return data


def get_chart_data(data):
    if not data:
        return None

    # Count occurrences of health statuses
    health_counts = {
        "On Track": 0,
        "Delayed": 0,
        "Budget Exceeded": 0,
        "Critical / Action Required": 0,
    }

    for row in data:
        status = row["health_status"]
        if status in health_counts:
            health_counts[status] += 1
        else:
            health_counts["Critical / Action Required"] += 1

    return {
        "data": {
            "labels": list(health_counts.keys()),
            "datasets": [
                {"name": _("Project Count"), "values": list(health_counts.values())}
            ],
        },
        "type": "percentage",
        "colors": ["#2ca02c", "#ff7f0e", "#d62728", "#9467bd"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_projects = len(data)
    flagged_projects = sum(
        1 for row in data if row["exception_flags"] != "None (Normal Operations)"
    )
    on_track_projects = total_projects - flagged_projects

    return [
        {
            "value": total_projects,
            "indicator": "Blue",
            "label": _("Total Portfolio Projects"),
            "datatype": "Int",
        },
        {
            "value": on_track_projects,
            "indicator": "Green",
            "label": _("Normal / On Track"),
            "datatype": "Int",
        },
        {
            "value": flagged_projects,
            "indicator": "Red" if flagged_projects > 0 else "Green",
            "label": _("Flagged Exceptions"),
            "datatype": "Int",
        },
    ]
