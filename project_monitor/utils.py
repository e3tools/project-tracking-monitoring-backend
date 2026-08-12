# Copyright (c) 2026, Project Monitor and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def recalculate_project_metrics(project, source_doc=None, update_message=None):
    """
    Centralized calculation logic for ProjectX metrics.
    Evaluates Project Monitor Settings to select the calculation method.
    """
    if not project:
        return

    # Fetch active calculation method from single DocType
    calc_method = (
        frappe.db.get_single_value(
            "Project Monitor Settings", "pending_bill_calculation_method"
        )
        or "Payment Certificate (IPC) Ledger"
    )

    # Fetch total expenditures (docstatus = 1)
    total_expenditure = (
        frappe.db.sql(
            """
        SELECT COALESCE(SUM(amount), 0.0)
        FROM `tabProjectX Expenditure`
        WHERE project = %s AND docstatus = 1
    """,
            (project,),
        )[0][0]
        or 0.0
    )

    # Fetch total disbursements (docstatus = 1)
    total_disbursed = (
        frappe.db.sql(
            """
        SELECT COALESCE(SUM(amount), 0.0)
        FROM `tabProjectX Disbursement`
        WHERE project = %s AND docstatus = 1
    """,
            (project,),
        )[0][0]
        or 0.0
    )

    # Fetch latest physical progress from submitted progress reports
    latest_progress_report = frappe.db.get_all(
        "ProjectX Progress Report",
        filters={"project": project, "docstatus": 1},
        fields=["physical_progress_percent", "inspection_date"],
        order_by="inspection_date desc, creation desc",
        limit=1,
    )

    current_progress = (
        latest_progress_report[0].physical_progress_percent
        if latest_progress_report
        else 0.0
    )
    last_update_date = (
        latest_progress_report[0].inspection_date if latest_progress_report else None
    )

    # Fetch total net certified work amount from submitted payment certificates
    total_certified = (
        frappe.db.sql(
            """
        SELECT COALESCE(SUM(net_payable_amount), 0.0)
        FROM `tabProjectX Payment Certificate`
        WHERE project = %s AND docstatus = 1
    """,
            (project,),
        )[0][0]
        or 0.0
    )

    # Load parent project
    project_doc = frappe.get_doc("ProjectX", project)
    approved_budget = flt(project_doc.approved_budget)

    # Evaluate calculation methodology
    if calc_method == "Earned Value Progress Estimate":
        # Value of Work Done = Approved Budget * (Physical Progress %)
        value_of_work_done = approved_budget * (flt(current_progress) / 100.0)
        pending_bills = max(value_of_work_done - total_expenditure, 0.0)
    else:
        # Default: Payment Certificate (IPC) Ledger
        # Value of Work Done = Sum of certified IPCs
        value_of_work_done = total_certified
        pending_bills = max(total_certified - total_expenditure, 0.0)

    # Financial progress percentage
    financial_progress = (
        (total_expenditure / approved_budget * 100.0) if approved_budget > 0 else 0.0
    )

    # Attach in-memory updater reference flag if source document provided
    if source_doc and update_message:
        project_doc.flags.updater_reference = {
            "doctype": source_doc.doctype,
            "docname": source_doc.name,
            "label": update_message,
        }

    # Update metric values
    project_doc.total_expenditure_amount = total_expenditure
    project_doc.total_disbursed_amount = total_disbursed
    project_doc.total_certified_amount = total_certified
    project_doc.current_physical_progress = current_progress
    project_doc.last_progress_update_date = last_update_date
    project_doc.value_of_work_done = value_of_work_done
    project_doc.pending_bills_amount = pending_bills
    project_doc.current_financial_progress = min(financial_progress, 100.0)

    project_doc.flags.ignore_permissions = True
    project_doc.save()

    # Trigger UI update
    frappe.publish_realtime(
        "doc_update", {"doctype": "ProjectX", "name": project}, after_commit=True
    )
