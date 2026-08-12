from frappe import _


def get_data():
    return {
        "fieldname": "project",
        # "non_standard_fieldnames": {
        #     "Item": "default_bom",
        # },
        "transactions": [
            {
                "label": _("Structure"),
                "items": [
                    "ProjectX Document",
                    "ProjectX Gallery",
                    "ProjectX Team",
                    "ProjectX PMC",
                ],
            },
            {
                "label": _("Feedback"),
                "items": ["ProjectX Feedback", "ProjectX Feedback Response"],
            },
            # {
            #     "label": _("Implementation"),
            #     "items": ["ProjectX Update"],
            # },
            {
                "label": _("Execution"),
                "items": [
                    "ProjectX Disbursement",
                    "ProjectX Expenditure",
                    "ProjectX Progress Report",
                    "ProjectX Post Evaluation",
                ],
            },
        ],
        "disable_create_buttons": [
            "ProjectX Feedback Response",
            # "Purchase Order",
        ],
    }
