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
            "width": 150,
        },
        {
            "fieldname": "gross_certified",
            "label": _("Gross Certified Work"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "total_retention",
            "label": _("Retention Withheld"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "net_certified",
            "label": _("Net Payable Certified"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "total_paid",
            "label": _("Actual Paid Expenditure"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "pending_bills",
            "label": _("Pending Liabilities"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "ipc_count",
            "label": _("IPCs Issued"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "liability_status",
            "label": _("Liability Status"),
            "fieldtype": "Data",
            "width": 130,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("project"):
        conditions.append("p.name = %(project)s")
        values["project"] = filters.get("project")

    if filters.get("department"):
        conditions.append("p.department = %(department)s")
        values["department"] = filters.get("department")

    if filters.get("sub_county"):
        conditions.append("p.sub_county LIKE %(sub_county)s")
        values["sub_county"] = f"%{filters.get('sub_county')}%"

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql_query = f"""
        SELECT
            p.name AS project,
            p.project_name,
            p.department,
            p.approved_budget,
            p.total_certified_amount AS net_certified,
            p.total_expenditure_amount AS total_paid,
            p.pending_bills_amount AS pending_bills,
            (
                SELECT COALESCE(SUM(gross_certified_amount), 0.0)
                FROM `tabProject Payment Certificate`
                WHERE project = p.name AND docstatus = 1
            ) AS gross_certified,
            (
                SELECT COALESCE(SUM(retention_amount), 0.0)
                FROM `tabProject Payment Certificate`
                WHERE project = p.name AND docstatus = 1
            ) AS total_retention,
            (
                SELECT COUNT(name)
                FROM `tabProject Payment Certificate`
                WHERE project = p.name AND docstatus = 1
            ) AS ipc_count
        FROM
            `tabProjectX` p
        {where_clause}
        ORDER BY
            p.pending_bills_amount DESC, p.creation DESC
    """

    raw_data = frappe.db.sql(sql_query, values, as_dict=True)
    data = []

    for row in raw_data:
        pending = flt(row.pending_bills)

        if filters.get("has_pending_liability") and pending <= 0:
            continue

        if pending <= 0:
            status = "Fully Settled"
        elif pending > 10000000:
            status = "Critical Liability"
        else:
            status = "Pending Payment"

        data.append(
            {
                "project": row.project,
                "project_name": row.project_name,
                "department": row.department,
                "approved_budget": flt(row.approved_budget),
                "gross_certified": flt(row.gross_certified),
                "total_retention": flt(row.total_retention),
                "net_certified": flt(row.net_certified),
                "total_paid": flt(row.total_paid),
                "pending_bills": pending,
                "ipc_count": row.ipc_count or 0,
                "liability_status": status,
            }
        )

    return data


def get_chart_data(data):
    if not data:
        return None

    # Top 10 projects with highest pending liabilities
    sorted_data = sorted(data, key=lambda x: x["pending_bills"], reverse=True)[:10]

    labels = [
        (
            row["project_name"][:15] + "..."
            if len(row["project_name"]) > 15
            else row["project_name"]
        )
        for row in sorted_data
    ]
    net_certified = [row["net_certified"] for row in sorted_data]
    total_paid = [row["total_paid"] for row in sorted_data]
    pending_bills = [row["pending_bills"] for row in sorted_data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Net Certified"), "values": net_certified},
                {"name": _("Paid Expenditure"), "values": total_paid},
                {"name": _("Pending Liabilities"), "values": pending_bills},
            ],
        },
        "type": "bar",
        "colors": ["#1f77b4", "#2ca02c", "#d62728"],
    }


def get_report_summary(data):
    if not data:
        return []

    total_gross = sum(row["gross_certified"] for row in data)
    total_retention = sum(row["total_retention"] for row in data)
    total_net_certified = sum(row["net_certified"] for row in data)
    total_paid = sum(row["total_paid"] for row in data)
    total_pending = sum(row["pending_bills"] for row in data)

    return [
        {
            "value": total_gross,
            "indicator": "Blue",
            "label": _("Total Gross Certified Work"),
            "datatype": "Currency",
        },
        {
            "value": total_retention,
            "indicator": "Grey",
            "label": _("Total Retention Withheld"),
            "datatype": "Currency",
        },
        {
            "value": total_net_certified,
            "indicator": "Purple",
            "label": _("Total Net Certified (IPCs)"),
            "datatype": "Currency",
        },
        {
            "value": total_paid,
            "indicator": "Green",
            "label": _("Total Paid Expenditure"),
            "datatype": "Currency",
        },
        {
            "value": total_pending,
            "indicator": "Red",
            "label": _("Outstanding Pending Liabilities"),
            "datatype": "Currency",
        },
    ]
