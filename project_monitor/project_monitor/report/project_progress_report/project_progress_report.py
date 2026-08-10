# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


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
            "fieldname": "progress_report_id",
            "label": _("Report Ref"),
            "fieldtype": "Link",
            "options": "ProjectX Progress Report",
            "width": 140,
        },
        {
            "fieldname": "inspection_date",
            "label": _("Inspection Date"),
            "fieldtype": "Date",
            "width": 120,
        },
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
            "fieldname": "physical_progress_percent",
            "label": _("Physical Progress (%)"),
            "fieldtype": "Percent",
            "width": 150,
        },
        {
            "fieldname": "progress_delta",
            "label": _("Progress Increase (%)"),
            "fieldtype": "Percent",
            "width": 150,
        },
        {
            "fieldname": "inspector_name",
            "label": _("Inspected By / Inspector"),
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "fieldname": "remarks",
            "label": _("Inspection Remarks"),
            "fieldtype": "Data",
            "width": 250,
        },
    ]


def get_data(filters):
    conditions = ["pr.docstatus = 1"]
    values = {}

    if filters.get("project"):
        conditions.append("pr.project = %(project)s")
        values["project"] = filters.get("project")

    if filters.get("from_date"):
        conditions.append("pr.inspection_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("pr.inspection_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    if filters.get("department"):
        conditions.append("p.department = %(department)s")
        values["department"] = filters.get("department")

    where_clause = f"WHERE {' AND '.join(conditions)}"

    sql_query = f"""
        SELECT
            pr.name AS progress_report_id,
            pr.inspection_date,
            pr.project,
            p.project_name,
            p.department,
            pr.physical_progress_percent,
            pr.inspector_name,
            pr.remarks
        FROM
            `tabProjectX Progress Report` pr
        LEFT JOIN
            `tabProjectX` p ON pr.project = p.name
        {where_clause}
        ORDER BY
            pr.project ASC, pr.inspection_date ASC, pr.creation ASC
    """

    raw_reports = frappe.db.sql(sql_query, values, as_dict=True)
    data = []
    project_last_progress = {}

    for row in raw_reports:
        project_code = row.project
        current_progress = flt(row.physical_progress_percent)

        # Calculate progress gained since the previous inspection report
        previous_progress = project_last_progress.get(project_code, 0.0)
        progress_delta = max(current_progress - previous_progress, 0.0)

        # Update tracker for sequential calculations
        project_last_progress[project_code] = current_progress

        data.append(
            {
                "progress_report_id": row.progress_report_id,
                "inspection_date": row.inspection_date,
                "project": row.project,
                "project_name": row.project_name,
                "department": row.department,
                "physical_progress_percent": current_progress,
                "progress_delta": progress_delta,
                "inspector_name": row.inspector_name or "N/A",
                "remarks": row.remarks or "",
            }
        )

    return data


def get_chart_data(data):
    if not data:
        return None

    # Group progress over inspection dates
    dates = []
    progress_values = []

    # Sort chronologically for chart display
    sorted_by_date = sorted(data, key=lambda x: str(x["inspection_date"]))[:15]

    for row in sorted_by_date:
        dates.append(str(row["inspection_date"]))
        progress_values.append(row["physical_progress_percent"])

    return {
        "data": {
            "labels": dates,
            "datasets": [
                {"name": _("Physical Progress (%)"), "values": progress_values}
            ],
        },
        "type": "line",
        "colors": ["#2ca02c"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_inspections = len(data)
    avg_progress = (
        (sum(row["physical_progress_percent"] for row in data) / total_inspections)
        if total_inspections > 0
        else 0.0
    )
    total_delta = sum(row["progress_delta"] for row in data)

    return [
        {
            "value": total_inspections,
            "indicator": "Blue",
            "label": _("Total Inspections Logged"),
            "datatype": "Int",
        },
        {
            "value": round(avg_progress, 2),
            "indicator": "Green",
            "label": _("Average Logged Progress"),
            "datatype": "Percent",
        },
        {
            "value": round(total_delta, 2),
            "indicator": "Purple",
            "label": _("Cumulative Progress Delta"),
            "datatype": "Percent",
        },
    ]
