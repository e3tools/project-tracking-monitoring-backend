import frappe
from frappe import _
from project_monitor.www.web_page_enum import WebPageEnum
from frappe.query_builder.functions import Count, Max, Sum, IfNull, Substring
from project_monitor.templates.project_base import get_context as get_base_context


def get_context(context):
    context = get_base_context(context)
    project_id = frappe.form_dict.project
    if not project_id:
        # redirect to search page
        context["labels"] = get_labels()
        return context
    if "is_new" in frappe.form_dict:
        submit_feedback()
        return context

    project = get_project(project_id)
    context["project"] = project

    context["feedback"] = get_feedback(project_id)

    # get project galleries
    context["galleries"] = get_top_level_galleries(project_id)

    # get project gallery items
    context["gallery_items"] = get_gallery_items(project_id)

    context["labels"] = get_labels()
    return context


def get_project(project_id):
    ProjectX = frappe.qb.DocType("ProjectX")
    query = (
        frappe.qb.from_(ProjectX)
        .select(
            ProjectX.expected_start_date,
            ProjectX.status,
            ProjectX.name,
            ProjectX.admin_names,
            ProjectX.project_scope,
            ProjectX.project_name,
            ProjectX.financial_year,
            ProjectX.department,
            ProjectX.implemented_by,
            ProjectX.estimated_cost,
            ProjectX.approval_number,
        )
        .where(ProjectX.name == project_id)
    )
    projects = query.run(as_dict=True)
    return projects[0] if projects else {}


def get_top_level_galleries(project_id):
    # get project galleries
    Gallery = frappe.qb.DocType("ProjectX Gallery")
    query = (
        frappe.qb.from_(Gallery)
        .select(
            Gallery.name,
            Gallery.project,
            Gallery.description,
        )
        .where(Gallery.project == project_id)
        .orderby(Gallery.modified, order=frappe.qb.desc)
    )
    return query.run(as_dict=True)


def get_gallery_items(project_id):
    # get project gallery items
    Gallery = frappe.qb.DocType("ProjectX Gallery")
    GalleryItem = frappe.qb.DocType("ProjectX Gallery Item")
    query = (
        frappe.qb.from_(Gallery)
        .inner_join(GalleryItem)
        .on(Gallery.name == GalleryItem.parent)
        .select(
            Gallery.name,
            Gallery.project,
            Gallery.project_title,
            GalleryItem.short_title,
            GalleryItem.attach_file,
        )
        .where(Gallery.project == project_id)
        .orderby(Gallery.modified, order=frappe.qb.desc)
        # .groupby(Gallery.project)
        # .limit(3)
    )
    return query.run(as_dict=True)


def get_feedback(project_id):
    # Feedback
    Feedback = frappe.qb.DocType("ProjectX Feedback")
    query = (
        frappe.qb.from_(Feedback)
        .select(
            Feedback.name,
            Feedback.subject,
            Feedback.description,
            Feedback.creation,
            Feedback.parent_projectx_feedback,
        )
        .where(Feedback.project == project_id and Feedback.is_public == 1)
    )
    raw_feedback = query.run(as_dict=True)

    feedback = []
    # only allows single level of nesting
    # Get all parents
    parents = [x for x in raw_feedback if not x.parent_projectx_feedback]
    for p in parents:
        p.update(
            {
                "children": [
                    x for x in raw_feedback if x.parent_projectx_feedback == p.name
                ]
            }
        )
        feedback.append(p)
    return feedback


def get_labels():
    labels = {
        "FeedbackTitle": "Feedback",
        "PageTitle": "Project Details",
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
        "FAQ": "Get More",
    }
    return labels


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
