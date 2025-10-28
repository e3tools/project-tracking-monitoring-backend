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
from project_monitor.templates.project_base import get_context as get_base_context


def get_context(context):
    context = get_base_context(context)
    fy = frappe.form_dict.fy
    # if not project_id:
    #     # redirect to search page
    #     context["labels"] = get_labels()
    #     return context
    # if "is_new" in frappe.form_dict:
    #     submit_feedback()
    #     return context

    context["fy"] = fy or "All"
    # get financial years
    context["financial_years"] = get_financial_years()

    # get pivot table of total cost by department and project status
    pivot_headers, pivot_data = get_project_costs_by_department_and_status(fy)
    context["project_by_dept_cost_headers"] = pivot_headers
    context["project_by_dept_cost"] = pivot_data

    # get pivot table of total number of projects by department and project status
    pivot_headers, pivot_data = get_project_counts_by_department_and_status(fy)
    context["project_by_dept_count_headers"] = pivot_headers
    context["project_by_dept_count"] = pivot_data

    # get pivot table of total number of projects by sub-counties and project status
    pivot_headers, pivot_data = get_project_counts_by_subcounties_and_status(fy)
    context["project_by_subcounty_count_headers"] = pivot_headers
    context["project_by_subcounty_count"] = pivot_data

    # get pivot table of total number and cost of projects by sub-counties
    pivot_headers, pivot_data = get_project_cost_by_subcounties(fy)
    context["project_by_subcounty_cost_headers"] = pivot_headers
    context["project_by_subcounty_cost"] = pivot_data

    # get pivot table of total number of projects by wards and project status
    pivot_headers, pivot_data = get_project_counts_by_wards_and_status(fy)
    context["project_by_ward_count_headers"] = pivot_headers
    context["project_by_ward_count"] = pivot_data

    # Get total cost by status
    context["project_by_status_cost"] = get_projects_by_status(fy)

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
        "ProjectCountTitle": "Number of Projects",
        "ProjectCostTitle": "Estimated Cost",
        "ProjectCountSummary": "Number of projects grouped by status",
        "ProjectCostSummary": "Estimated cost of projects grouped by status",
    }
    return labels


def get_financial_years():
    FinancialYearX = frappe.qb.DocType("Financial YearX")
    query = frappe.qb.from_(FinancialYearX).select(FinancialYearX.name)
    return query.run(as_dict=True)


@frappe.whitelist(allow_guest=True)
def get_projects_by_status(fy=None):
    return filter_projects(fy=fy)
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        .on(
            ProjectXStatus.name
            == ProjectX.status
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            ProjectXStatus.theme,
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(ProjectXStatus.name)
    )
    res = query.run(as_dict=True)
    return res


def filter_projects(fy=None):
    # project status
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        .on(
            ProjectXStatus.name
            == ProjectX.status
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            ProjectXStatus.theme,
            ProjectXStatus.description,
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(ProjectXStatus.name)
    )
    status_costs = query.run(as_dict=True)

    # all projects
    query = (
        frappe.qb.from_(ProjectX)
        .select(
            Count(ProjectX.name).as_("count"),
            # ("All Projects").as_("project_status"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .where(
            ProjectX.financial_year == fy
            if fy
            else ProjectX.financial_year == ProjectX.financial_year
        )
        .groupby()
    )
    all_project_cost = query.run(as_dict=True)
    all_project_cost[0].update(
        {
            "project_status": "All Projects",
            "theme": "Primary",
            "description": "All projects",
        }
    )
    status_costs.insert(0, all_project_cost[0])
    return status_costs


def get_project_counts_by_department_and_status(fy=None):
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    DepartmentX = frappe.qb.DocType("DepartmentX")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        .on(
            ProjectXStatus.name
            == ProjectX.status
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .left_join(DepartmentX)
        .on(DepartmentX.name == ProjectX.department)
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            ProjectX.department,
            # GroupConcat(ProjectXStatus.name).as_("project_status"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(ProjectX.department, ProjectXStatus.name)
    )
    pivot_status_costs = query.run(as_dict=True)
    return get_pivot_data(pivot_status_costs, "project_status", "department", "count")


