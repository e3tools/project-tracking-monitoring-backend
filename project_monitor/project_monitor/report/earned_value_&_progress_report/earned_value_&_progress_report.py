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
            "fieldname": "approved_budget",
            "label": _("Budget at Completion (BAC)"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "physical_progress",
            "label": _("Physical Progress (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "earned_value",
            "label": _("Earned Value (EV)"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "actual_cost",
            "label": _("Actual Cost (AC)"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "total_certified",
            "label": _("Total Certified (IPC)"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "cost_variance",
            "label": _("Cost Variance (EV - AC)"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "cpi",
            "label": _("Cost Performance Index (CPI)"),
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "fieldname": "cost_status",
            "label": _("Cost Health"),
            "fieldtype": "Data",
            "width": 130,
        },
        {
            "fieldname": "last_progress_date",
            "label": _("Last Inspection Date"),
            "fieldtype": "Date",
            "width": 130,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("project"):
        conditions.append("name = %(project)s")
        values["project"] = filters.get("project")

    if filters.get("department"):
        conditions.append("department = %(department)s")
        values["department"] = filters.get("department")

    # if filters.get("sub_county"):
    #     conditions.append("sub_county LIKE %(sub_county)s")
    #     values["sub_county"] = f"%{filters.get('sub_county')}%"
    if filters.get("admin_2"):
        conditions.append("FIND_IN_SET(%(admin_2)s, admin_2_names) > 0")
        values["admin_2"] = f"{filters.get('admin_2')}"

    if filters.get("admin_3"):
        # conditions.append("p.sub_county LIKE %(sub_county)s")
        # values["sub_county"] = f"%{filters.get('sub_county')}%"
        conditions.append("FIND_IN_SET(%(admin_3)s, admin_3_names) > 0")
        values["admin_3"] = f"{filters.get('admin_3')}"

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters.get("status")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql_query = f"""
        SELECT
            name AS project,
            project_name,
            department,
            approved_budget,
            current_physical_progress AS physical_progress,
            value_of_work_done AS earned_value,
            total_expenditure_amount AS actual_cost,
            total_certified_amount AS total_certified,
            last_progress_update_date AS last_progress_date
        FROM
            `tabProjectX`
        {where_clause}
        ORDER BY
            creation DESC
    """

    raw_projects = frappe.db.sql(sql_query, values, as_dict=True)
    data = []

    for p in raw_projects:
        approved_budget = flt(p.approved_budget)
        physical_progress = flt(p.physical_progress)
        actual_cost = flt(p.actual_cost)

        # Earned Value (EV) calculation
        earned_value = (
            flt(p.earned_value)
            if flt(p.earned_value) > 0
            else (approved_budget * (physical_progress / 100.0))
        )

        # Cost Variance = EV - AC
        cost_variance = earned_value - actual_cost

        # CPI = EV / AC
        cpi = (
            (earned_value / actual_cost)
            if actual_cost > 0
            else (1.0 if earned_value == 0 else 2.0)
        )

        # Determine Cost Health Status
        if actual_cost == 0 and earned_value == 0:
            cost_status = "Not Started"
        elif cpi >= 1.0:
            cost_status = "Under Budget"
        elif cpi >= 0.9:
            cost_status = "Slightly Over Budget"
        else:
            cost_status = "Over Budget"

        data.append(
            {
                "project": p.project,
                "project_name": p.project_name,
                "department": p.department,
                "approved_budget": approved_budget,
                "physical_progress": physical_progress,
                "earned_value": earned_value,
                "actual_cost": actual_cost,
                "total_certified": flt(p.total_certified),
                "cost_variance": cost_variance,
                "cpi": round(cpi, 2),
                "cost_status": cost_status,
                "last_progress_date": p.last_progress_date,
            }
        )

    return data


def get_chart_data(data):
    if not data:
        return None

    # Top 10 projects by approved budget
    sorted_data = sorted(data, key=lambda x: x["approved_budget"], reverse=True)[:10]

    labels = [
        (
            row["project_name"][:15] + "..."
            if len(row["project_name"]) > 15
            else row["project_name"]
        )
        for row in sorted_data
    ]
    earned_values = [row["earned_value"] for row in sorted_data]
    actual_costs = [row["actual_cost"] for row in sorted_data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Earned Value (EV)"), "values": earned_values},
                {"name": _("Actual Cost (AC)"), "values": actual_costs},
            ],
        },
        "type": "bar",
        "colors": ["#2ca02c", "#d62728"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_bac = sum(row["approved_budget"] for row in data)
    total_ev = sum(row["earned_value"] for row in data)
    total_ac = sum(row["actual_cost"] for row in data)
    overall_cost_variance = total_ev - total_ac
    overall_cpi = (total_ev / total_ac) if total_ac > 0 else 1.0

    return [
        {
            "value": total_bac,
            "indicator": "Blue",
            "label": _("Total Budget (BAC)"),
            "datatype": "Currency",
        },
        {
            "value": total_ev,
            "indicator": "Green",
            "label": _("Total Earned Value (EV)"),
            "datatype": "Currency",
        },
        {
            "value": total_ac,
            "indicator": "Orange",
            "label": _("Total Actual Cost (AC)"),
            "datatype": "Currency",
        },
        {
            "value": overall_cost_variance,
            "indicator": "Green" if overall_cost_variance >= 0 else "Red",
            "label": _("Portfolio Cost Variance"),
            "datatype": "Currency",
        },
        {
            "value": round(overall_cpi, 2),
            "indicator": "Green" if overall_cpi >= 1.0 else "Red",
            "label": _("Portfolio CPI"),
            "datatype": "Float",
        },
    ]
