import frappe
from frappe import _
from frappe.apps import get_apps
from frappe.query_builder.functions import Count, Sum


def get_context(context):
    years = frappe.get_all("Financial YearX", order_by="end_date DESC")
    if not years:
        return context

    fiscal_year = years[0]
    all_projects = frappe.get_all("ProjectX")
    # Organize by project status
    statuses = frappe.get_all("ProjectX Status")
    currency = "KES"
    entries = [
        {
            "status": _("All Projects"),
            "count": len(all_projects),
            "budget": frappe.utils.fmt_money(40000000, currency=currency),
        }
    ]
    for status in statuses:
        projects = [x for x in all_projects if x.status == status]
        entry = {
            "status": status.name,
            "count": len(projects),
            "budget": frappe.utils.fmt_money(4000000, currency=currency),
        }
        entries.append(entry)

    context.update({"project_status": entries})

    # organize by wards
    ProjectX = frappe.qb.DocType("ProjectX")
    LocationItem = frappe.qb.DocType("ProjectX Location Item")
    query = (
        (frappe.qb.from_(ProjectX))
        .inner_join(LocationItem)
        .on(ProjectX.name == LocationItem.parent)
        # .select( ProjectX.name, LocationItem.admin_level, LocationItem.admin)
        .select(
            LocationItem.admin, Count(LocationItem.name), Sum(ProjectX.estimated_cost)
        )
        .where(
            LocationItem.admin_level == 3
            and ProjectX.financial_year == fiscal_year.name
        )
        .groupby(LocationItem.admin)
        # .orderby("count", order=frappe.qb.desc)
    )
    # print(query.get_sql())
    # res = frappe.db.sql(query, debug=True)
    projects = query.run(as_dict=True, debug=True)
    context.update({"wards": projects})
    return context