def get_project_costs_by_department_and_status(fy=None):
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    DepartmentX = frappe.qb.DocType("DepartmentX")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        .on(
            ProjectXStatus.name
            == ProjectX.status
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .left_join(DepartmentX)
        .on(DepartmentX.name == ProjectX.department)
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            ProjectX.department,
            # GroupConcat(ProjectXStatus.name).as_("project_status"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(ProjectX.department, ProjectXStatus.name)
    )
    pivot_status_costs = query.run(as_dict=True)
    return get_pivot_data(
        pivot_status_costs, "project_status", "department", "total_cost"
    )


def get_project_counts_by_subcounties_and_status(fy=None):
    data = _get_sub_county_data(fy=fy)
    return get_pivot_data(data, "project_status", "sub_county", "count")


def get_project_cost_by_subcounties(fy=None):
    data = _get_sub_county_data(fy=fy, ignore_status=True)
    # override count column to contain Projects
    res = []
    total_no = sum([x["count"] for x in data if x])
    total_cost = sum([x["total_cost"] for x in data if x])
    data.append({"sub_county": "Totals", "count": total_no, "total_cost": total_cost})
    # return get_pivot_data(res, "count", "sub_county", "total_cost")
    headers = [
        # {"field": "sub_county", "label": "Sub-County"},
        {"field": "count", "label": "No. Of Projects"},
        {"field": "total_cost", "label": "Total Cost"},
    ]
    return headers, data


