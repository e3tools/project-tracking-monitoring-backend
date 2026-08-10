import frappe
from frappe.utils import getdate


def check_project_health_alerts():
    projects = frappe.get_all(
        "ProjectX",
        filters={"status": ["in", ["In Progress", "Ongoing"]]},
        fields=[
            "name",
            "current_financial_progress",
            "current_physical_progress",
            "expected_end_date",
        ],
    )

    today = frappe.utils.today()
    today = getdate(today)

    for p in projects:
        # Flag physical progress lagging significantly behind financial spend
        if p.current_financial_progress - p.current_physical_progress > 20:
            frappe.db.set_value("ProjectX", p.name, "health_status", "Budget Exceeded")
        elif (
            p.expected_end_date
            and getdate(p.expected_end_date) < today
            and p.current_physical_progress < 100
        ):
            frappe.db.set_value("ProjectX", p.name, "health_status", "Delayed")
