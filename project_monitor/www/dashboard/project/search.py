import frappe
from frappe import _
from project_monitor.www.web_page_enum import WebPageEnum
from frappe.query_builder.functions import Count, Max, Sum, IfNull, Substring
from project_monitor.templates.project_base import get_context as get_base_context


def get_context(context):
    context = get_base_context(context)
    search = frappe.form_dict.search
    ProjectX = frappe.qb.DocType("ProjectX")
    query = (
        frappe.qb.from_(ProjectX)
        .select(
            ProjectX.name,
            ProjectX.project_name,
            Substring(ProjectX.project_scope, 1, 300).as_("project_scope"),
            ProjectX.administrative_level,
            ProjectX.admin_names,
            ProjectX.financial_year,
            ProjectX.expected_start_date,
        )
        .where(
            ProjectX.project_name.like(f"%{search}%")
            if search
            else ProjectX.docstatus < 2
        )
    )
    projects = query.run(as_dict=True)
    context["search_term"] = search
    context["projects"] = projects
    context["labels"] = get_labels()
    return context


def get_labels():
    labels = {
        "FeedbackTitle": "Feedback",
        "PageTitle": "Project Details",
        "AddFeedback": "Add Feedback",
        "Reply": "Reply",
        "ViewFeedback": "Feedback",
    }
    return labels
