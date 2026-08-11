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
            "label": _("Approved Budget"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "total_disbursed",
            "label": _("Total Disbursed"),
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
            "fieldname": "value_of_work_done",
            "label": _("Value of Work Done"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "pending_bills",
            "label": _("Pending Liabilities"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "budget_variance",
            "label": _("Budget Variance"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "financial_progress",
            "label": _("Financial Progress (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "physical_progress",
            "label": _("Physical Progress (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "progress_variance",
            "label": _("Progress Variance (%)"),
            "fieldtype": "Percent",
            "width": 140,
        },
        {
            "fieldname": "health_status",
            "label": _("Health Status"),
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

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

    if filters.get("health_status"):
        conditions.append("health_status = %(health_status)s")
        values["health_status"] = filters.get("health_status")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql_query = f"""
        SELECT
            name AS project,
            project_name,
            department,
            approved_budget,
            total_disbursed_amount AS total_disbursed,
            total_expenditure_amount AS total_expenditure,
            value_of_work_done,
            pending_bills_amount AS pending_bills,
            current_physical_progress AS physical_progress,
            financial_progress_percent AS financial_progress,
            health_status
        FROM
            `tabProjectX`
        {where_clause}
        ORDER BY
            creation DESC
    """

    raw_projects = frappe.db.sql(sql_query, values, as_dict=True, debug=True)
    data = []

    for p in raw_projects:
        approved_budget = flt(p.approved_budget)
        expenditure = flt(p.total_expenditure)
        physical = flt(p.physical_progress)
        financial = flt(p.financial_progress)

        # Budget Variance = Approved Budget - Actual Expenditure
        budget_variance = approved_budget - expenditure

        # Progress Variance = Physical Progress - Financial Progress
        progress_variance = physical - financial

        data.append(
            {
                "project": p.project,
                "project_name": p.project_name,
                "department": p.department,
                "approved_budget": approved_budget,
                "total_disbursed": flt(p.total_disbursed),
                "total_expenditure": expenditure,
                "value_of_work_done": flt(p.value_of_work_done),
                "pending_bills": flt(p.pending_bills),
                "budget_variance": budget_variance,
                "financial_progress": financial,
                "physical_progress": physical,
                "progress_variance": progress_variance,
                "health_status": p.health_status or "On Track",
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
    approved_budgets = [row["approved_budget"] for row in sorted_data]
    total_expenditures = [row["total_expenditure"] for row in sorted_data]
    work_done_values = [row["value_of_work_done"] for row in sorted_data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Approved Budget"), "values": approved_budgets},
                {"name": _("Total Expenditure"), "values": total_expenditures},
                {"name": _("Work Done Value"), "values": work_done_values},
            ],
        },
        "type": "bar",
        "colors": ["#1f77b4", "#e377c2", "#2ca02c"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_budget = sum(row["approved_budget"] for row in data)
    total_expenditure = sum(row["total_expenditure"] for row in data)
    total_pending = sum(row["pending_bills"] for row in data)

    overall_financial_progress = (
        (total_expenditure / total_budget * 100.0) if total_budget > 0 else 0.0
    )

    return [
        {
            "value": total_budget,
            "indicator": "Blue",
            "label": _("Total Budget"),
            "datatype": "Currency",
        },
        {
            "value": total_expenditure,
            "indicator": "Orange",
            "label": _("Total Expenditure"),
            "datatype": "Currency",
        },
        {
            "value": total_pending,
            "indicator": "Red",
            "label": _("Total Pending Liabilities"),
            "datatype": "Currency",
        },
        {
            "value": overall_financial_progress,
            "indicator": "Green" if overall_financial_progress <= 100 else "Red",
            "label": _("Overall Financial Absorption"),
            "datatype": "Percent",
        },
    ]