def _get_sub_county_data(fy=None, ignore_status=False):
    """Get data disaggregated by sub-county"""
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    ProjectXLocation = frappe.qb.DocType("ProjectX Location Item")
    Admin3 = frappe.qb.DocType("Admin 3")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        # add ProjectX.administrative_level == "Admin 2" as part of the on statement else if you put it
        # in the where clause, it will not work as expected
        .on(
            (ProjectXStatus.name == ProjectX.status)
            & (ProjectX.administrative_level == "Admin 2")
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .left_join(ProjectXLocation)
        .on(ProjectXLocation.parent == ProjectX.name)
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            ProjectX.admin_names.as_("sub_county"),
            GroupConcat(ProjectXLocation.admin).as_("location"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .distinct()
        .groupby(
            ProjectX.admin_names,
            ProjectXStatus.name if not ignore_status else ProjectX.admin_names,
        )
    )
    sub_county_projects = query.run(as_dict=True)

    # Get projects at ward level while getting the sub-county
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        # add ProjectX.administrative_level == "Admin 3" as part of the on statement else if you put it
        # in the where clause, it will not work as expected
        .on(
            (ProjectXStatus.name == ProjectX.status)
            & (ProjectX.administrative_level == "Admin 3")
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .left_join(ProjectXLocation)
        .on(ProjectXLocation.parent == ProjectX.name)
        .inner_join(Admin3)
        .on(Admin3.name == ProjectXLocation.admin)
        .select(
            ProjectX.name.as_("project_id"),
            (ProjectXStatus.name).as_("project_status"),
            # ProjectX.admin_names,
            Admin3.parent_admin.as_("sub_county"),
            GroupConcat(ProjectXLocation.admin).as_("ward"),
            ProjectX.estimated_cost,
        )
        .distinct()
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            # ProjectX.admin_names,
            Admin3.parent_admin.as_("sub_county"),
            GroupConcat(ProjectXLocation.admin).as_("ward"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(
            # ProjectX.admin_names,
            Admin3.parent_admin,
            ProjectXStatus.name if not ignore_status else Admin3.parent_admin,
        )
    )
    ward_projects = query.run(as_dict=True)
    return sub_county_projects + ward_projects


def get_project_counts_by_wards_and_status(fy=None):
    # Get projects at ward level while getting the sub-county
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    ProjectXLocation = frappe.qb.DocType("ProjectX Location Item")
    Admin3 = frappe.qb.DocType("Admin 3")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        # add ProjectX.administrative_level == "Admin 3" as part of the on statement else if you put it
        # in the where clause, it will not work as expected
        .on(
            (ProjectXStatus.name == ProjectX.status)
            & (ProjectX.administrative_level == "Admin 3")
            & (
                ProjectX.financial_year == fy
                if fy
                else ProjectX.financial_year == ProjectX.financial_year
            )
        )
        .left_join(ProjectXLocation)
        .on(ProjectXLocation.parent == ProjectX.name)
        .inner_join(Admin3)
        .on(Admin3.name == ProjectXLocation.admin)
        # .select(
        #     ProjectX.name.as_("project_id"),
        #     (ProjectXStatus.name).as_("project_status"),
        #     # ProjectX.admin_names,
        #     Admin3.parent_admin.as_("sub_county"),
        #     GroupConcat(ProjectXLocation.admin).as_("ward"),
        #     ProjectX.estimated_cost,
        # )
        # .distinct()
        .select(
            Count(ProjectX.name).as_("count"),
            (ProjectXStatus.name).as_("project_status"),
            # ProjectX.admin_names,
            Admin3.parent_admin.as_("sub_county"),
            ProjectXLocation.admin.as_("ward"),
            # GroupConcat(ProjectXLocation.admin).as_("location"),
            Sum(IfNull(ProjectX.estimated_cost, 0)).as_("total_cost"),
        )
        .groupby(ProjectX.admin_names, ProjectXStatus.name)
    )
    ward_projects = query.run(as_dict=True)

    return get_pivot_data(ward_projects, "project_status", "ward", "count")


def get_pivot_data(
    data,
    pivot_column,
    groupby_column,
    value_column,
    row_totals=True,
    col_totals=True,
    row_totals_header="Total",
):
    pivot_data = []
    pivot_headers = sorted(list(set([x[pivot_column] for x in data])))
    if row_totals:
        pivot_headers.append(row_totals_header)
    groupby_rows = sorted(
        list(set([x[groupby_column] for x in data if x[groupby_column]]))
    )
    for grp in groupby_rows:
        sub_rows = [x for x in data if x[groupby_column] == grp]
        row_total = 0  # sum([x[groupby_column] for x in sub_rows]) if row_totals else 0
        pivot_row = {groupby_column: grp, "is_total": False}
        for col in pivot_headers:
            for row in sub_rows:
                if row[pivot_column] == col:
                    pivot_row[col] = row[value_column]

            # If col does not exist in final row, create it
            if col not in pivot_row:
                pivot_row[col] = 0
            # increment total
            row_total += pivot_row[col]

        if row_totals:
            pivot_row[row_totals_header] = row_total
        pivot_data.append(pivot_row)

    # get column-wise totals
    if col_totals:
        grand_total = 0
        total_row = {groupby_column: f"Total", "is_total": True}
        for col in pivot_headers:
            col_vals = [x[col] for x in pivot_data if x[col]]
            total_row[col] = sum(col_vals)
            grand_total += sum(col_vals)

        total_row["total"] = grand_total
        pivot_data.append(total_row)

    return pivot_headers, pivot_data


@frappe.whitelist()
def submit_feedback(feedback):
    vals = frappe.form_dict
    doc = frappe.new_doc("ProjectX Feedback")
    doc.update(
        {
            "subject": vals.subject,
            "attachment": vals.attach_file,
            "project": vals.project,
            "project_name": vals.project_name,
            "is_public": True,
            "email": vals.email,
            "full_name": vals.full_name,
            "phone_number": vals.phone_number,
            "description": vals.feedback,
        }
    )
    doc.insert(ignore_permissions=True)
