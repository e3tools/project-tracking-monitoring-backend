import frappe
from frappe import _
from project_monitor.www.web_page_enum import WebPageEnum
from frappe.query_builder.functions import Count, Max, Sum, IfNull, Substring
from project_monitor.templates.project_base import get_context as get_base_context


def get_context(context):
    context = get_base_context(context)
    lang = frappe.form_dict.page or "en"
    WebPageContent = frappe.qb.DocType("ProjectX Web Page Content")
    WebPageContentItem = frappe.qb.DocType("ProjectX Web Page Content Item")
    query = (
        frappe.qb.from_(WebPageContent)
        .inner_join(WebPageContentItem)
        .on(WebPageContent.name == WebPageContentItem.parent)
        .select(
            WebPageContentItem.content_title,
            WebPageContentItem.language,
            WebPageContentItem.content,
        )
        .where(
            WebPageContent.web_page == WebPageEnum.HOMEPAGE.value
            and (
                WebPageContentItem.language == lang
                or WebPageContentItem.language == None
            )
        )
    )
    page_labels = query.run(as_dict=True, debug=True)
    # transform into {content_title: item dict} for ease of access on the frontend
    # content = [{x.content_title: x} for x in content]
    labels = {}
    for x in page_labels:
        labels[x.content_title] = x
    context.update({"content": labels})

    # get latest gallery
    Gallery = frappe.qb.DocType("ProjectX Gallery")
    # Get 8 latest modified projects
    projects = (
        frappe.qb.from_(Gallery)
        .select(Gallery.name, Gallery.project_title)
        .orderby(Gallery.modified, order=frappe.qb.desc)
        .limit(8)
    ).run(as_dict=True)
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
        .where(GalleryItem.parent.isin([x.name for x in projects]))
        .orderby(Gallery.modified, order=frappe.qb.desc)
        # .groupby(Gallery.project)
        # .limit(3)
    )
    gallery = query.run(as_dict=True)
    context["recent_projects"] = projects
    context["gallery"] = gallery

    # project status
    ProjectX = frappe.qb.DocType("ProjectX")
    ProjectXStatus = frappe.qb.DocType("ProjectX Status")
    query = (
        frappe.qb.from_(ProjectXStatus)
        .left_join(ProjectX)
        .on(ProjectXStatus.name == ProjectX.status)
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
    context["status_costs"] = status_costs

    # project status
    query = frappe.qb.from_(ProjectXStatus).select(
        ProjectXStatus.name,
        ProjectXStatus.description,
        ProjectXStatus.theme,
    )
    status = query.run(as_dict=True)
    context["status"] = status

    # project feedback
    ProjectXFeedback = frappe.qb.DocType("ProjectX Feedback")
    query = (
        frappe.qb.from_(ProjectXFeedback)
        .select(
            ProjectXFeedback.subject,
            Substring(ProjectXFeedback.description, 1, 100).as_("description"),
            ProjectXFeedback.creation,
            ProjectXFeedback.project_name,
        )
        .limit(5)
    )
    feedback = query.run(as_dict=True)
    context["feedback"] = feedback
    context["labels"] = {}
    return context


def get_recent_gallery():
    pass


def get_project_count_by_status():
    pass
