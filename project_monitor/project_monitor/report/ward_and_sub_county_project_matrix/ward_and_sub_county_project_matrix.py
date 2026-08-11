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
    settings = frappe.get_doc("Project Monitor Settings", "Project Monitor Settings")
    return [
        {
            "fieldname": "admin_2",
            "label": _(settings.admin_2_display_name or "Sub-County"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "admin_3",
            "label": _(settings.admin_3_display_name or "Ward"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "project",
            "label": _("Project Code"),
            "fieldtype": "Link",
            "options": "ProjectX",
            "width": 130,
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
            "fieldname": "total_expenditure",
            "label": _("Total Expenditure"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "pending_bills",
            "label": _("Pending Liabilities"),
            "fieldtype": "Currency",
            "width": 140,
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
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    # if filters.get("sub_county"):
    #     conditions.append("sub_county LIKE %(sub_county)s")
    #     values["sub_county"] = f"%{filters.get('sub_county')}%"

    # if filters.get("ward"):
    #     conditions.append("ward LIKE %(ward)s")
    #     values["ward"] = f"%{filters.get('ward')}%"

    if filters.get("admin_2"):
        conditions.append("FIND_IN_SET(%(admin_2)s, admin_2_names) > 0")
        values["admin_2"] = f"{filters.get('admin_2')}"

    if filters.get("admin_3"):
        # conditions.append("p.sub_county LIKE %(sub_county)s")
        # values["sub_county"] = f"%{filters.get('sub_county')}%"
        conditions.append("FIND_IN_SET(%(admin_3)s, admin_3_names) > 0")
        values["admin_3"] = f"{filters.get('admin_3')}"

    if filters.get("department"):
        conditions.append("department = %(department)s")
        values["department"] = filters.get("department")

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters.get("status")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql_query = f"""
        SELECT
            COALESCE(admin_2_names, 'Unassigned') AS admin_2,
            COALESCE(admin_3_names, 'Unassigned') AS admin_3,
            name AS project,
            project_name,
            department,
            approved_budget,
            total_expenditure_amount AS total_expenditure,
            pending_bills_amount AS pending_bills,
            current_physical_progress AS physical_progress,
            financial_progress_percent AS financial_progress,
            status
        FROM
            `tabProjectX`
        {where_clause}
        ORDER BY
            admin_2_names ASC, admin_3_names ASC, name ASC
    """

    raw_projects = frappe.db.sql(sql_query, values, as_dict=True)
    data = []

    for p in raw_projects:
        data.append(
            {
                "admin_2": p.admin_2,
                "admin_3": p.admin_3,
                "project": p.project,
                "project_name": p.project_name,
                "department": p.department,
                "approved_budget": flt(p.approved_budget),
                "total_expenditure": flt(p.total_expenditure),
                "pending_bills": flt(p.pending_bills),
                "physical_progress": flt(p.physical_progress),
                "financial_progress": flt(p.financial_progress),
                "status": p.status or "In Progress",
            }
        )

    return data


def get_chart_data(data):
    if not data:
        return None

    # Aggregate budget by Sub-County
    sub_county_budgets = {}
    for row in data:
        sc = row["admin_2"]
        sub_county_budgets[sc] = (
            sub_county_budgets.get(sc, 0.0) + row["approved_budget"]
        )

    labels = list(sub_county_budgets.keys())
    budget_values = list(sub_county_budgets.values())

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Allocated Budget"), "values": budget_values}],
        },
        "type": "bar",
        "colors": ["#1f77b4"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_budget = sum(row["approved_budget"] for row in data)
    total_expenditure = sum(row["total_expenditure"] for row in data)
    unique_sub_counties = len(set(row["admin_2"] for row in data))
    unique_wards = len(set(row["admin_3"] for row in data))

    return [
        {
            "value": total_budget,
            "indicator": "Blue",
            "label": _("Total Regional Budget"),
            "datatype": "Currency",
        },
        {
            "value": total_expenditure,
            "indicator": "Orange",
            "label": _("Total Regional Expenditure"),
            "datatype": "Currency",
        },
        {
            "value": unique_sub_counties,
            "indicator": "Purple",
            "label": _("Sub-Counties Covered"),
            "datatype": "Int",
        },
        {
            "value": unique_wards,
            "indicator": "Green",
            "label": _("Wards Covered"),
            "datatype": "Int",
        },
    ]
