import frappe
from frappe import _
from project_monitor.www.web_page_enum import WebPageEnum
from frappe.query_builder.functions import (
    Count,
    DistinctOptionFunction,
    Max,
    Sum,
    IfNull,
    Substring,
)
from frappe.query_builder.functions import GroupConcat


def get_context(context):
    # get financial years
    context["financial_years"] = get_financial_years()

    # Get UI labels
    context["labels"] = get_labels()
    return context


def get_labels():
    labels = {
        "PageTitle": "Projects Summary",
        "BodyTitle": "Projects Summary",
        "EmptyProject": 'Project does not exist. Click <a href="page_search_result">here</a> to search',
        "Reply": "Reply",
        "SubmitFeedback": "Submit New Feedback",
        "CopyRight": "2025 © County Government of Taita Taveta. ALL Rights Reserved",
        "FBLink": "",
        "XLink": "",
        "YoutubeLink": "",
    }
    return labels


def get_financial_years():
    FinancialYearX = frappe.qb.DocType("Financial YearX")
    query = frappe.qb.from_(FinancialYearX).select(FinancialYearX.name)
    return query.run(as_dict=True)
