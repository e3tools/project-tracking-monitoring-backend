import frappe
from frappe import _
from project_monitor.www.web_page_enum import WebPageEnum
from frappe.query_builder.functions import Count, Max, Sum, IfNull, Substring
from project_monitor.templates.project_base import get_context as get_base_context


def get_context(context):
    context["categories"] = get_faq_categories()
    context["faqs"] = get_faqs()
    context["labels"] = get_labels()
    return context


def get_faqs():
    FAQ = frappe.qb.DocType("FAQX")
    query = (
        frappe.qb.from_(FAQ)
        .select(FAQ.name, FAQ.category, FAQ.question, FAQ.response)
        .where(FAQ.show_in_website == 1)
    )
    return query.run(as_dict=True)


def get_faq_categories():
    Category = frappe.qb.DocType("FAQX Category")
    query = frappe.qb.from_(Category).select(Category.name, Category.category)
    return query.run(as_dict=True)


def get_labels():
    labels = {
        "PageTitle": "Frequently Asked Questions",
        "EmptyProject": 'Project does not exist. Click <a href="page_search_result">here</a> to search',
        "Reply": "Reply",
        "SubmitFeedback": "Submit New Feedback",
        "ViewFeedback": "View Feedback",
        "Department": "Department",
        "ImplementedBy": "Implemented By",
        "EstimatedCost": "Estimated Cost",
        "ApprovalNumber": "Approval Number",
        "MoreInfo": "Want to know more about the County and other budgeting processes",
        "RecentWorksTitle": "Recent Works",
        "RecentWorksText": "Click on the galleries to view project photos",
    }
    return labels
