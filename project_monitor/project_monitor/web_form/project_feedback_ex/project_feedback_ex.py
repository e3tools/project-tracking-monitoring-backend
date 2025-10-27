import frappe


def get_context(context):
    # do your magic here
    pass


@frappe.whitelist(allow_guest=True)
def get_project_name(project):
    """
    Get Sales order details
    """
    return {"project_name": frappe.db.get_value("ProjectX", project, ["project_name"])}
