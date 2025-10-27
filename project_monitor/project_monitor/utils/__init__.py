import frappe


def projects_by_department(department: str = None):
    department_counts = frappe.get_all(
        "Project Ex",
        fields=[
            "`tabProject Ex`.department",
            "COUNT(`tabProject Ex`.name) as item_count",
        ],
        group_by="`tabProject Ex`.department",
        order_by="item_count DESC",
        debug=True,
    )


# invoice_item_counts = frappe.get_all(
#     "Sales Invoice",
#     fields=[
#         "`tabSales Invoice`.name",
#         "COUNT(`tabSales Invoice Item`.item_code) as item_count"
#     ],
#     group_by="`tabSales Invoice`.name",
#     order_by="item_count DESC",
#     debug=True
# )
